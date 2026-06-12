"""Contient l'ensemble des données d'une partie en cours"""
from datetime import datetime
from enum import Enum
import functools

from backend.core.JobStatus import JobStatus

from .PlayerCardGroup import PlayedCardGroup
from .Player import Player
from .cards.Card import Card
from ..userIo.botIO import BotIO

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cards.specials.Casino import Casino

class TurnState(Enum):
    PIOCHE = "pioche"
    POSE = "pose"

class GameStateKey(Enum):
    CHANCE = "chance"
    ARC_EN_CIEL = "arc_en_ciel"

HISTORY_SIZE = 5

def validate_player(method):
    @functools.wraps(method)
    def wrapper(self, player_id, *args, **kwargs):
        if self.player_turn != player_id:
            return None, "Ce n'est pas votre tour."
        return method(self, player_id, *args, **kwargs)
    return wrapper

def validate_phase(required_phase: TurnState):
    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.turn_state != required_phase:
                return None, f"Action impossible en phase '{self.turn_state}' (attendu : '{required_phase}')."
            return method(self, *args, **kwargs)
        return wrapper
    return decorator




class Game:
    # PARAMETRES DE BASE DE LA PARTIE
    id: str # Identifiant de la partie (code à 5 lettres)
    players: list[Player] # Liste des joueurs dans la partie
    deck: list[Card] # Cartes restantes dans la pioche
    discard: list[Card] # Cartes dans la défausse
    player_turn: int # Index du joueur dont c'est le tour
    center_cards_played: list[Card] # Cartes jouées au centre de la table
    historique: list[str] # historique de la partie
    turn_state: TurnState # etat du jeu
    game_state: dict[GameStateKey, int]
    updated_at: datetime
    # PARAMETRE SUPPLEMENTAIRE POUR LE JEU

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
        print(self.game_state)
        # Donne les mains des joueurs
        for _ in range(5):
            for player in self.players:
                player.add_card_to_hand(deck.pop())

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
        }
        last_discard = self.get_last_discard()
        if last_discard:
            data["last_discard"] = last_discard.to_dict()
        return data
    

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

    def next_turn(self):
        """Passe au tour du joueur suivant."""
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
                card = self.take_card_from_deck()
                current_player.add_card_to_hand(card)        
        
        print("[INFO] "+"="*60)
        print("[INFO] "+f" FIN du tour du joueur {self.get_current_player().name}")
        print("[INFO] "+"="*60)
        self.player_turn = (self.player_turn + 1) % len(self.players)

        print("[INFO] "+"="*60)
        print("[INFO] "+f" DEBUT du tour du joueur {self.get_current_player().name}")
        print("[INFO] "+"="*60)
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
        """supprime une carte de la défausse"""
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

    
    # ------------------------------------------------------------------ #
    #  Actions du tour - Actions                                         #
    # ------------------------------------------------------------------ #   
    @validate_player
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
        player.add_card_to_hand(card)
        self.turn_state = TurnState.POSE
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
        card.play_card(self, player, player.get_interface())
        self.add_to_history(f"Le joueur {self.get_current_player().name} a joué la carte de la défausse {card.get_name()}")
        self.next_turn()

        return True, ""
        

    @validate_player
    @validate_phase(TurnState.POSE)
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
        self.next_turn()

        return True, ""

    @validate_player
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
                    player.remove_card(card)
                    card.discard_job(player, self)
                    self.add_card_to_discard(card)
                    self.add_to_history(f"Le joueur {self.get_current_player().name} se défausse de son métier : {card.get_name()}")    
                    if card.status != JobStatus.INTERIMERE:
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
                    player.remove_card(card)
                    self.add_card_to_discard(card)
                    self.add_to_history(f"Le joueur {self.get_current_player().name} se défausse de son marriage {card.get_name()}")
                    self.next_turn()

                    return True, ""
                else:
                    return False, reason
            else:
                return False, "[ERROR] la carte n'est pas un marriage"
        else:
            return False, "[ERROR] La carte n'est pas trouvée"

    @validate_player
    @validate_phase(TurnState.PIOCHE)
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
                    player.remove_card(card)
                    self.add_card_to_discard(card)
                    self.add_to_history(f"Le joueur {self.get_current_player().name} se défausse de son adultère {card.get_name()}")
                    self.next_turn()

                    return True, ""
                else:
                    return False, reason
            else:
                return False, "[ERROR] la carte n'est pas un adultère"
        else:
            return False, "[ERROR] La carte n'est pas trouvée"


    @validate_player
    @validate_phase(TurnState.POSE)
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

        card.play_card(self, player, player.get_interface())
        self.add_to_history(f"Le joueur {self.get_current_player().name} a joué la carte {card.get_name()}")
        self.next_turn()

        return True, ""

    
    @validate_player
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
        self.next_turn()
        return True, ""