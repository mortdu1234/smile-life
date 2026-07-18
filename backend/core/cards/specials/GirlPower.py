from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
from ...Power import Power
from ...PlayerCardGroup import PlayedCardGroup as groupe
from ....userIo.interface import IOType
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ..Card import Card

class GrilPower(SpecialCard):    
    card_played: list[SpecialCard]
    def __init__(self, id: int, image_path: str, smiles: int):
        super().__init__(id, image_path, smiles)
        self.card_played = []

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)
    
    def get_name(self) -> str:
        return "Girl Power"

    def girl_power_effect(self, game: "Game", current_player: "Player"):
        # récupère la liste des cartes spéciales
        available_card = []
        speciales_cards = current_player.get_card_from_group(groupe.CARTES_SPECIALES)
        for card in speciales_cards:
            if card.can_be_played(current_player, game)[0] and card not in self.card_played:
                available_card.append(card)

        
        interface = current_player.get_interface()
        if len(available_card) == 0:
            print("[DEBUG] aucune cartes spéciales n'est jouables")
            return
        card_selected = interface.ask_card(
            prompt="Choisit la carte spéciale à rejouer",
            cards=available_card,
            kind=IOType.CARD_PICKER
        )
        assert card_selected is not None, "la carte n'est pas selectionnee"
        assert isinstance(card_selected, SpecialCard), "la carte n'est pas une carte speciale"
        card_selected.apply_card_effect(game, current_player)
        self.card_played.append(card_selected)
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from ..personnals.Children import FemaleChild
        current_player.add_power(Power.GIRL_POWER)
        # appliquer l'effet pour chaque fille déja posé
        played = current_player.get_card_from_group(groupe.VIE_PERSONNELLE)
        for card in played:
            if isinstance(card, FemaleChild):
                self.girl_power_effect(game, current_player)
        return super().apply_card_effect(game, current_player)
    def discard_card(self, game: "Game", owner: "Player") -> None:
        owner.remove_power(Power.GIRL_POWER)
        self.card_played = []
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """Permet de rejouer une carte spéciale déja jouée pour chaque fille posé (effet permanent)"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()