from uuid import UUID
from ..cards import Card 
from .player import Player

class Game:
    def __init__(self, game_id: 'UUID'):
        self.game_id: 'UUID' = game_id      # Unique identifier for the game
        self.deck: 'list[Card]' = []        # la pioche de jeu
        self.discard: 'list[Card]' = []     # la defausse de jeu
        self.players: 'list[Player]' = []   # liste des joueurs dans la partie
        self.idx_current_player: int = 0    # index du joueur courant dans la liste des joueurs

