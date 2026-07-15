"""
Game
====
Représente l'état complet d'une partie en cours : joueurs, pioche, défausse,
cartes au centre de la table, historique, et machine à états du tour en cours.

Le déroulement normal d'un tour est : PIOCHE -> POSE -> (tour suivant).
Certains effets (Ephemerides, pouvoirs) peuvent modifier ce déroulement :
- Power.AVEUGLEMENT inverse l'ordre du tour du joueur qui le possède : il POSE une
  carte avant de PIOCHER (voir la section "Gestion des tours" plus bas).
"""
from datetime import datetime
from enum import Enum
import functools

from backend.core.JobStatus import JobStatus
from .cards.ephemerides.Ephemeride import Ephemeride

from .PlayerCardGroup import PlayedCardGroup
from .Player import Player
from .cards.Card import Card
from ..userIo.botIO import BotIO
from .Power import Power

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cards.specials.Casino import Casino


class TurnState(Enum):
    """Phase courante du tour du joueur actif."""
    PIOCHE = "pioche"              # le joueur doit piocher (ou poser s'il a Power.AVEUGLEMENT)
    POSE = "pose"                  # le joueur doit poser/défausser (ou piocher s'il a Power.AVEUGLEMENT)
    IN_DISCARDING = "in_discarding"  # défausses multiples en cours (ex: Lune Rouge)
    IN_PLACING = "in_placing"        # poses multiples en cours (ex: Pleine Lune)


class GameModes(Enum):
    CLASSIC = "classic"
    RIVER = "river"


class GameStateKey(Enum):
    CHANCE = "chance"
    ARC_EN_CIEL = "arc_en_ciel"
    NB_CARDS_DISCARD = "nb_cards_discard"
    NB_CARDS_PLACED = "nb_cards_placed"


HISTORY_SIZE = 5
NB_CARD_RIVER = 3


def validate_player(method):
    """Décorateur : bloque l'appel si ce n'est pas le tour du joueur ciblé."""
    @functools.wraps(method)
    def wrapper(self, player_id, *args, **kwargs):
        if self.player_turn != player_id:
            return None, "Ce n'est pas votre tour."
        return method(self, player_id, *args, **kwargs)
    return wrapper


def validate_phase(*required_phases: TurnState):
    """Décorateur : bloque l'appel si la partie n'est pas dans une des phases attendues."""
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.turn_state not in required_phases:
                phases_str = ", ".join(str(p) for p in required_phases)
                return None, f"Action impossible en phase '{self.turn_state}' (attendu : '{phases_str}')."
            return method(self, *args, **kwargs)
        return wrapper
    return decorator



class Game:
    """Etat complet d'une partie et logique associée (tours, pioche, actions des joueurs)."""

    # --- Attributs de base de la partie ---
    id: str                                # Identifiant de la partie (code à 5 lettres)
    players: list[Player]                  # Liste des joueurs dans la partie
    deck: list[Card]                       # Cartes restantes dans la pioche
    discard: list[Card]                    # Cartes dans la défausse
    cards_removed: list[Card]              # Cartes supprimées par violence
    player_turn: int                       # Index du joueur dont c'est le tour
    center_cards_played: list[Card]        # Cartes jouées au centre de la table
    historique: list[str]                  # Historique de la partie
    turn_state: TurnState                  # Phase courante du tour
    game_state: dict[GameStateKey, int]    # Compteurs d'effets en cours (chance, arc-en-ciel, ...)
    game_mode: GameModes
    river_deck: list[Card]
    updated_at: datetime
    ephemeride: Ephemeride | None

    def __init__(self, id: str, players: list[Player], deck: list[Card]):
        self.id = id
        self.players = players
        self.deck = deck
        self.discard = []
        self.player_turn = 0
        self.center_cards_played = []
        self.historique = []
        self.turn_state = TurnState.PIOCHE
        self.game_state = {key:0 for key in GameStateKey}
        self.game_mode = GameModes.CLASSIC
        self.river_deck = []
        self.cards_removed = []
        self.ephemeride = None
        # Donne les mains des joueurs
        for _ in range(5):
            for player in self.players:
                result = False
                while not result:
                    card = deck.pop()
                    result = player.add_card_to_hand(card)
                    if not result:
                        player.remove_card_from_hand(card)
                        deck.insert(len(deck)//2, card)

        # testing map
        from .cards.LoaderCard import build_card
        for player in self.players:
            player.add_card_to_played(build_card("salary__1"))
            player.add_card_to_played(build_card("salary__1"))
            player.add_card_to_played(build_card("salary__1"))
            player.add_card_to_played(build_card("salary__4"))
            player.add_card_to_played(build_card("salary__4"))
            player.add_card_to_played(build_card("salary__4"))
            player.add_card_to_played(build_card("study__2"))
            player.add_card_to_played(build_card("study__2"))
            player.add_card_to_played(build_card("study__2"))

    def add_card_to_cards_remove(self, card: "Card"):
        """ajoute une carte au carte supprimées"""
        self.cards_removed.append(card)
    def get_removed_cards(self) -> "list[Card]":
        return self.cards_removed
    def remove_cards_from_removed_cards(self, card: "Card"):
        """retire une carte des cartes retirées"""
        self.cards_removed.remove(card)

    def add_to_history(self, message: str):
        """ajoute un element a l'historique"""
        self.historique.append(message)
        if len(self.historique) > HISTORY_SIZE:
            self.historique.pop(0)

    def to_dict(self, viewer: str | None = None) -> dict:
        """Sérialise l'état de la partie en un dictionnaire pour l'envoyer au client."""
        data = {
            'id': self.id,
            "players": [p.to_dict(reveal_hand=(p.name == viewer)) for p in self.players],
            'deck_count': len([c.to_dict() for c in self.deck]),
            'discard_count': [c.to_dict() for c in self.discard],
            'current_player': self.get_current_player().to_dict(),
            'center_cards_played': [c.to_dict() for c in self.center_cards_played],
            'history': self.historique,
            'game_state': {key.value: val for key, val in self.game_state.items()},
            'game_mode': self.game_mode.value,
            'river_deck': [c.to_dict() for c in self.river_deck],
            'turn_state': self.turn_state.value,
        }
        last_discard = self.get_last_discard()
        if last_discard:
            data["last_discard"] = last_discard.to_dict()
        return data

    def change_game_mode(self, new: GameModes):
        """change le mode de jeu vers le mode riviere"""
        if new == GameModes.RIVER:
            for _ in range(NB_CARD_RIVER):
                self.river_deck.append(self._draw_card_from_deck())
            self.game_mode = new
        else:
            print("change mode to classic")
            for card in self.river_deck:
                self.add_card_to_discard(card)
            self.river_deck = []
            print(self.river_deck)


    def take_card_from_deck_to_player_hand(self, current_player: Player):
        result = False
        while not result:
            card = self.take_card_from_deck()
            assert card is not None, "La pioche est vide"
            result = current_player.add_card_to_hand(card)
            if not result:
                self.add_to_history(f"Le joueur {self.get_current_player().name} a pioché l'ephemeride {card.get_name()}")
                card.play_card(self, current_player)



    def get_last_discard(self) -> Card | None:
        """Retourne la dernière carte de la défausse, ou None si la défausse est vide."""
        return self.discard[-1] if self.discard else None

    def get_current_player(self) -> Player:
        """Retourne le joueur dont c'est le tour."""
        return self.players[self.player_turn]

    def add_card_to_center(self, card: Card):
        """ajoute une carte au centre de la table"""
        self.center_cards_played.append(card)

    def get_casino(self) -> "Casino | None":
        from .cards.specials.Casino import Casino
        for card in self.center_cards_played:
            if isinstance(card, Casino):
                return card
        return None 
    def end_game(self):
        pass

    # ------------------------------------------------------------------ #
    #  Gestion des tours                                                  #
    # ------------------------------------------------------------------ #
    def _has_power_aveuglement(self, player: Player) -> bool:
        """Indique si `player` possède Power.AVEUGLEMENT (tour inversé : pose avant pioche)."""
        return Power.AVEUGLEMENT in player.get_power()

    def _advance_after_draw(self, player: Player):
        """A appeler juste après qu'un joueur a pioché sa carte.

        - Flux normal : la pioche est la 1ère étape du tour, on passe donc en phase POSE.
        - Flux inversé (Power.AVEUGLEMENT) : la pioche est la dernière étape du tour, on termine
          donc le tour du joueur.
        """
        if self._has_power_aveuglement(player):
            self.next_turn()
        else:
            self.turn_state = TurnState.POSE

    def _advance_after_place(self, player: Player):
        """A appeler juste après qu'un joueur a posé/défaussé sa carte.

        - Flux normal : la pose est la dernière étape du tour, on termine donc le tour.
        - Flux inversé (Power.AVEUGLEMENT) : la pose est la 1ère étape du tour, le joueur doit
          maintenant piocher.
        """
        if self._has_power_aveuglement(player):
            self.turn_state = TurnState.PIOCHE
        else:
            self.next_turn()

    def next_turn(self):
        """Termine le tour du joueur courant et passe au tour du joueur suivant."""
        value = self.game_state.get(GameStateKey.CHANCE, 0)
        if value > 0:
            print(f"[INFO] le joueur ({self.get_current_player().name}) possède la chance et rejoue")
            self.game_state[GameStateKey.CHANCE] = value - 1        
            self.turn_state = TurnState.POSE
            return

        value = self.game_state.get(GameStateKey.ARC_EN_CIEL, 0)
        if value > 1:
            print(f"[INFO] le joueur ({self.get_current_player().name}) possède l'effet arc_en_ciel et l'utilise")
            self.game_state[GameStateKey.ARC_EN_CIEL] = value - 1        
            self.turn_state = TurnState.POSE
            return
        if value == 1:
            print(f"[INFO] le joueur ({self.get_current_player().name}) fini l'arc en ciel et repioche", end=" ")
            current_player = self.get_current_player()
            nb_cards_to_add = current_player.get_max_hand_card() - len(current_player.get_hand())
            print(f"{nb_cards_to_add} cartes.")
            for _ in range(nb_cards_to_add):
                self.take_card_from_deck_to_player_hand(current_player)


        value = self.game_state.get(GameStateKey.NB_CARDS_DISCARD, 0) 
        if value > 0:
            print(f"[INFO] le joueur ({self.get_current_player().name}) a défausser {value} cartes, donc il repioche")
            for _ in range(value-1):
                current_player = self.get_current_player()
                self.take_card_from_deck_to_player_hand(current_player)
            self.game_state[GameStateKey.NB_CARDS_DISCARD] = 0

        value = self.game_state.get(GameStateKey.NB_CARDS_PLACED, 0) 
        if value > 0:
            print(f"[INFO] le joueur ({self.get_current_player().name}) a posé {value} cartes, donc il repioche")
            for _ in range(value-1):
                current_player = self.get_current_player()
                self.take_card_from_deck_to_player_hand(current_player)
            self.game_state[GameStateKey.NB_CARDS_PLACED] = 0
                                
        print("[INFO] "+"="*60)
        print("[INFO] "+f" FIN du tour du joueur {self.get_current_player().name}")
        print("[INFO] "+"="*60)
        print("[DEBUG] "+f"info du joueur qui viens de finir son tour \n\tpower:{self.get_current_player().get_power()}")
        self.player_turn = (self.player_turn + 1) % len(self.players)

        print("[INFO] "+"="*60)
        print("[INFO] "+f" DEBUT du tour du joueur {self.get_current_player().name}")
        print("[INFO] "+"="*60)
        print("[DEBUG] "+f"info du joueur qui viens de commencer son tour \n\tpower:{self.get_current_player().get_power()}")

        new_current_player = self.get_current_player()
        if self._has_power_aveuglement(new_current_player):
            print(f"[INFO] le joueur ({new_current_player.name}) possède Power.AVEUGLEMENT : son tour est inversé (pose avant pioche)")
            self.turn_state = TurnState.POSE
        else:
            self.turn_state = TurnState.PIOCHE


    def _draw_card_from_deck(self) -> "Card":
        """retourne la prochaine carte du deck SANS FAIRE DE TEST DE SECURITEE"""
        return self.deck.pop()

    def get_card_from_discard_by_id(self, card_id: int) -> "Card | None":
        """retourne une carte de la défausse a partir de son ID"""
        for card in self.discard:
            if card.get_id() == card_id:
                return card
        return None

    def remove_card_from_discard(self, card: "Card") -> int:
        """supprime une carte de la défausse et renvois l'indice"""
        indice = self.discard.index(card)
        self.discard.remove(card)
        return indice
    

    def add_card_to_discard(self, card: "Card", indice:int|None=None):
        """ajoute une carte a la défausse"""
        if not indice:
            self.discard.append(card)
            return
        self.discard.insert(indice+1, card)
        return
    
    def take_card_from_discard(self) -> "Card|None":
        if len(self.discard) == 0:
            return None
        return self.discard.pop()

    def take_card_from_deck(self) -> "Card|None":
        """prend une carte du deck"""
        if len(self.deck) == 0:
            return None
        return self.deck.pop()

    def get_ephemeride(self) -> "Ephemeride | None":
        """retourne la carte ephemeride qui est en cour"""
        from .cards.ephemerides.Ephemeride import Ephemeride
        for card in self.center_cards_played:
            if isinstance(card, Ephemeride):
                return card
        return None

    def set_ephemeride(self, new: "Ephemeride"):
        card = self.get_ephemeride()
        if card:
            self.center_cards_played.remove(card)
        self.center_cards_played.append(new)

    # ------------------------------------------------------------------ #
    #  Actions du tour - Actions                                         #
    # ------------------------------------------------------------------ #   
    @validate_player
    @validate_phase(TurnState.POSE)
    def stop_arc_en_ciel(self, player_id: int) -> tuple[bool, str]:
        """Permet d'arreter un Arc En Ciel en cour"""
        print("[INFO] action du joueur : stop arc en ciel")
        if self.game_state.get(GameStateKey.ARC_EN_CIEL, 0) <= 1:
            return False, "Il n'y a pas d'arc en ciel en cour"
        self.game_state[GameStateKey.ARC_EN_CIEL] = 1
        self.add_to_history(f"Le joueur {self.get_current_player().name} arrete son arc en ciel")
        self.next_turn()
        return True, ""
         
    @validate_player
    @validate_phase(TurnState.PIOCHE)
    def skip_turn(self, player_id: int) -> tuple[bool, str]:
        """Le joueur courrant passe son tour
        pre: uniquement si le joueur courrant a des tours a passer
        """
        print("[INFO] action du joueur : passer un tour")
        player = self.get_current_player()
        if player.skip_turn <= 0:
            print("[ERROR] skip un tour alors que le joueur n'as pas de tours a skip")
            return False, ""
        
        player.skip_turn -= 1
        self.add_to_history(f"Le joueur {self.get_current_player().name} passe son tour")
        self.next_turn()

        return True, ""

    @validate_player
    @validate_phase(TurnState.PIOCHE)
    def draw_card_from_deck(self, player_id: int) -> tuple[bool, str]:
        """pioche une carte depuis la pioche"""
        print("[INFO] action du joueur : piocher une carte")
        player = self.get_current_player()
        if player.skip_turn > 0:
            print("[ERROR] essaye de piocher alors que je joueurs dois skip un tour")
            return False, ""

        if not self.deck:
            print("[ERROR] pioche vide")
            return False, ""
        card: Card = self._draw_card_from_deck()
        if isinstance(card, Ephemeride):
            player.add_card_to_hand(card)
            self.add_to_history(f"Le joueur {self.get_current_player().name} a pioché l'ephemeride {card.get_name()}")
            card.play_card(self, player)
            self.next_turn()
            return True, ""

        ephemeride = self.get_ephemeride()
        if ephemeride:
            from .cards.ephemerides.Equinoxe import Equinoxe
            if isinstance(ephemeride, Equinoxe):
                # demander a l'utilisateur de garder la carte ou de la troquer troc=True (effectuer un troc)
                troc = player.get_interface().ask_troc(card)
                if troc:
                    card = ephemeride.troc_cards(self, player, card)
        
        player.add_card_to_hand(card)
        self._advance_after_draw(player)
        return True, ""


    @validate_player
    @validate_phase(TurnState.PIOCHE)
    def draw_card_from_river(self, player_id: int, card_id: int) -> tuple[bool, str]:
        """pioche une carte depuis la rivière"""
        print("[INFO] action du joueur : piocher une carte depuis la riviere")
        player = self.get_current_player()
        if player.skip_turn > 0:
            print("[ERROR] essaye de piocher alors que je joueurs dois skip un tour")
            return False, ""

        if not self.game_mode == GameModes.RIVER:
            print("[ERROR] le mode de jeu n'est pas river")
            return False, "Le jeux n'est pas en mode rivière"

        # recherche de la carte dans la riviere
        card = None
        for i in range(len(self.river_deck)):
            card = self.river_deck[i]
            if card.get_id() == card_id:
                # changer la carte de la rivière
                self.river_deck[i] = self._draw_card_from_deck()
                break
        if not card:
            print("[ERROR] la carte n'est pas trouvée dans la rivière")
            return False, "La carte n'est pas trouvée dans la rivière"
                
        player.add_card_to_hand(card)
        if isinstance(card, Ephemeride):
            self.add_to_history(f"Le joueur {self.get_current_player().name} a pioché l'ephemeride {card.get_name()}")
            card.play_card(self, player)
            self.next_turn()
            return True, ""

        self._advance_after_draw(player)
        return True, ""


    @validate_player
    @validate_phase(TurnState.PIOCHE)
    def draw_card_from_discard(self, player_id: int) -> tuple[bool, str]:
        """pioche une carte depuis la défausse"""
        print("[INFO] action du joueur : poser la carte de la défausse")
        player = self.get_current_player()
        if player.skip_turn > 0:
            print("[ERROR] essaye de piocher alors que je joueurs dois skip un tour")
            return False, ""

        if not self.deck:
            print("[ERROR] défausse vide")
            return False, ""

        card = self.get_last_discard()
        if not card:
            return False, "[ERROR] Défausse vide"
        
        success, reason = card.can_be_played(player, self)
        if not success:
            return False, reason
        print("[DEUBG] gestion de la pose de la carte")
        card = self.take_card_from_discard()
        if not card:
            return False, "pas de carte dans la défausse"
        player.add_card_to_hand(card)
        self.turn_state = TurnState.POSE
        card.play_card(self, player)
        self.add_to_history(f"Le joueur {self.get_current_player().name} a joué la carte de la défausse {card.get_name()}")
        self.next_turn()

        return True, ""
        

    @validate_player
    @validate_phase(TurnState.POSE, TurnState.IN_DISCARDING)
    def discard_card_from_hand(self, player_id: int, card_id: int) -> tuple[bool, str]:
        """se défausse d'une carte en main vers la défausse"""
        print("[INFO] action du joueur : défausser une carte de la main")
        player = self.get_current_player()
        card = player.get_card_by_id_from_hand(card_id)
        if not card:
            print("[ERROR] La carte n'est pas trouvée")
            return False, ""
        player.remove_card_from_hand(card)
        self.discard.append(card)
        self.add_to_history(f"Le joueur {self.get_current_player().name} a défaussé {card.get_name()}")

        ephemeride = self.get_ephemeride()
        if ephemeride:
            from .cards.ephemerides.LuneRouge import LuneRouge
            if isinstance(ephemeride, LuneRouge):
                self.turn_state = TurnState.IN_DISCARDING
                self.game_state[GameStateKey.NB_CARDS_DISCARD] += 1
                return True, ""

        self._advance_after_place(player)

        return True, ""

    @validate_player
    @validate_phase(TurnState.POSE, TurnState.PIOCHE)
    def discard_job_card(self, player_id: int, card_id: int) -> tuple[bool, str]:
        """démissionne volontairement d'un métier"""
        print("[INFO] action du joueur : démissionner de son métier")
        player = self.get_current_player()
        card = player.find_card_by_id(card_id)
        if card:
            from .cards.professionnals.JobCard import JobCard
            if isinstance(card, JobCard):
                success, reason = card.can_be_discard(player, self)
                if not success:
                    return False, reason
                else:
                    player.remove_card(card, self)
                    self.add_card_to_discard(card)
                    self.add_to_history(f"Le joueur {self.get_current_player().name} se défausse de son métier : {card.get_name()}")    
                    if Power.INSTANT_QUIT_JOB in player.get_power():
                        return True, ""
                    self.next_turn()
                    
                    return True, ""
            else:
                return False, "[ERROR] la carte n'est pas un métier"
        else:
            print("[ERROR] La carte n'est pas trouvée")
            return False, "[ERROR] La carte n'est pas trouvée"


    @validate_player
    @validate_phase(TurnState.PIOCHE)
    def discard_wedding_card(self, player_id: int, card_id: int) -> tuple[bool, str]:
        """supprime son marriage volontairement"""
        print("[INFO] action du joueur : divorcer de son marriage")
        player = self.get_current_player()
        card = player.find_card_by_id(card_id)
        if card:
            from .cards.personnals.Wedding import Wedding
            if isinstance(card, Wedding):
                success, reason = card.can_be_discard(player, self)
                if success:
                    player.remove_card(card, self)
                    self.add_card_to_discard(card)
                    self.add_to_history(f"Le joueur {self.get_current_player().name} se défausse de son marriage {card.get_name()}")
                    if Power.INSTANT_QUIT_WEDDING in player.get_power():
                        return True, ""
                    self.next_turn()
                    return True, ""
                else:
                    return False, reason
            else:
                return False, "[ERROR] la carte n'est pas un marriage"
        else:
            return False, "[ERROR] La carte n'est pas trouvée"

    @validate_player
    @validate_phase(TurnState.POSE, TurnState.PIOCHE)
    def discard_adultery_card(self, player_id: int, card_id: int) -> tuple[bool, str]:
        """supprime son adultaire volontairement"""
        print("[INFO] action du joueur : défausser son adultère")
        player = self.get_current_player()
        card = player.find_card_by_id(card_id)
        if card:
            from .cards.personnals.Wedding import Adultery
            if isinstance(card, Adultery):
                success, reason = card.can_be_discard(player, self)
                if success:
                    player.remove_card(card, self)
                    self.add_card_to_discard(card)
                    self.add_to_history(f"Le joueur {self.get_current_player().name} se défausse de son adultère {card.get_name()}")

                    return True, ""
                else:
                    return False, reason
            else:
                return False, "[ERROR] la carte n'est pas un adultère"
        else:
            return False, "[ERROR] La carte n'est pas trouvée"


    @validate_player
    @validate_phase(TurnState.POSE, TurnState.IN_PLACING)
    def place_card(self, player_id: int, card_id: int) -> tuple[bool, str]:
        """pose une carte devant lui"""
        player = self.get_current_player()
        card = player.get_card_by_id_from_hand(card_id)
        if not card:
            print("[ERROR] la carte n'est pas trouvée")
            return False, ""
        print(f"[INFO] action du joueur : poser la carte {card.get_name()}")
        success, reason = card.can_be_played(player, self)
        if not success:
            return False, reason

        card.play_card(self, player)
        self.add_to_history(f"Le joueur {self.get_current_player().name} a joué la carte {card.get_name()}")

        ephemeride = self.get_ephemeride()
        if ephemeride:
            from .cards.ephemerides.PleineLune import PleineLune
            if isinstance(ephemeride, PleineLune):
                self.turn_state = TurnState.IN_PLACING
                self.game_state[GameStateKey.NB_CARDS_PLACED] += 1
                return True, ""

        self._advance_after_place(player)

        return True, ""

    @validate_player
    @validate_phase(TurnState.IN_DISCARDING, TurnState.IN_PLACING)
    def finish_turn(self, player_id: int) -> tuple[bool, str]:
        """Termine une séquence de poses/défausses multiples (ex: Pleine Lune, Lune Rouge).

        Si le joueur possède Power.AVEUGLEMENT et sort d'une séquence de poses (IN_PLACING),
        son tour est inversé : il doit encore piocher avant que le tour ne se termine.
        """
        player = self.get_current_player()
        if self.turn_state == TurnState.IN_PLACING and self._has_power_aveuglement(player):
            self.turn_state = TurnState.PIOCHE
        else:
            self.next_turn()
        return True, ""

        
    @validate_player
    @validate_phase(TurnState.POSE, TurnState.IN_PLACING)
    def bet_on_casino(self, player_id: int, card_id: int) -> tuple[bool, str]:
        """pose une carte devant lui"""
        print("[INFO] action du joueur : miser au casino une carte")
        from .cards.professionnals.SalaryCard import SalaryCard
        player = self.get_current_player()

        # vérifie le l'état du tour
        card = player.get_card_by_id_from_hand(card_id)
        if not(card and self.turn_state == TurnState.POSE and isinstance(card, SalaryCard)):
            card = self.get_last_discard()
            if not(card and self.turn_state == TurnState.PIOCHE and isinstance(card, SalaryCard)):
                print("[ERROR] La phase de jeu n'est pas la bonne")
                return False, "[ERROR] La phase de jeu n'est pas la bonne"
                
        casinoCard = self.get_casino()
        if not casinoCard:
            return False, "Le casino n'est pas ouvert"
        success, reason = casinoCard.can_bet(player, self)
        if not success:
            return False, reason
        casinoCard.bet(card, player)
        self.add_to_history(f"Le joueur {self.get_current_player().name} a misé au casino un salaire")

        ephemeride = self.get_ephemeride()
        if ephemeride:
            from .cards.ephemerides.PleineLune import PleineLune
            if isinstance(ephemeride, PleineLune):
                self.turn_state = TurnState.IN_PLACING
                self.game_state[GameStateKey.NB_CARDS_PLACED] += 1
                return True, ""

        self._advance_after_place(player)
        return True, ""