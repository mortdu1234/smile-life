from .card import Card
from threading import Event
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.Game import Game
    from src.Player import Player
    from .children import ChildCard, DaenerysChild

class AnimalCard(Card):
    """Carte animal"""
    def __init__(self, animal_name: str, smiles: int, image_path: str):
        super().__init__(image_path)
        self.animal_name = animal_name
        self.smiles = smiles

    
    def __str__(self):
        return f"{self.animal_name} - smile : {self.smiles} - AnimalCard"
    
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'animal',
            'subtype': self.animal_name
        })
        return base
    
    def get_card_rule(self):
        return "Nous avons une carte Animal\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"l'animal est un : {self.animal_name}\n" \
        + "\nREGLES\n" \
        + "- possibilité de jouer la carte a tout moment\n"
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

class LicorneAnimal(AnimalCard):
    def __init__(self, animal_name: str, smiles: int, image_path: str):
        super().__init__(animal_name, smiles, image_path)

class DragonAnimal(AnimalCard):
    def __init__(self, animal_name: str, smiles: int, image_path: str):
        super().__init__(animal_name, smiles, image_path)
        self.selection_event: Event = Event()
        self.target_card_id: int = None
        self.target_card: Card = None
    
    def confirm_player_selection(self, data):
        """confirmation de la carte a détruire"""
        self.target_card_id = data.get('target_card_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_player_selection(self, data):
        """annulation de la carte a détruire"""
        self.selection_event.set()  # Déclencher l'événement

    def apply_card_effect(self, game, current_player):
        if any(isinstance(c, DaenerysChild) for c in current_player.get_all_played_cards()):
            for player in game.players:
                if player != current_player:
                    played_cards: list[Card] = player.get_all_played_cards()
                    emit('select_burn_card', {
                        "card_id": self.id,
                        'player_name': player.name,
                        'available_targets': [c.to_dict() for c in played_cards] 
                    })

                    print("[EVENT] : Wait for selection")
                    self.selection_event.wait()
                    self.selection_event.clear()  # Réinitialiser l'événement
                    print("[EVENT] : trigger selection")
                    
                    if self.target_card_id:
                        self.target_card = player.get_played_card_by_id(self.target_card_id) 
                        player.remove_card_from_played(self.target_card)
        return True


