from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Sequence, TypeVar

T = TypeVar("T")

if TYPE_CHECKING:
    from ..core.Player import Player
    from ..core.cards.Card import Card
    from ..core.cards.CardAttributes import CanBeUseOnAcquisition
    from ..core.cards.acquisitions.Acquisition import Acquisition
    from ..core.cards.personnals.Children import ChildCard
    from ..core.roles.PlayerRole import PlayerRole

class IOType(Enum):
    HARDSHIP_TARGET = "hardship-target"
    SALARY_SELECTOR = "salary-selector"
    CARD_BROWSER    = "card-browser"
    SHOW_HAND       = "show-hand"
    CARD_PICKER     = "card-picker"
    PLAYER_PICKER   = "player-picker"
    ERROR_LABELLING = "error-labelling"
    TROC_CHOICE     = "troc-choice"
    HAND_REORDER    = "hand-reorder"
    CHOICE          = "choice"


class UserIO(ABC):
    @abstractmethod
    def choice(self, prompt: str, choices: list[T]) -> T:
        """Affiche un message et une liste de choix (texte simple, pas de cartes).
        Bloque jusqu'à ce que le joueur sélectionne une des possibilités.
        Retourne l'élément choisi (pas un index)."""
        pass 

    @abstractmethod
    def reorder_hands(self, players: list["Player"], hands: "list[list[Card]]") -> "list[list[Card]]":
        """retourne la nouvelle liste des cartes en main dans l'ordre des players"""
        pass

    @abstractmethod
    def ask_role(self, prompt: str, cards: list["PlayerRole"], kind: IOType) -> "PlayerRole | None":
        """retourne l'id de la carte selectionnée"""
        pass
    
    @abstractmethod
    def ask_cards(self, prompt: str, cards: list["Card"], kind: IOType, nb: int) -> list["Card"]:
        """Demande au joueur de sélectionner jusqu'à nb cartes parmi la liste
        (au moins 1, au maximum nb). Retourne la liste des cartes sélectionnées."""
        pass
    
    @abstractmethod
    def ask_player(self, prompt: str, players: list["Player"], kind: IOType) -> "Player | None":
        """retourne l'id du joueur selectionnée"""
        pass

    @abstractmethod
    def ask_card(self, prompt: str, cards: list["Card"], kind: IOType) -> "Card | None":
        """retourne l'id de la carte selectionnée"""
        pass

    @abstractmethod
    def erreur_detiquetage_interface(self, owner: "Player", others: "list[Player]", children_owner: "list[ChildCard]", children_others: "list[list[ChildCard]]") -> "tuple[ChildCard, ChildCard, Player]":
        """effectue l'interface de l'erreur d'étiquetage, retourne 2 carte selectionnee avec le joueur selectionnee"""
        pass

    @abstractmethod
    def ask_troc(self, card: "Card") -> bool:
        """Demande au joueur s'il souhaite troquer la carte piochée (effet Eclipse).
        Retourne True si le joueur choisit de troquer, False s'il choisit de la garder."""
        pass

    @abstractmethod
    def ask_salaries(self, acquisition: "Acquisition", salaries: "list[CanBeUseOnAcquisition]", cost: int) -> "list[CanBeUseOnAcquisition]":
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

    @abstractmethod
    def submit_hands(self, hands: "list[list[dict]]") -> None:
        """Appelé par la route Flask quand l'utilisateur valide la réorganisation des mains.

        `hands` est une liste, dans l'ordre des joueurs, de listes de références
        vers les cartes d'origine sous la forme {"player": int, "card": int}
        (indices dans la structure `hands` passée à `reorder_hands`)."""
        pass