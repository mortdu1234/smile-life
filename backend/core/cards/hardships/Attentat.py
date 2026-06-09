from backend.core.Power import Power
from .HardshipCard import Hardship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
    from backend.userIo.interface import UserIO


class Attentat(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:        
        # Vérifie si il y a un joeuur qui empeiche les attentats
        players = game.players
        for game_player in players:
            if Power.NO_ATTENTAT in game_player.get_power():
                return False
        
        return super().can_be_targeted(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        success = super().apply_card_effect(game, current_player, interface)
        if not success:
            return False
        assert self.target_player is not None
        # Action
        from ...PlayerCardGroup import PlayedCardGroup
        from ..personnals.Children import ChildCard
        players = game.players
        for player in players:
            for card in player.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE):
                if isinstance(card, ChildCard):
                    player.remove_card(card)
                    game.add_card_to_discard(card)

        return True

    def get_name(self) -> str:
        return "Attentat"