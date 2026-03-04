from enum import Enum 

class PermanentEffects(Enum):
    """
    Enum for the permanent effects that a player can have.
    """
    NO_SICKNESS = "Pas de maladie"
    NO_FIRE = "Pas de Licenciement"
    NO_TAX = "Pas d'impôt"
    