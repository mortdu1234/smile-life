from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..Player import Player
    from ..Game import Game
    from ...userIo.interface import UserIO

class Card:
    id: int
    image_path: str
    smiles: int
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
        }
    def __init__(self, id: int, image_path: str, smiles: int):
        self.id = id
        self.image_path = image_path
        self.smiles = smiles
    def get_id(self) -> int:
        return self.id
    def get_smiles(self) -> int:
        return self.smiles
    # ------------------------------------------------------------------ #
    #  Méthodes avec comportement par défaut                             #
    # ------------------------------------------------------------------ #
    def get_effect(self) -> None:
        """
        Décrit l'effet de la carte en données pures.
        Retourne None si l'effet est entièrement géré par apply_card_effect().
        """
        return None

    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        """Applique l'effet de la carte. Retourne True si succès."""
        return True

    def play_card(self, game: "Game", current_player: "Player", interface: "UserIO") -> None:
        """Pose la carte : applique l'effet puis déplace la carte dans les posées."""
        if self.apply_card_effect(game, current_player, interface):
            current_player.remove_card_from_hand(self)
            current_player.add_card_to_played(self)
        else:
            print("[ERROR] : il y a une erreur lors du pouvoir")

    def get_card_rule(self) -> str:
        return f"Carte classique — donne {self.smiles} smile(s)."
    
    # ------------------------------------------------------------------ #
    #  Méthodes à redéfinir                                              #
    # ------------------------------------------------------------------ #

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        """Vérifie si la carte peut être jouée dans le contexte courant."""
        return True, ""