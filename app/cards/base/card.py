"""
Classe de base abstraite pour toutes les cartes.
Aucun import Flask — logique pure testable unitairement.
"""
import uuid
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game
from app.core.effect import CardEffect


class Card(ABC):
    """Interface commune à toutes les cartes."""

    def __init__(self, image_path: str):
        self.id: str = str(uuid.uuid4())
        self.smiles: int = 0
        self.image: str = image_path

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    # ------------------------------------------------------------------ #
    #  Méthodes abstraites                                                 #
    # ------------------------------------------------------------------ #

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Sérialise la carte en dict pour le client."""
        return {
            "id": self.id,
            "smiles": self.smiles,
            "type": self.__class__.__name__.lower(),
            "image": self.image,
            "rule": self.get_card_rule(),
        }

    @abstractmethod
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        """Vérifie si la carte peut être jouée dans le contexte courant."""
        return True, ""

    # ------------------------------------------------------------------ #
    #  Méthodes avec comportement par défaut                              #
    # ------------------------------------------------------------------ #

    def get_effect(self) -> CardEffect | None:
        """
        Décrit l'effet de la carte en données pures.
        Retourne None si l'effet est entièrement géré par apply_card_effect().
        """
        return None

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        """Applique l'effet de la carte. Retourne True si succès."""
        return True

    def play_card(self, game: "Game", current_player: "Player") -> None:
        """Pose la carte : applique l'effet puis déplace la carte dans les posées."""
        if self.apply_card_effect(game, current_player):
            current_player.hand.remove(self)
            current_player.add_card_to_played(self)

    def get_card_rule(self) -> str:
        return f"Carte classique — donne {self.smiles} smile(s)."
