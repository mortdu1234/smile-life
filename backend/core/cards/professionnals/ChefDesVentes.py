from ...Game import Game
from ...Player import Player
from ...Power import Power
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ..Card import Card
class ChefDesVentes(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 3
        self.salary = 3
    def apply_card_effect(self, game: Game, current_player: Player, interface: "UserIO") -> bool:
        """permet de récupérer un salaire posable depuis la défausse"""
        print("[DEBUG] TODO")
        current_player.add_card_to_played(self)
        cards_availables: list["Card"] = []
        for card in game.discard:
            sucess, reason = card.can_be_played(current_player, game)
            from .SalaryCard import SalaryCard
            if sucess and isinstance(card, SalaryCard):
                cards_availables.append(card)
        current_player.remove_card(self)
        if len(cards_availables) > 0:
            from ....userIo.interface import IOType
            selected_card: "Card | None" = interface.ask_card(prompt="Recherche dans la défausse des salaire posable : Chef Des Ventes", cards=cards_availables, kind=IOType.CARD_PICKER)
            print(f"[DEBUG] Carte Selectionnée {selected_card}")
            if selected_card:
                game.remove_card_from_discard(selected_card)
                current_player.add_card_to_hand(selected_card)
                selected_card.play_card(game, current_player, interface)
        return super().apply_card_effect(game, current_player, interface)
    