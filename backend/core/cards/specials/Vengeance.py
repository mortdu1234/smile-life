from backend.core.PlayerCardGroup import PlayedCardGroup
from backend.core.cards.hardships.HardshipCard import Hardship
from ....userIo.interface import IOType
from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ..Card import Card
        
    
class Vengeance(SpecialCard):
    hardship_card: Hardship | None
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path, 0)
        self.hardship_card = None
    def get_name(self) -> str:
        return "Vengeance"
    def get_available_hardships(self, game: "Game") -> "list[Card]":
        current_player = game.get_current_player()
        hardships_cards = current_player.get_card_from_group(PlayedCardGroup.HARDSHIP)
        cards_availables = []
        for card in hardships_cards:
            success, reason = card.can_be_played(current_player, game)
            if success:
                cards_availables.append(card) 
        return cards_availables

    def select_harship(self, game: "Game", interface: "UserIO") -> bool:
        cards_availables = self.get_available_hardships(game)
        selected_card: "Card | None" = interface.ask_card(prompt="Selection de la carte malus", cards=cards_availables, kind=IOType.CARD_PICKER)
        if not selected_card:
            return False
        if not isinstance(selected_card, Hardship):
            print("[ERROR] la carte sélectionnée n'est pas une HARDSHIP")
            return False
        self.hardship_card = selected_card
        return True


    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        cards_availables = self.get_available_hardships(game)
        if len(cards_availables) == 0:
            return False, "il n'y a pas de cible possible"
        return super().can_be_played(player, game)

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        print("[DEBUG] TODO")
        success = self.select_harship(game, interface)
        if not success or not self.hardship_card:
            return False
        # ajouter temporairement l'hardship dans la main
        current_player.add_card_to_hand(self.hardship_card)
        self.hardship_card.play_card(game, current_player, interface)        

        return super().apply_card_effect(game, current_player, interface)

    def get_card_rule(self) -> str:
        return """La carte Vengeance permet d'attribuer a un adversaire une des cartes Malus recus"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()