from ...Game import Game
from ...Player import Player
from .JobCard import JobCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...cards.Card import Card
class Astronaute(JobCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path)
        self.study = 6
        self.salary = 4
    def get_name(self) -> str:
        return "Astronaute"
    def get_card_rule(self) -> str:
        return """permet de récupérer une carte posable au choix depuis la défausse au moment ou le joueur pose la carte Astronaute"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()
    
    def _get_available_card(self, current_player: "Player", game: "Game") -> list["Card"]:
        current_player.add_card_to_played(self)
        cards_availables: list["Card"] = []
        for card in game.discard:
            sucess, reason = card.can_be_played(current_player, game)
            if sucess:
                cards_availables.append(card)
        current_player.remove_card(self)
        return cards_availables
        

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        """Recupère une carte depuis la défausse posable et la pose immédiatement"""
        cards_availables = self._get_available_card(current_player, game)
        if len(cards_availables) > 0:
            from ....userIo.interface import IOType
            selected_card: "Card | None" = interface.ask_card(prompt="Recherche dans la défausse : Astronaute", cards=cards_availables, kind=IOType.CARD_PICKER)
            if selected_card:
                game.remove_card_from_discard(selected_card)
                current_player.add_card_to_hand(selected_card)
                selected_card.play_card(game, current_player, interface)
        return super().apply_card_effect(game, current_player, interface)
