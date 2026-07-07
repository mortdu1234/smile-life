from .HardshipCard import Hardship
from ...PlayerCardGroup import PlayedCardGroup as groupe
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class TachesMenagere(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        return super().can_be_targeted(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        assert self.target_player is not None
        from ..acquisitions.HouseAcquisition import House
        played = self.target_player.get_card_from_group(groupe.ACQUISITIONS)
        smiles = 0
        for card in played:
            if isinstance(card, House):
                smiles += card.get_smiles(self.target_player)
        self.target_player.add_skip_turn(smiles)
        print("[DEBUG] taches ménagère : ", smiles, " tours à skip")
        return True

    def get_name(self) -> str:
        return "Tâches Ménagères"

    def get_card_rule(self) -> str:
        return """passer un tour par smile sur les maisons posés devant la cible"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()