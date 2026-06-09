from .SpecialCard import SpecialCard
from ....userIo.interface import IOType
from typing import TYPE_CHECKING
import random
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
class Troc(SpecialCard):    
    target_player: "Player | None"
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path, 0)
        self.target_player = None

    def _selection_cibles(self, game: "Game") -> "list[Player]":
        """retourne la liste des cibles potentielles"""
        targetted_players: list[Player] = []
        for player in game.players:
            if self.can_be_targeted(player, game):
                targetted_players.append(player)
        return targetted_players

    def select_target(self, game: "Game", interface: "UserIO") -> bool:
        """Selectionne la cible et la met dans self.target_player"""
        print("[DEBUG] TODO")
        targetted_players: "list[Player]" = self._selection_cibles(game)
        target: "Player | None" = interface.ask_player("Selection d'une cible", targetted_players, IOType.PLAYER_PICKER)
        if not target:
            print("[ERROR] aucune cible n'a été choisie")
            return False
        else:
            print("[DEBUG] selection de la cible avec succès")
            self.target_player = target
            return True

    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        """retourne si le player est une cible potentielle"""
        if player == game.get_current_player():
            return False
        return True
    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        targets = self._selection_cibles(game)
        if len(targets) == 0:
            return False, "Il n'y a pas de cible possible"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        print("[DEBUG] TODO")
        have_target = self.select_target(game, interface)
        if not have_target or not self.target_player:
            return False
        current_hand = current_player.get_hand()
        other_hand = self.target_player.get_hand()
        current_hand.remove(self)
        # selection des cartes selectionnées
        current_choose = random.choice(current_hand)
        other_choose = random.choice(other_hand)
        print(f"[INFO] selection de la carte {current_choose.id}/{current_choose.__class__} pour {current_player.name}")
        print(f"[INFO] selection de la carte {other_choose.id}/{other_choose.__class__} pour {self.target_player.name}")
        current_hand.append(self)
        # supprimer les cartes des mains
        current_player.remove_card_from_hand(current_choose)
        self.target_player.remove_card_from_hand(other_choose)

        # ajouter les cartes dans les autres mains
        current_player.add_card_to_hand(other_choose)
        self.target_player.add_card_to_hand(current_choose)


        return super().apply_card_effect(game, current_player, interface)

    def get_name(self) -> str:
        return "Troc"