from .HardshipCard import Hardship
from ...PlayerCardGroup import PlayedCardGroup as groupe
from ...Power import Power
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class ChargeMentale(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        power = player.get_power()
        if Power.CHILDREN_PROTECTED in power:
            return False
        children = 0
        from ..personnals.Children import ChildCard
        for card in player.get_card_from_group(groupe.CHILDREN):
            if isinstance(card, ChildCard) and not card.is_protected:
                children += 1
        return children > 0 and super().can_be_targeted(player, game)

    def hardship_effect(self, game: "Game", target: "Player") -> bool:
        """effectue simplement l'effet de la carte"""
        from ..personnals.Children import ChildCard
        from ....userIo.interface import IOType
        # récupération de la liste des enfants
        list_children = [card for card in target.get_card_from_group(groupe.CHILDREN) if isinstance(card, ChildCard) and not card.is_protected]
        selected_child = target.get_interface().ask_card("Charge Mentale: Choisissez un enfant à défausser", cards=list_children, kind=IOType.CARD_PICKER) # pyright: ignore[reportArgumentType]
        if not selected_child:
            return False
        target.remove_card(selected_child, game)
        game.add_card_to_discard(selected_child)
        return super().hardship_effect(game, target)


    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        assert self.target_player is not None
        self.hardship_effect(game, self.target_player)
        return True

    def get_name(self) -> str:
        return "Charge Mentale"

    def get_card_rule(self) -> str:
        return """Défausse un enfant si la cible possède un métier"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()