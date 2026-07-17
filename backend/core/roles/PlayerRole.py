from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Game import Game
    from ..Player import Player
    from ..Power import Power

class PlayerRole:
    powers: "list[Power]" = []
    is_used: bool = False
    img_path: str
    def __init__(self, img_path: str) -> None:
        self.img_path = img_path

    def do_receive_action(self, game: "Game", owner: "Player"):
        """effectue les actions lors de la reception du role"""
        return
    
    def can_be_attribute(self, game: "Game") -> "tuple[bool, str]":
        return True, ""

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        if self.is_used:
            return False, "Le pouvoir à déjà été utilisé"
        return True, ""

    def to_dict(self) -> dict:        
        return {
            'name': self.__class__.__name__,
            'image_path': self.img_path,
            'description': self.get_card_rule(),
        }
    
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""
        is_used = True

    def get_power(self):
        """retourne une copie de la liste des pouvoirs du roles"""
        return self.powers.copy()

    def get_card_rule(self) -> str:
        return "possède un pouvoir permanent (PP) et un pouvoir ephémère (PE), les pouvoirs ephémère peuvent etre utilisé pendant une ephemeride particulière et remplace un tour de jeu."
