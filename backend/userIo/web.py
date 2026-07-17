from http.client import TEMPORARY_REDIRECT
from time import sleep
from typing import Sequence, TYPE_CHECKING



from .interface import UserIO, IOType
if TYPE_CHECKING:
    from backend.core.roles.PlayerRole import PlayerRole
    from ..core.Player import Player
    from ..core.cards.Card import Card
    from ..core.cards.acquisitions.Acquisition import Acquisition
    from ..core.cards.personnals.Children import ChildCard

from gevent.queue import Queue

TEMPS_ATTENTES = 0.5

class WebIO(UserIO):
    def __init__(self):
        self._queue: Queue = Queue()
        self.pending: dict | None = None

    def choice(self, prompt: str, choices: list) -> "Card | Player | PlayerRole | str":
        """Affiche l'overlay générique de choix (liste de boutons texte,
        pas de cartes). Bloque la greenlet jusqu'à ce que le joueur
        sélectionne une des possibilités. Retourne l'élément choisi
        (et non son index), pour coller à la signature de l'interface.
        """
        sleep(TEMPS_ATTENTES)
        self.pending = {
            "ui_component": IOType.CHOICE.value,
            "prompt": prompt,
            # Le frontend n'a besoin que d'un libellé par choix ; on garde
            # les objets d'origine côté serveur pour retrouver l'élément
            # sélectionné à partir de son index.
            "choices": [str(c) for c in choices],
        }
        index: int = self._queue.get()
        self.pending = None
        return choices[index]

    def reorder_hands(self, players: list["Player"], hands: "list[list[Card]]") -> "list[list[Card]]":
        """Affiche l'overlay de réorganisation des mains (drag and drop entre joueurs).
        Bloque la greenlet jusqu'à ce que le joueur valide la nouvelle répartition.

        Chaque carte envoyée au frontend embarque sa position d'origine
        (`_origin: {player, card}`) afin que le frontend n'ait qu'à renvoyer
        des références plutôt que des cartes sérialisées, et que l'on puisse
        reconstituer les vrais objets `Card` (et non des copies) côté serveur.
        """
        sleep(TEMPS_ATTENTES)
        self.pending = {
            "ui_component": IOType.HAND_REORDER.value,
            "prompt": "Réorganisez les cartes entre les mains des joueurs, puis validez.",
            "players_names": [p.name for p in players],
            "hands": [
                [
                    {**c.to_dict(), "_origin": {"player": p_idx, "card": c_idx}}
                    for c_idx, c in enumerate(hand)
                ]
                for p_idx, hand in enumerate(hands)
            ],
        }
        new_hands_origins: list[list[dict]] = self._queue.get()
        self.pending = None
        print(f"yousk {new_hands_origins}")
        return [
            [hands[origin["player"]][origin["card"]] for origin in new_hand]
            for new_hand in new_hands_origins
        ]

    def ask_cards(self, prompt: str, cards: list["Card"], kind: IOType, nb: int) -> "list[Card]":
        """Demande au joueur de sélectionner jusqu'à nb cartes parmi une liste
        (au moins 1, au maximum nb).
        Bloque la greenlet jusqu'à ce que le joueur valide une sélection.
        """
        sleep(TEMPS_ATTENTES)
        self.pending = {
            "ui_component": kind.value,
            "prompt": prompt,
            "options": [c.to_dict() for c in cards],
            "nb": nb,
        }
        indices: list[int] = self._queue.get()
        self.pending = None
        return [cards[i] for i in indices]

    def _ask(self, prompt: str, options: list, kind: IOType) -> "Card | Player | PlayerRole | None":
        sleep(TEMPS_ATTENTES)
        self.pending = {
            "ui_component": kind.value,
            "prompt": prompt,
            "options": [o.to_dict() for o in options],
        }
        index = self._queue.get()  # bloque la greenlet, libère les autres
        self.pending = None
        return options[index]

    def ask_player(self, prompt: str, players: list["Player"], kind: IOType) -> "Player | None":
        """retourne l'id du joueur selectionnée"""
        return self._ask(prompt, players, kind) # type: ignore

    def ask_card(self, prompt: str, cards: list["Card"], kind: IOType) -> "Card | None":
        """retourne l'id de la carte selectionnée"""
        return self._ask(prompt, cards, kind) # type: ignore

    def ask_role(self, prompt: str, cards: "list[PlayerRole]", kind: IOType) -> "PlayerRole | None":
        return self._ask(prompt, cards, kind) # type: ignore

    def erreur_detiquetage_interface(self, owner: "Player", others: "list[Player]", children_owner: "list[ChildCard]", children_others: "list[list[ChildCard]]") -> "tuple[ChildCard, ChildCard, Player]":
        """effectue l'interface de l'erreur d'étiquetage, retourne 2 carte selectionnee avec le joueur selectionnee"""
        sleep(TEMPS_ATTENTES)
        self.pending = {
            "ui_component": IOType.ERROR_LABELLING.value,
            "prompt": "Sélectionnez une carte à échanger avec la carte d'un autre joueur.",
            "owner_name": owner.name,
            "owner_cards": [c.to_dict() for c in children_owner],
            "others": [
                {"player_name": p.name, "cards": [c.to_dict() for c in cards]}
                for p, cards in zip(others, children_others)
            ],
        }
        # Le frontend envoie via la route générique /submit-indices :
        # [owner_index, other_player_index, other_card_index]
        owner_index, other_player_index, other_card_index = self._queue.get()
        self.pending = None

        owner_card = children_owner[owner_index]
        other_player = others[other_player_index]
        other_card = children_others[other_player_index][other_card_index]
        return owner_card, other_card, other_player


    def ask_troc(self, card: "Card") -> bool:
        """Affiche l'overlay de choix troc/garder pour la carte piochée (effet Eclipse).
        Bloque la greenlet jusqu'à ce que le joueur choisisse.
        Le frontend envoie via /submit : index 0 = troquer, index 1 = garder.
        """
        sleep(TEMPS_ATTENTES)
        self.pending = {
            "ui_component": IOType.TROC_CHOICE.value,
            "prompt": "Une éclipse est en cours : voulez-vous troquer cette carte ?\n"+card.get_card_rule(),
            "card": card.to_dict(),
        }
        index: int = self._queue.get()
        self.pending = None
        return index == 0

    def ask_salaries(self, acquisition: "Acquisition", salaries: Sequence["Card"], cost: int) -> list["Card"]:
        """Affiche l'overlay de sélection de salaires.
        Bloque la greenlet jusqu'à ce que le joueur valide une sélection dont la somme >= cost.
        """
        print(f"APPEL DE ASK SALARIES + longeur de la queue = {len(self._queue)}")
        sleep(TEMPS_ATTENTES)
        self.pending = {
            "ui_component": IOType.SALARY_SELECTOR.value,
            "prompt": f"Payer {acquisition.name if hasattr(acquisition, 'name') else 'acquisition'} ({cost})", # type: ignore
            "cost": cost,
            "cards": [s.to_dict() for s in salaries],
        }
        indices: list[int] = self._queue.get()
        self.pending = None

        print(f"FIN DE ASK SALARIES + longeur de la queue = {len(self._queue)}")
        return [salaries[i] for i in indices]

    def show_cards(self, title: str, prompt: str, cards: Sequence["Card"]) -> None:
        """Affiche l'overlay de consultation de cartes (lecture seule).
        Bloque la greenlet jusqu'à ce que le joueur ferme l'overlay.
        """
        sleep(TEMPS_ATTENTES)
        self.pending = {
            "ui_component": IOType.CARD_BROWSER.value,
            "title":  title,
            "prompt": prompt,
            "cards":  [c.to_dict() for c in cards],
        }
        self._queue.get()   # le frontend envoie None ou 0 à la fermeture
        self.pending = None

    def submit(self, index: int) -> None:
        """Appelé par la route Flask quand l'utilisateur choisit (choix simple)."""
        self._queue.put(index)

    def submit_indices(self, indices: list[int]) -> None:
        """Appelé par la route Flask quand l'utilisateur valide une sélection multiple."""
        print("YOUSKKKKKKKKK")
        self._queue.put(indices)

    def submit_dismiss(self) -> None:
        """Appelé par la route Flask quand l'utilisateur ferme un overlay de consultation."""
        self._queue.put(None)

    def submit_hands(self, hands: "list[list[dict]]") -> None:
        """Appelé par la route Flask quand l'utilisateur valide la réorganisation des mains.
        `hands` : liste (par joueur) de listes de références {"player": int, "card": int}
        vers les positions d'origine des cartes."""
        self._queue.put(hands)

    def show_players_hand(self, players_names: Sequence[str], players_hands: "Sequence[Sequence[Card]]"):
        sleep(TEMPS_ATTENTES)
        self.pending = {
            "ui_component": IOType.SHOW_HAND.value,
            "players_names": players_names,
            "players_hands": [[c.to_dict() for c in hand] for hand in players_hands]
        }
        self._queue.get()   # le frontend envoie None ou 0 à la fermeture
        self.pending = None