from .card import Card
from threading import Event
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.Game import Game
    from src.Player import Player
    from .special_cards import GirlPowerCard
    from .animals import DragonAnimal
    from .acquisitions import SabreCard

class ChildCard(Card):
    """Carte enfant"""
    def __init__(self, name: str, image_path: str):
        super().__init__(image_path)
        self.name = name
        self.smiles = 2
    
    
    def __str__(self):
        return f"{self.name} - smile : {self.smiles} - ChildCard"
    
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'child',
            'subtype': self.name
        })
        return base
    
    
    def get_card_rule(self):
        return "Nous avons une carte Enfant\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"l'enfant s'appelle : {self.name}\n" \
        + "\nREGLES\n" \
        + "- il faut avoir au moins 1 marriage avant de pouvoir poser un enfant\n"
    

    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        last_flirt = current_player.get_last_flirt()
        if isinstance(last_flirt, FlirtWithChildCard) and last_flirt.child_link is None:
            return True, ""
        if not current_player.is_married():
            return False, "Vous devez être marié(e) pour avoir un enfant"
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        last_flirt = current_player.get_last_flirt()
        if isinstance(last_flirt, FlirtWithChildCard) and last_flirt.child_link is None:
            last_flirt.child_link = self
        super().play_card(game, current_player)

class FemaleChild(Card):
    def apply_card_effect(self, game: 'Game', current_player: 'Player'):
        for card in current_player.get_played_effet_permanent():
            if isinstance(card, GirlPowerCard):
                current_player.remove_card_from_played(card)
                current_player.add_card_to_hand(card)
                card.effect(game, current_player)
        return True
    
class MaleChild(Card):
    pass

class GirlPowerChild(Card):
    pass

class AngelaChild(ChildCard, GirlPowerChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class BeatrixChild(ChildCard, FemaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)
    
    def apply_card_effect(self, game, current_player):
        played = current_player.get_played_acquisitions()
        for card in played:
            if isinstance(card, SabreCard):
                card.apply_card_effect(game, current_player)
        return True

class DaenerysChild(ChildCard, FemaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)
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
        if any(isinstance(c, DragonAnimal) for c in current_player.get_all_played_cards()):
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

class DianaChild(ChildCard, FemaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class HarryChild(ChildCard, MaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class HermioneChild(ChildCard, FemaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class LaraChild(ChildCard, FemaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class LeiaChild(ChildCard, FemaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class LouiseChild(ChildCard, GirlPowerChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class LuigiChild(ChildCard, MaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class MarioChild(ChildCard, MaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class LukeChild(ChildCard, MaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class OlympeChild(ChildCard, GirlPowerChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class RockyChild(ChildCard, MaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class SimoneChild(ChildCard, GirlPowerChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

class ZeldaChild(ChildCard, FemaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)
