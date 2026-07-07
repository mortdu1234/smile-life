from backend.core.Game import Game
from backend.core.Player import Player

from .HardshipCard import Hardship
from ...PlayerCardGroup import PlayedCardGroup as groupe
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class Porc(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        if player.get_wedding() is not None:
            print("[DEBUG] tentative de jouer Porc sur un joueur marié, ce qui est interdit")
            return False
        return super().can_be_targeted(player, game)

    def hardship_effect(self, game: Game, target: Player) -> bool:
        for _ in range(3):
            flirt_card = target.get_last_flirt()
            if flirt_card:
                target.remove_card(flirt_card, game)
                game.add_card_to_discard(flirt_card)
        return super().hardship_effect(game, target)
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        assert self.target_player is not None, "aucunes cibles selectionnées"
        self.hardship_effect(game, self.target_player)
        return True

    def get_name(self) -> str:
        return "Porc"

    def get_card_rule(self) -> str:
        return """la cible défausse les 3 dernières cartes flirts posées. La cible ne dois pas etre mariée afin de pouvoir etre une cible."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()