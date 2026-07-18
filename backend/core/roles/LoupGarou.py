import random
from typing import TYPE_CHECKING

from ..PlayerCardGroup import PlayedCardGroup as groupe
from .PlayerRole import PlayerRole
from ..Power import Power
if TYPE_CHECKING:
    from ..cards.Card import Card
    from ..Game import Game
    from ..Player import Player

class LoupGarou(PlayerRole):
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)
        self.powers = [Power.DOUBLE_ANIMAL]

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.PleineLune import PleineLune
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, PleineLune):
            return False, "Ce n'est pas le bon ephemeride"
        return super().can_use_instant_power(game, owner)

    def get_available_cards(self, target: "Player") -> "list[Card]":
        from ..cards.personnals.Children import ChildCard
        from ..cards.animals.AnimalCard import AnimalCard
        available_cards = []
        zone = target.get_card_from_group(groupe.ANIMALS) + target.get_card_from_group(groupe.CHILDREN) 
        for card in zone:
            if isinstance(card, (AnimalCard, ChildCard)) and not card.is_protected:
                available_cards.append(card)
        return available_cards
     
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""   
        from ..cards.animals.AnimalCard import AnimalCard
        for player in game.players:
            if player == owner:
                continue
            available_cards = self.get_available_cards(player)
            if len(available_cards) == 0:
                continue
            selected_card = random.choice(available_cards)
            player.remove_card(selected_card, game)
            if isinstance(selected_card, AnimalCard):
                owner.add_card_to_played(selected_card)
        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return "PP : Animaux valent double | PE (Pleine Lune) : pour chaque joueur, selectionne aléatoirement parmis les enfants et les animaux posé une carte. Si c'est un enfants, alors il est supprimé, si c'est un animal alors il est posé sur devant le joueur."+ "\n"+ "="*10+ "\n" + super().get_card_rule()
