from .AnimalCard import AnimalCard
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.cards.CardAttributes import Extention

class LicorneAnimal(AnimalCard):
    """Licorne — combo licorne + arc-en-ciel + étoile filante = +3 smiles."""
    def __init__(self, id: int, image_path: str, extention: "Extention"):
        super().__init__(id, image_path=image_path, smiles=3, extention=extention)

    def get_name(self) -> str:
        return "Licorne"

    def get_card_rule(self) -> str:
        return """Une licorne est un animal particulier qui double son nombre de smile donnée si le joueur pose la licorne, l'arc-en-ciel et l'étoile filante devant lui"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()