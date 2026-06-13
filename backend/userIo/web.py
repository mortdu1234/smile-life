from time import sleep
from typing import Sequence, TYPE_CHECKING

from backend.core.cards.Card import Card

from .interface import UserIO, IOType
if TYPE_CHECKING:
    from ..core.Player import Player
    from ..core.cards.Card import Card
    from ..core.cards.acquisitions.Acquisition import Acquisition

from gevent.queue import Queue


class WebIO(UserIO):
    def __init__(self):
        self._queue: Queue = Queue()
        self.pending: dict | None = None

    def _ask(self, prompt: str, options: list, kind: IOType) -> "Card | Player | None":
        sleep(0.5)
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

    def ask_salaries(self, acquisition: "Acquisition", salaries: Sequence["Card"], cost: int) -> list["Card"]:
        """Affiche l'overlay de sélection de salaires.
        Bloque la greenlet jusqu'à ce que le joueur valide une sélection dont la somme >= cost.
        """
        self.pending = {
            "ui_component": IOType.SALARY_SELECTOR.value,
            "prompt": f"Payer {acquisition.name if hasattr(acquisition, 'name') else 'acquisition'} ({cost})", # type: ignore
            "cost": cost,
            "cards": [s.to_dict() for s in salaries],
        }
        indices: list[int] = self._queue.get()
        self.pending = None
        return [salaries[i] for i in indices]

    def show_cards(self, title: str, prompt: str, cards: Sequence["Card"]) -> None:
        """Affiche l'overlay de consultation de cartes (lecture seule).
        Bloque la greenlet jusqu'à ce que le joueur ferme l'overlay.
        """
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
        self._queue.put(indices)

    def submit_dismiss(self) -> None:
        """Appelé par la route Flask quand l'utilisateur ferme un overlay de consultation."""
        self._queue.put(None)

    def show_players_hand(self, players_names: Sequence[str], players_hands: Sequence[Sequence[Card]]):
        self.pending = {
            "ui_component": IOType.SHOW_HAND.value,
            "players_names": players_names,
            "players_hands": [[c.to_dict() for c in hand] for hand in players_hands]
        }
        self._queue.get()   # le frontend envoie None ou 0 à la fermeture
        self.pending = None