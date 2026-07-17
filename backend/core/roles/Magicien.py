from typing import TYPE_CHECKING

from backend.userIo.interface import IOType

from .PlayerRole import PlayerRole
from ..Power import Power
if TYPE_CHECKING:
    from ..Game import Game
    from ..Player import Player

class Magicien(PlayerRole):
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)
        self.powers = [Power.STUDY_VALUE_DOUBLE]

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.Eclipse import Eclipse
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, Eclipse):
            return False, "Ce n'est pas le bon ephemeride"
        return super().can_use_instant_power(game, owner)
     
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""
        # récupération des cartes en mains
        cards = []
        for player in game.players:
            if player == owner:
                continue
            cards.extend(player.get_hand())

        interface = owner.get_interface()
        selected_card = interface.ask_card(
            prompt="Selectionner une carte en main a voler pour un joueur",
            cards=cards,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None, "aucune cartes selectionnées"

        # récupération du joueur qui possède cette carte
        target = None
        for player in game.players:
            if player == owner:
                continue
            if selected_card in player.get_hand():
                target = player
        assert target is not None, "la cible n'est pas trouvée"
        target.remove_card_from_hand(selected_card)
        target.add_power(Power.SUB_1_HAND_CARD)

        owner.add_power(Power.ADD_1_HAND_CARD)
        owner.add_card_to_hand(selected_card)
        
        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return "PP : double les smiles données par les études | PE (Eclipse) : regarder toutes les cartes en main des joueurs pour sélectionner une carte de votre choix, vous jouerez avec une carte de plus et il jouera avec une carte de moins."+ "\n"+ "="*10+ "\n" + super().get_card_rule()
