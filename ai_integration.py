# -*- coding: utf-8 -*-

"""
Intégration de l'IA avec le serveur Flask
"""

import torch
import numpy as np
from typing import Dict, Optional
from ai_player import GameStateEncoder, SmileAIAgent, ActionManager
from card_classes import Player
from constants import games


class AIPlayer(Player):
    """Joueur IA héritant de la classe Player"""
    
    def __init__(self, player_id: int, name: str = "IA", model_path: Optional[str] = None):
        super().__init__(player_id, name)
        
        # Initialiser les composants de l'IA
        self.encoder = GameStateEncoder()
        self.action_manager = ActionManager()
        
        # Charger le modèle
        self.agent = SmileAIAgent(
            state_size=self.encoder.state_size,
            action_size=self.action_manager.action_size,
            device='cpu'  # CPU pour la production
        )
        
        if model_path:
            try:
                self.agent.load(model_path)
                self.agent.epsilon = 0.05  # Faible exploration en production
                print(f"[IA] Modèle chargé depuis {model_path}")
            except Exception as e:
                print(f"[IA] Erreur lors du chargement du modèle: {e}")
                print(f"[IA] Utilisation d'un modèle non entraîné")
        
        self.is_ai = True
        self.decision_count = 0
    
    def get_game_state(self, game) -> Dict:
        """
        Extrait l'état du jeu pour l'IA
        
        Args:
            game: Instance du jeu
            
        Returns:
            Dictionnaire représentant l'état
        """
        # Main du joueur
        my_hand = [card.to_dict() for card in self.hand]
        
        # Cartes posées
        my_played = {
            category: [card.to_dict() for card in cards]
            for category, cards in self.played.items()
        }
        
        # Informations sur les adversaires
        opponents = []
        for player in game.players:
            if player.id != self.id and player.connected:
                opponents.append({
                    'id': player.id,
                    'name': player.name,
                    'hand_count': len(player.hand),
                    'smiles': self._calculate_smiles(player),
                    'has_job': player.has_job(),
                    'is_married': player.is_married(),
                    'skip_turns': player.skip_turns,
                    'received_hardships': [
                        h.to_dict().get('subtype', 'unknown')
                        for h in player.received_hardships
                    ]
                })
        
        # état global
        my_smiles = self.calculate_smiles()
        all_smiles = sorted([p.calculate_smiles() for p in game.players if p.connected], reverse=True)
        my_position = all_smiles.index(my_smiles) if my_smiles in all_smiles else len(all_smiles)
        leader_smiles = all_smiles[0] if all_smiles else 0
        
        return {
            'my_hand': my_hand,
            'my_played': my_played,
            'my_smiles': my_smiles,
            'opponents': opponents,
            'phase': game.phase,
            'is_my_turn': game.current_player == self.id,
            'skip_turns': self.skip_turns,
            'heritage': self.heritage,
            'deck_count': len(game.deck),
            'discard_count': len(game.discard),
            'turn_number': getattr(game, 'turn_number', 0),
            'num_players': game.num_players,
            'casino_open': game.casino_card is not None if hasattr(game, 'casino_card') else False,
            'arc_en_ciel_mode': game.arcEnCielMode if hasattr(game, 'arcEnCielMode') else False,
            'my_position': my_position,
            'leader_position': leader_smiles,
            'position_diff': leader_smiles - my_smiles,
            'can_win_next_turn': my_smiles >= 25,
            'received_hardships': [
                h.to_dict().get('subtype', 'unknown')
                for h in self.received_hardships
            ]
        }
    
    def _calculate_smiles(self, player: Player) -> int:
        """Calcule les smiles d'un joueur"""
        return player.calculate_smiles()
    
    def decide_action(self, game) -> Dict:
        """
        Décide de l'action à effectuer
        
        Args:
            game: Instance du jeu
            
        Returns:
            Dictionnaire décrivant l'action à effectuer
        """
        self.decision_count += 1
        
        # Extraire l'état du jeu
        game_state = self.get_game_state(game)
        
        # Encoder l'état
        encoded_state = self.encoder.encode_state(game_state)
        
        # Obtenir les actions valides
        valid_actions = self.action_manager.get_valid_actions(game_state)
        
        if not valid_actions:
            print(f"[IA] Aucune action valide, passage du tour")
            return {'type': 'skip_turn'}
        
        # Choisir une action
        action_idx = self.agent.act(encoded_state, valid_actions)
        
        # Décoder l'action
        action = self.action_manager.decode_action(action_idx, game_state)
        
        # Log
        action_type = action.get('type', 'unknown')
        print(f"[IA] Décision #{self.decision_count}: {action_type}")
        
        return action
    
    def execute_turn(self, game, socketio):
        """
        Exécute un tour complet de l'IA
        
        Args:
            game: Instance du jeu
            socketio: Instance SocketIO pour les notifications
        """
        import time
        
        # Attendre un peu pour simuler la réflexion
        time.sleep(0.5)
        
        try:
            # Décider de l'action
            action = self.decide_action(game)
            action_type = action.get('type')
            
            # Exécuter l'action
            if action_type == 'draw':
                self._execute_draw(game, action, socketio)
            
            elif action_type == 'play_card':
                self._execute_play_card(game, action, socketio)
            
            elif action_type == 'discard_card':
                self._execute_discard_card(game, action, socketio)
            
            elif action_type == 'skip_turn':
                self._execute_skip_turn(game, socketio)
            
            else:
                print(f"[IA] Action inconnue: {action_type}")
                self._execute_skip_turn(game, socketio)
        
        except Exception as e:
            print(f"[IA] Erreur lors de l'exécution du tour: {e}")
            import traceback
            traceback.print_exc()
            # En cas d'erreur, passer le tour
            self._execute_skip_turn(game, socketio)
    
    def _execute_draw(self, game, action, socketio):
        """Exécute une action de pioche"""
        source = action.get('source', 'deck')
        
        if source == 'deck' and game.deck:
            card = game.deck.pop()
            self.hand.append(card)
            game.phase = 'play'
            print(f"[IA] Pioche dans le deck")
        
        elif source == 'discard' and game.discard:
            card = game.discard.pop()
            if card.can_be_played(self, game)[0]:
                self.hand.append(card)
                card.play_card(game, self)
                game.next_player()
                print(f"[IA] Pioche et joue depuis la défausse")
            else:
                game.discard.append(card)
                print(f"[IA] Carte de la défausse non jouable")
        
        from constants import update_all_player
        update_all_player(game, f"{self.name} (IA) a pioché")
    
    def _execute_play_card(self, game, action, socketio):
        """Exécute une action de jeu de carte"""
        card_id = action.get('card_id')
        
        card = None
        for c in self.hand:
            if c.id == card_id:
                card = c
                break
        
        if card:
            success, message = card.can_be_played(self, game)
            if success:
                card.play_card(game, self)
                print(f"[IA] Joue {card.__class__.__name__}")
                
                from constants import update_all_player
                update_all_player(game, f"{self.name} (IA) a joué une carte")
            else:
                print(f"[IA] Carte non jouable: {message}")
                self._execute_skip_turn(game, socketio)
        else:
            print(f"[IA] Carte non trouvée")
            self._execute_skip_turn(game, socketio)
    
    def _execute_discard_card(self, game, action, socketio):
        """Exécute une action de défausse"""
        card_id = action.get('card_id')
        
        card = None
        for c in self.hand:
            if c.id == card_id:
                card = c
                break
        
        if card:
            self.hand.remove(card)
            game.discard.append(card)
            game.next_player()
            print(f"[IA] Défausse une carte")
            
            from constants import update_all_player
            update_all_player(game, f"{self.name} (IA) a défaussé une carte")
        else:
            print(f"[IA] Carte non trouvée pour défausse")
            self._execute_skip_turn(game, socketio)
    
    def _execute_skip_turn(self, game, socketio):
        """Exécute un passage de tour"""
        if self.skip_turns > 0:
            self.skip_turns -= 1
            message = f"{self.name} (IA) passe son tour ({self.skip_turns} restant(s))"
        else:
            message = f"{self.name} (IA) passe son tour"
        
        game.next_player()
        print(f"[IA] Passe le tour")
        
        from constants import update_all_player
        update_all_player(game, message)


# ============================================
# GESTIONNAIRE DE TOURS IA
# ============================================

class AITurnManager:
    """Gère les tours des joueurs IA"""
    
    @staticmethod
    def should_ai_play(game) -> bool:
        """Vérifie si c'est au tour d'un joueur IA"""
        if game.phase not in ['draw', 'play']:
            return False
        
        current_player = game.players[game.current_player]
        return hasattr(current_player, 'is_ai') and current_player.is_ai
    
    @staticmethod
    def execute_ai_turn(game, socketio):
        """Exécute le tour d'un joueur IA"""
        current_player = game.players[game.current_player]
        
        if not hasattr(current_player, 'is_ai') or not current_player.is_ai:
            return
        
        print(f"\n[IA] === Début du tour de {current_player.name} ===")
        print(f"[IA] Phase: {game.phase}")
        print(f"[IA] Cartes en main: {len(current_player.hand)}")
        print(f"[IA] Smiles: {current_player.calculate_smiles()}")
        
        # Exécuter le tour
        current_player.execute_turn(game, socketio)
        
        print(f"[IA] === Fin du tour ===\n")


# ============================================
# HOOK POUR INTÉGRATION
# ============================================

def integrate_ai_player(game_id: str, player_slot: int, model_path: str = "models/smile_ai_final.pth"):
    """
    Intègre un joueur IA dans une partie
    
    Args:
        game_id: ID de la partie
        player_slot: Slot du joueur (0-4)
        model_path: Chemin vers le modèle IA
    """
    if game_id not in games:
        print(f"[IA] Partie {game_id} non trouvée")
        return False
    
    game = games[game_id]
    
    if player_slot >= len(game.players):
        print(f"[IA] Slot {player_slot} invalide")
        return False
    
    # Remplacer le joueur par une IA
    ai_player = AIPlayer(player_slot, f"IA-{player_slot}", model_path)
    ai_player.connected = True
    
    # Donner des cartes à l'IA
    if game.deck:
        ai_player.hand = [game.deck.pop() for _ in range(5)]
    
    game.players[player_slot] = ai_player
    game.players_joined += 1
    
    print(f"[IA] Joueur IA ajouté au slot {player_slot} de la partie {game_id}")
    return True


# ============================================
# MODIFICATION DE app.py
# ============================================

def patch_game_loop():
    """
    Patch pour intégrer l'IA dans la boucle de jeu
    Ajoutez ceci dans votre app.py
    """
    
    # Exemple d'intégration dans le gestionnaire de tour
    """
    from ai_integration import AITurnManager
    
    @socketio.on('game_updated')
    def on_game_updated(data):
        game_id = data.get('game_id')
        if game_id in games:
            game = games[game_id]
            
            # Vérifier si c'est au tour d'une IA
            if AITurnManager.should_ai_play(game):
                # Exécuter le tour de l'IA après un court délai
                socketio.start_background_task(
                    target=lambda: AITurnManager.execute_ai_turn(game, socketio)
                )
    """
    pass


if __name__ == "__main__":
    print("Module d'intégration IA chargé")
    print("Utilisez integrate_ai_player() pour ajouter une IA à une partie")
