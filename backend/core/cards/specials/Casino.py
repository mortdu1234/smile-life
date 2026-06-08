from backend.core.Game import Game
from backend.core.Player import Player
from backend.userIo.interface import UserIO

from .SpecialCard import SpecialCard
from ....userIo.interface import IOType
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..professionnals.SalaryCard import SalaryCard
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ..Card import Card
    from ...Player import Player
class Casino(SpecialCard):
    first_bet : "SalaryCard | None"
    first_player : "Player | None"
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path, 0)
        self.first_bet = None
        self.first_player = None

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["first_bet"] = self.first_bet.to_dict() if self.first_bet else None 
        data["first_player"] = self.first_player.name if self.first_player else None
        return data

    def _check_victory(self, card: "SalaryCard", player: "Player"):
        assert self.first_bet, "[ERROR] Le premier vote n'est pas present"
        assert self.first_player, "[ERROR] Le premier vote n'est pas present"
        if card.get_value() == self.first_bet.get_value():
            player.add_card_to_played(card)
            player.add_card_to_played(self.first_bet)
        else:
            self.first_player.add_card_to_played(card)
            self.first_player.add_card_to_played(self.first_bet)
        self.first_bet = None
        self.first_player = None

    def bet(self,card: "SalaryCard", player: "Player"):
        if not self.first_bet:
            self.first_bet = card
            self.first_player = player
            player.remove_card_from_hand(card)
        else:
            player.remove_card_from_hand(card)
            self._check_victory(card, player)

    def card_bet_available(self, player: "Player") -> "list[Card]":
        from ..professionnals.SalaryCard import SalaryCard
        cards = []
        for card in player.get_hand():
            if isinstance(card, SalaryCard):
                cards.append(card)
        return cards
    
    def can_bet(self, player: "Player", game: "Game") -> tuple[bool, str]:
        cards_available = self.card_bet_available(player)
        if len(cards_available) == 0:
            return False, "Tu n'as pas d'argent a miser"
        if self.first_player and self.first_player == player:
            return False, "Tu as déja miser ton argent au casino"
        return True, ""

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        print("[DEBUG] TODO")

        from ..professionnals.SalaryCard import SalaryCard
        success, reason = self.can_bet(current_player, game)
        if success:
            cards_available = self.card_bet_available(current_player)
            interface = current_player.get_interface()
            card: "Card | None" = interface.ask_card(prompt=f"Selection de la mise au casino", cards=cards_available, kind=IOType.CARD_PICKER)
            if not card or not isinstance(card, SalaryCard):
                print("[ERROR] aucune carte n'as été selectionnées")
                return False
            self.bet(card, current_player)
        game.add_card_to_center(self)
        return True

    def play_card(self, game: Game, current_player: Player, interface: UserIO) -> None:
        return