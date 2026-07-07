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

    def hardship_effect(self, game: "Game", target: "Player") -> bool:
        """effectue simplement l'effet de la carte"""
        from ...PlayerCardGroup import PlayedCardGroup
        from ..personnals.Children import ChildCard
        players = game.players
        for player in players:
            power = player.get_power()
            if Power.CHILDREN_PROTECTED in power:
                print("[DEBUG] Le joueur {} est protégé de l'attentat".format(player.name))
                continue
            for card in player.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE):
                if isinstance(card, ChildCard):
                    player.remove_card(card, game)
        
        return super().hardship_effect(game, target)


    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        self.target_player = current_player
        # Action
        self.hardship_effect(game, self.target_player)
        
        return True

    def get_name(self) -> str:
        return "Attentat"
    def get_card_rule(self) -> str:
        return """Un Attentat est particulier car il se pose sur le board du joueur qui le pose. Son effet est de tuer tous les enfants du terrain. Attention après avoir fait un attentat, il n'est plus possible d'avoir la légion d'honneur"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()