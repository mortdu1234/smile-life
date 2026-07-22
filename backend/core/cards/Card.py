from typing import TYPE_CHECKING
from backend.core.Power import Power

if TYPE_CHECKING:
    from backend.core.Player import Player
    from backend.core.Game import Game
    from backend.core.cards.CardAttributes import Extention


class Card:
    id: int
    image_path: str
    smiles: int
    is_protected: bool = False
    extention: "Extention"
    def set_protected(self):
        self.is_protected = True
    def set_not_protected(self):
        self.is_protected = False

    def to_dict(self) -> dict:
        # MRO du plus spécifique au plus général,
        # sans `object` et sans `Card` (trop générique pour le routing JS)
        mro = [
            cls.__name__ for cls in type(self).__mro__
            if cls not in (object, Card)
        ]
        return {
            'id': self.id,
            'name': self.__class__.__name__,
            'type': self.__class__.__name__,
            'mro': mro,
            'image_path': self.image_path,
            'smiles': self.smiles,
            'description': self.get_card_rule(),
            "is_protected": self.is_protected
        }
    def __init__(self, id: int, image_path: str, smiles: int, extention: "Extention"):
        self.id = id
        self.image_path = image_path
        self.smiles = smiles
        self.extention = extention

    def get_id(self) -> int:
        return self.id
    def get_smiles(self, owner: "Player") -> int:
        return self.smiles
    def get_name(self) -> str:
        return str(self.__class__.__name__)
    # ------------------------------------------------------------------ #
    #  Méthodes avec comportement par défaut                             #
    # ------------------------------------------------------------------ #

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        """Applique l'effet de la carte. Retourne True si succès."""
        return True

    def play_card(self, game: "Game", current_player: "Player") -> None:
        """Pose la carte : applique l'effet puis déplace la carte dans les posées."""
        if self.apply_card_effect(game, current_player):
            current_player.remove_card_from_hand(self)
            current_player.add_card_to_played(self)
        else:
            print("[ERROR] : il y a une erreur lors du pouvoir")

    # ------------------------------------------------------------------ #
    #  Méthodes à redéfinir                                              #
    # ------------------------------------------------------------------ #
    def get_card_rule(self) -> str:
        return f"Carte classique — donne {self.smiles} smile(s).\n"

    def discard_card(self, game: "Game", owner: "Player") -> None:
        """Effectue les actions lors de la perte de la carte"""
        pass    

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        """Vérifie si la carte peut être jouée dans le contexte courant."""
        powers = player.get_power()
        if Power.CANT_PLACE_CARD in powers:
            return False, "Vous ne pouvez plus poser de cartes"
        return True, ""
    
class InstantPlayedCard(Card):
    pass
