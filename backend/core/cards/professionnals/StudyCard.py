from ...Game import Game
from ...Player import Player
from ...Power import Power

from ..Card import Card

class StudyCard(Card):
    value: int
    def __init__(self, id: int, image_path: str, smiles: int, value: int):
        super().__init__(id, image_path, smiles)
        self.value = value

    def get_value(self) -> int:
        return self.value

    def get_name(self) -> str:
        return f"Etude {self.value}"

    def can_be_played(self, player: Player, game: Game) -> tuple[bool, str]:
        job = player.get_job()
        if job and Power.INFINITE_STUDY not in player.get_power():
            return False, "tu as déja un métier" 
        return super().can_be_played(player, game)

    def get_card_rule(self) -> str:
        return """Premet d'augmenter son niveau d'étude. Il est possible de poser jusqu'a 6 cartes études maxmimum. Les études permettent d'avoir un meilleur métier. Il n'est pas possible de poser une carte étude si on a déja un métier."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()