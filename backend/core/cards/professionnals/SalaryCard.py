from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player

from ..Card import Card

class SalaryCard(Card):
    value: int
    def __init__(self, id: int, image_path: str, smiles: int, value: int):
        super().__init__(id, image_path, smiles)
        self.value = value
    def to_dict(self) -> dict:
        data = super().to_dict()
        data["value"] = self.value
        return data

    def get_value(self):
        return self.value

    def get_name(self) -> str:
        return f"Salaire {self.value}"

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        job=player.get_job()
        if not (job and job.get_salary() >= self.value):
            if job:
                return False, f"le métier ne permet pas de mettre des salaires de valeur {self.value}>{job.get_salary()}"  
            return False, f"Vous n'avez pas de métiers0"
        return super().can_be_played(player, game)
    def get_card_rule(self) -> str:
        return f"Il s'agit d'une carte Salaire de valeur {self.value}" + """les salaires peuvent etre dépensé, dans ce cas, ils arrivent dans la zone "Cartes Protégéesé". POur etre posé il faut avoir un métier ou les miser au casino (si le casino est ouvert)"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()