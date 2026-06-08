from backend.core.Game import Game
from backend.core.Player import Player
from backend.userIo.interface import UserIO

from ..Card import Card
from ....userIo.interface import IOType
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player

class Hardship(Card):
    target_player: Player | None
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path, 0)
        self.target_player = None
    def _selection_cibles(self, game: Game) -> list[Player]:
        """retourne la liste des cibles potentielles"""
        targetted_players: list[Player] = []
        for player in game.players:
            if self.can_be_targeted(player, game):
                targetted_players.append(player)
        return targetted_players

    def can_be_played(self, player: Player, game: Game) -> tuple[bool, str]:
        if len(self._selection_cibles(game)) == 0:
            return False, "aucune cibles possible"
        return super().can_be_played(player, game)

    def select_target(self, game: "Game", interface: "UserIO") -> bool:
        """Selectionne la cible et la met dans self.target_player"""
        print("[DEBUG] TODO")
        targetted_players: list[Player] = self._selection_cibles(game)
        target: Player | None = interface.ask_player("Selection d'une cible", targetted_players, IOType.PLAYER_PICKER)
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

    def play_card(self, game: "Game", current_player: "Player", interface: "UserIO") -> None:
        """Pose la carte : applique l'effet puis déplace la carte dans les posées."""
        if self.apply_card_effect(game, current_player, interface) and self.target_player:
            current_player.remove_card_from_hand(self)
            self.target_player.add_card_to_played(self)
        else:
            print("[ERROR] : il y a une erreur lors du pouvoir")

    def apply_card_effect(self, game: Game, current_player: Player, interface: UserIO) -> bool:
        have_target = self.select_target(game, interface)
        if not have_target:
            return False
        return super().apply_card_effect(game, current_player, interface)
    
