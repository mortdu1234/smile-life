from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from ..core.Player import Player
    from ..core.cards.Card import Card
    from ..core.cards.acquisitions.Acquisition import Acquisition

class IOType(Enum):
    HARDSHIP_TARGET = "hardship-target"
    SALARY_SELECTOR = "salary-selector"
    CARD_BROWSER    = "card-browser"
    SHOW_HAND       = "show-hand"
    CARD_PICKER     = "card-picker"
    PLAYER_PICKER   = "player-picker"

class UserIO(ABC):
    @abstractmethod
    def ask_player(self, prompt: str, players: list["Player"], kind: IOType) -> "Player | None":
        """retourne l'id du joueur selectionnée"""
        pass

    @abstractmethod
    def ask_card(self, prompt: str, cards: list["Card"], kind: IOType) -> "Card | None":
        """retourne l'id de la carte selectionnée"""
        pass

    @abstractmethod
    def ask_salaries(self, acquisition: "Acquisition", salaries: Sequence["Card"], cost: int) -> list["Card"]:
        """Demande au joueur de sélectionner des salaires pour payer une acquisition.
        Retourne la liste des cartes salaire choisies (somme >= cost garanti côté frontend)."""
        pass

    @abstractmethod
    def show_cards(self, title: str, prompt: str, cards: Sequence["Card"]) -> None:
        """Affiche une liste de cartes en consultation (pas de sélection).
        Bloque jusqu'à ce que le joueur ferme l'overlay."""
        pass

    @abstractmethod
    def show_players_hand(self, players_names: Sequence[str], players_hands: Sequence[Sequence["Card"]]):
        """Affiche la liste des cartes en main des joueurs"""
        pass

    @abstractmethod
    def submit(self, index: int) -> None:
        """Appelé par la route Flask quand l'utilisateur choisit (choix simple)."""
        pass

    @abstractmethod
    def submit_indices(self, indices: list[int]) -> None:
        """Appelé par la route Flask quand l'utilisateur valide une sélection multiple."""
        pass

    @abstractmethod
    def submit_dismiss(self) -> None:
        """Appelé par la route Flask quand l'utilisateur ferme un overlay de consultation."""
        pass