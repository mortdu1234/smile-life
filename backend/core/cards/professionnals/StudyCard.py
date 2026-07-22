from ...Game import Game
from ...Player import Player
from ...Power import Power
from ...PlayerCardGroup import PlayedCardGroup as groupe
from ..Card import Card

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

MAX_STUDY_CARDS = 6

class StudyCard(Card):
    value: int
    count: bool = True # compte pour le maximum de cartes études d'un joueur
    def __init__(self, id: int, image_path: str, smiles: int, value: int, extention: "Extention"):
        super().__init__(id, image_path, smiles, extention)
        self.value = value

    def get_value(self) -> int:
        return self.value

    def get_smiles(self, owner: Player) -> int:
        powers = owner.get_power()
        if Power.STUDY_VALUE_DOUBLE in powers:
            return 2*super().get_smiles(owner) 
        return super().get_smiles(owner)

    def get_name(self) -> str:
        return f"Etude {self.value}"

    def count_number_study(self, player: "Player") -> int:
        nb = 0
        for card in player.get_card_from_group(groupe.VIE_PROFESSIONNELLE):
            if isinstance(card, StudyCard) and card.count:
                nb += 1
        return nb

    def can_be_played(self, player: Player, game: Game) -> tuple[bool, str]:
        job = player.get_job()
        if job and Power.INFINITE_STUDY not in player.get_power():
            return False, "tu as déja un métier" 
        nb_cards = self.count_number_study(player)
        if nb_cards == MAX_STUDY_CARDS and Power.INFINITE_STUDY not in player.get_power():
            return False, "tu as déja atteint le nombre maximum d'études"
        return super().can_be_played(player, game)

    def get_card_rule(self) -> str:
        return """Premet d'augmenter son niveau d'étude. Il est possible de poser jusqu'a 6 cartes études maxmimum. Les études permettent d'avoir un meilleur métier. Il n'est pas possible de poser une carte étude si on a déja un métier."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()