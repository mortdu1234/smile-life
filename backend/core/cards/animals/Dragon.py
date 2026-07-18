from backend.core.Game import Game
from backend.core.Player import Player

from .AnimalCard import AnimalCard
from ...PlayerCardGroup import PlayedCardGroup as groupe
from ...Power import Power
from ....userIo.interface import IOType

class Dragon(AnimalCard):
    def __init__(self, id: int, image_path: str):
        super().__init__(id, image_path=image_path, smiles=3)

    def get_name(self) -> str:
        return "Dragon"

    def dragon_effect(self, game: Game, current_player: Player) -> bool:
        from ..personnals.Children import ChildCard
        for target_player in game.players:
            if target_player == current_player:
                continue
            # selection des cartes disponibles
            cards_available = []
            cards = target_player.get_card_from_group(groupe.ACQUISITIONS)
            cards += target_player.get_card_from_group(groupe.ANIMALS)
            cards += target_player.get_card_from_group(groupe.OTHER)
            cards += target_player.get_card_from_group(groupe.SALARIES)
            cards += target_player.get_card_from_group(groupe.VIE_PERSONNELLE)
            cards += target_player.get_card_from_group(groupe.VIE_PROFESSIONNELLE)
            cards += target_player.get_card_from_group(groupe.SPECIAL)
            for card in cards:
                if not card.is_protected:
                    cards_available.append(card)

            enfants = target_player.get_card_from_group(groupe.CHILDREN)
            for card in enfants:
                if not(Power.CHILDREN_PROTECTED in target_player.get_power() and isinstance(card, ChildCard)) and not card.is_protected:
                    cards_available.append(card)

            if len(cards_available) == 0:
                continue

            
            # affichage de la selection de la carte
            selected_card = current_player.get_interface().ask_card(
                prompt=f"Selection de la carte a bruler pour le joueur {target_player.name}",
                cards=cards_available,
                kind=IOType.CARD_PICKER
            )
            assert selected_card is not None, "aucune cartes n'est selectionnées"
            # suppression de la carte
            target_player.remove_card(selected_card, game)
            game.add_card_to_cards_remove(selected_card)

        return True

    def apply_card_effect(self, game: Game, current_player: Player) -> bool:
        played = current_player.get_card_from_group(groupe.CHILDREN)
        from ..personnals.Children import DaenerysChild
        for card in played:
            if isinstance(card, DaenerysChild):
                self.dragon_effect(game, current_player)
        return super().apply_card_effect(game, current_player)

    def get_card_rule(self) -> str:
        return """Quand le dragon et daeneris sont posé sur le terrain, alors le joueur peut faire bruler une carte posé pour chaque joueurs"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()