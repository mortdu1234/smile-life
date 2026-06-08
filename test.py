from enum import Enum

class GameSpecificState(Enum):
    ARC_EN_CIEL = "arc_en_ciel"
    CHANCE = "chance"

    def set_ARC_EN_CIEL_value(value: int):
        GameSpecificState.ARC_EN_CIEL = value

    def reduce_ARC_EN_CIEL_value():
        GameSpecificState.ARC_EN_CIEL -= 1
                