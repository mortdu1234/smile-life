from ..Acquisition import Acquisition

class Potion(Acquisition):

    def get_card_rule(self) -> str:
        return """""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    