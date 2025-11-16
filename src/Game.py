from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.Player import Player

from src.cartes import *


class Game:
    """classe qui gere une partie"""
    def __init__(self, game_id: str, deck: list[Card], num_players: int):
        self.id: str = game_id
        self.players: list[Player] = []        
        self.num_players: int = num_players
        self.deck: list[Card] = deck
        self.discard: list[Card] = []
        self.current_player: int = 0
        self.phase: str = "waiting"
        self.players_joined: int = 0
        self.host_id: int = 0
        self.casino_card: CasinoCard = None
        self.pending_hardship = None
        self.arcEnCielMode = False
        self.arcEnCielCard: ArcEnCielCard = None

    # GESTION DECK ET DEFAUSSE
    def get_card_from_deck(self):
        """pioche une carte depuis la pioche"""
        return self.deck.pop()
    def add_card_to_deck(self, card: Card):
        """ajoute une carte à la pioche"""
        self.deck.append(card)
    def add_to_discard(self, card: Card):
        """ajoute une carte à la défausse"""
        self.discard.append(card)
    def get_card_from_discard(self):
        """pioche une carte depuis la défausse"""
        if self.discard:
            return self.discard.pop()
        return None
    

    def add_player(self, player: 'Player'):
        """Ajoute un joueur à la partie"""
        if isinstance(player, 'Player'):
            self.players.append(player)
            if player.connected:
                self.players_joined += 1

    def next_player(self):
        self.change_current_player()
        self.phase = "draw"

    def change_current_player(self):
        """Change le joueur qui joue en passant automatiquement les joueurs déconnectés"""
        self.current_player = (self.current_player + 1) % self.num_players
        
        attempts = 0
        while not self.players[self.current_player].connected and attempts < self.num_players:
            self.current_player = (self.current_player + 1) % self.num_players
            attempts += 1

    def to_dict(self):
        """Retourne une représentation dict complète du jeu"""
        return {
            "id": self.id,
            "players": [p.to_dict() for p in self.players],
            "deck": [c.to_dict() for c in self.deck],
            "deck_count": len(self.deck),
            "discard": [c.to_dict() for c in self.discard],
            "current_player": self.current_player,
            "phase": self.phase,
            "last_discard": self.get_card_from_discard().to_dict(),
            "num_players": self.num_players,
            "players_joined": self.players_joined,
            "host_id": self.host_id,
            "casino": self.casino_card.to_dict() if self.casino_card else {"open": False},
            "pending_hardship": self.pending_hardship,
            "arc_en_ciel": self.arcEnCielMode,
            "arc_en_ciel_card": self.arcEnCielCard.to_dict() if self.arcEnCielCard else {}    
        }

    def broadcast_update(self, message: str = ""):
        """
        Envoie une mise à jour à tous les joueurs connectés
        
        Args:
            message: Message optionnel à afficher aux joueurs
            socketio: Instance de SocketIO pour l'émission (doit être passée depuis l'extérieur)
        """            
        from constants import socketio
        
        print(f"[start]: Game.broadcast_update - message: '{message}'")
        
        for player in self.players:
            if player.connected:
                print(f"[broadcast] Sending update to player {player.id} ({player.name})")
                socketio.emit('game_updated', {
                    'game': self.to_dict(),
                    'message': message
                }, room=player.session_id)