from typing import TYPE_CHECKING

from backend.userIo.interface import IOType

from .PlayerRole import PlayerRole
from ..Power import Power
if TYPE_CHECKING:
    from ..Game import Game
    from ..Player import Player

class Mutant(PlayerRole):
    role_copie: str = ""
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)

    def can_be_attribute(self, game: "Game") -> tuple[bool, str]:
        if len(game.players) < 3:
            return False, "Pas assez de joueur"
        return super().can_be_attribute(game)

    def do_receive_action(self, game: "Game", owner: "Player"):
        print("[DEBUG] selection role power")
        self.apply_instant_power(game, owner)
        
    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.Equinoxe import Equinoxe
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, Equinoxe):
            return False, "Ce n'est pas le bon ephemeride"
        return super().can_use_instant_power(game, owner)

    def get_available_roles(self, game: "Game", owner: "Player") -> "list[PlayerRole]":
        """selectionne les roles disponibles"""
        available_roles = []
        for player in game.players:
            if player == owner:
                continue
            role = player.get_role()
            if role:
                if isinstance(role, Mutant):
                    continue
                available_roles.append(role)
        return available_roles

    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""
        print("DEBUG : apply instant power")
        interface = owner.get_interface()
        available_roles = self.get_available_roles(game, owner)
        selected_role = interface.ask_role(
            prompt="Choisissez un role a copier",
            cards=available_roles,
            kind=IOType.CARD_PICKER
        )
        assert isinstance(selected_role, PlayerRole), "la carte choisit n'est pas un role"
        self.powers = selected_role.get_power()
        self.role_copie = selected_role.__class__.__name__

        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return f"PP (courrant : {self.role_copie}): Copie le pouvoir permanent d'un autre joueur | PE (Equinoxe) : permet de changer de pouvoir permanent"+ "\n"+ "="*10+ "\n" + super().get_card_rule()
