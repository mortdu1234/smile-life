from ...Game import Game
from ...Player import Player
from ...Power import Power
from ....userIo.interface import IOType
from .Acquisition import Acquisition
from ..hardships.HardshipCard import Hardship
from ...PlayerCardGroup import PlayedCardGroup as groupe

class Sabre(Acquisition):
    def __init__(self, id: int, image_path: str, original_price: int, cost: int):
        super().__init__(id, image_path, original_price, cost)

    def calcul_cost(self, player: Player, game: Game) -> int:
        return self.original_price
        
    def get_name(self) -> str:
        return f"Sabre"

    def sabre_effect(self, game: Game, current_player: Player) -> None:
        for target_player in game.players:
            if target_player == current_player:
                continue
            # selection des cartes malus disponibles pour se venger
            available_hardships = []
            for card in current_player.get_card_from_group(groupe.HARDSHIP):
                success, reason = card.can_be_played(current_player, game)
                if success:
                    available_hardships.append(card)
            if len(available_hardships) == 0:
                continue

            # selection du malus pour le joueur
            selected_card = current_player.get_interface().ask_card(
                prompt=f"Selection de la carte malus pour se venger de {target_player.name}",
                cards=available_hardships,
                kind=IOType.CARD_PICKER
            )
            assert selected_card is not None, "il n'y a pas de cartes selectionnées"
            assert isinstance(selected_card, Hardship), "la carte n'est pas un hardship"
            # application de la carte
            selected_card.hardship_effect(game, target_player)

    def apply_card_effect(self, game: Game, current_player: Player) -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False

        # vérifie si le joueur possède déja la carte béatrix
        from ..personnals.Children import BeatrixChild
        from ...PlayerCardGroup import PlayedCardGroup as groupe
        for card in current_player.get_card_from_group(groupe.VIE_PERSONNELLE):
            if isinstance(card, BeatrixChild):
                self.sabre_effect(game, current_player)

        return True

    def get_card_rule(self) -> str:
        return """Quand le joueur possède a la fois le sabre et béatrix, alors il peut se venger de chaque joueurs""" + "\n"+ "="*10+ "\n" + super().get_card_rule()