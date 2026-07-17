from backend.core.Power import Power
from backend.core.Game import Game
from backend.core.Player import Player
from backend.core.cards.hardships.HardshipCard import Hardship


class MaleficeCard(Hardship):
    def apply_malefice_effect(self, player: "Player", game: "Game") -> bool:        
        assert self.target_player is not None, "Aucun joueur selectionnée"
        powers = self.target_player.get_power()
        if Power.NO_MALEFICES_EFFECT in powers:
            return False
        return True
    
    def can_be_played(self, player: Player, game: Game) -> tuple[bool, str]:
        return super().can_be_played(player, game)
    
    def get_card_rule(self) -> str:
        return """applique un effet (souvent permanent) a un adversaire"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()