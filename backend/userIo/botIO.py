from .interface import UserIO, IOType
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from ..core.Player import Player
    from ..core.cards.Card import Card
    from ..core.cards.acquisitions.Acquisition import Acquisition

import random

class BotIO(UserIO):
    def ask_player(self, prompt: str, players: list["Player"], kind: IOType) -> "Player | None":
        """retourne l'id du joueur selectionnée"""
        return random.choice(players)
    
    def ask_card(self, prompt: str, cards: list["Card"], kind: IOType) -> "Card | None":
        """retourne l'id de la carte selectionnée"""
        return random.choice(cards)
        
    def ask_salaries(self, acquisition: "Acquisition", salaries: Sequence["Card"], cost: int) -> list["Card"]:
        """Demande au joueur de sélectionner des salaires pour payer une acquisition.
        Retourne la liste des cartes salaire choisies (somme >= cost garanti côté frontend)."""
        selected_cards = []
        actual_cost = 0
        for card in salaries:
            selected_cards.append(card)
            if actual_cost >= cost:
                return selected_cards
        return selected_cards
    
    def show_cards(self, title: str, prompt: str, cards: Sequence["Card"]) -> None:
        """Affiche une liste de cartes en consultation (pas de sélection).
        Bloque jusqu'à ce que le joueur ferme l'overlay."""
        pass

    
    def show_players_hand(self, players_names: Sequence[str], players_hands: Sequence[Sequence["Card"]]):
        """Affiche la liste des cartes en main des joueurs"""
        pass

    
    def submit(self, index: int) -> None:
        """Appelé par la route Flask quand l'utilisateur choisit (choix simple)."""
        pass

    
    def submit_indices(self, indices: list[int]) -> None:
        """Appelé par la route Flask quand l'utilisateur valide une sélection multiple."""
        pass

    
    def submit_dismiss(self) -> None:
        """Appelé par la route Flask quand l'utilisateur ferme un overlay de consultation."""
        pass