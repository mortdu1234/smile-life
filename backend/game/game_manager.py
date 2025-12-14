"""
Gestionnaire de parties - Logique pure du jeu
"""
from typing import Dict, List, Optional
from .player import Player
from cards.factory import CardFactory

class GameManager:
    """Gère l'état et la logique d'une partie"""
    
    def __init__(self, game_id: str, num_players: int, deck_config: Optional[Dict] = None):
        self.id = game_id
        self.num_players = num_players
        self.players: List[Player] = []
        self.deck = CardFactory.create_deck(deck_config)
        self.discard = []
        self.current_player_idx = 0
        self.phase = "waiting"  # waiting, draw, play
        self.casino_card = None
        self.arc_en_ciel_mode = False
        
    def add_player(self, player: Player) -> bool:
        """Ajoute un joueur à la partie"""
        if len(self.players) >= self.num_players:
            return False
        self.players.append(player)
        return True
    
    def start_game(self) -> bool:
        """Démarre la partie"""
        if len(self.players) < 2:
            return False
            
        # Distribution initiale
        for player in self.players:
            player.draw_cards(self.deck, 5)
        
        self.phase = "draw"
        return True
    
    def draw_card(self, player_id: int, source: str = 'deck') -> Optional[Dict]:
        """Pioche une carte"""
        player = self.players[player_id]
        
        if self.phase != 'draw':
            return {'error': 'Vous devez d\'abord piocher'}
        
        if source == 'deck':
            if not self.deck:
                return {'game_over': True, 'scores': self.calculate_final_scores()}
            
            card = self.deck.pop()
            player.hand.append(card)
            self.phase = 'play'
            return {'success': True, 'card': card}
        
        elif source == 'discard':
            if not self.discard:
                return {'error': 'Défausse vide'}
            
            card = self.discard.pop()
            can_play, message = card.can_be_played(player, self)
            
            if can_play:
                player.hand.append(card)
                card.play_card(self, player)
                self.next_player()
                return {'success': True, 'card': card, 'played': True}
            else:
                self.discard.append(card)
                return {'error': message}
    
    def play_card(self, player_id: int, card_id: str) -> Dict:
        """Joue une carte"""
        player = self.players[player_id]
        
        if self.phase != 'play':
            return {'error': 'Vous devez d\'abord piocher'}
        
        card = player.get_card_by_id(card_id)
        if not card:
            return {'error': 'Carte non trouvée'}
        
        can_play, message = card.can_be_played(player, self)
        if not can_play:
            return {'error': message}
        
        # Jouer la carte
        result = card.play_card(self, player)
        
        # Gérer le mode arc-en-ciel
        if self.arc_en_ciel_mode:
            self.arc_en_ciel_card.add_card_played(self, player)
        
        return {'success': True, 'result': result}
    
    def discard_card(self, player_id: int, card_id: str) -> Dict:
        """Défausse une carte"""
        player = self.players[player_id]
        
        if self.phase != 'play':
            return {'error': 'Vous devez d\'abord piocher'}
        
        card = player.get_card_by_id(card_id)
        if not card:
            return {'error': 'Carte non trouvée'}
        
        player.hand.remove(card)
        self.discard.append(card)
        
        if not self.arc_en_ciel_mode:
            self.next_player()
        
        return {'success': True}
    
    def next_player(self):
        """Passe au joueur suivant"""
        self.current_player_idx = (self.current_player_idx + 1) % self.num_players
        
        # Passer les joueurs déconnectés
        attempts = 0
        while not self.players[self.current_player_idx].connected and attempts < self.num_players:
            self.current_player_idx = (self.current_player_idx + 1) % self.num_players
            attempts += 1
        
        self.phase = "draw"
    
    def skip_turn(self, player_id: int) -> Dict:
        """Passe le tour d'un joueur"""
        player = self.players[player_id]
        
        if player.skip_turns > 0:
            player.skip_turns -= 1
            message = f"{player.name} passe son tour ({player.skip_turns} tour(s) restant(s))"
        else:
            message = f"{player.name} passe son tour volontairement"
        
        self.next_player()
        return {'success': True, 'message': message}
    
    def calculate_final_scores(self) -> List[tuple]:
        """Calcule les scores finaux"""
        scores = []
        for player in self.players:
            if player.connected:
                smiles = player.calculate_smiles()
                scores.append((player.name, smiles, player.id))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores
    
    def to_dict(self) -> Dict:
        """Sérialise l'état du jeu"""
        return {
            'id': self.id,
            'players': [p.to_dict() for p in self.players],
            'deck_count': len(self.deck),
            'discard': [c.to_dict() for c in self.discard],
            'current_player': self.current_player_idx,
            'phase': self.phase,
            'num_players': self.num_players,
            'casino': self.casino_card.to_dict() if self.casino_card else {'open': False},
            'arc_en_ciel': self.arc_en_ciel_mode
        }
    
    def get_state_for_player(self, player_id: int) -> Dict:
        """Retourne l'état du jeu pour un joueur spécifique"""
        state = self.to_dict()
        
        # Masquer les mains des autres joueurs
        for i, player in enumerate(state['players']):
            if i != player_id:
                player['hand'] = []
        
        return state