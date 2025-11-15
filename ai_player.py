# -*- coding: utf-8 -*-

"""
Joueur IA pour le jeu Smile utilisant du Machine Learning
Architecture basée sur Deep Q-Learning (DQN)
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random
import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime


# ============================================
# 1. ENCODAGE DE L'ÉTAT DU JEU
# ============================================

class GameStateEncoder:
    """Encode l'état du jeu en vecteur numérique pour le réseau de neurones"""
    
    def __init__(self):
        # Définir les dimensions de chaque composant
        self.card_types = {
            'job': 0, 'study': 1, 'salary': 2, 'flirt': 3,
            'marriage': 4, 'child': 5, 'animal': 6, 'adultere': 7,
            'house': 8, 'travel': 9, 'hardship': 10, 'special': 11, 'other': 12
        }
        
        # Taille du vecteur d'état
        self.state_size = self._calculate_state_size()
    
    def _calculate_state_size(self) -> int:
        """Calcule la taille du vecteur d'état"""
        return (
            50 +      # Main du joueur (encodage one-hot des cartes)
            100 +     # Cartes posées (par catégorie)
            20 +      # Informations sur les autres joueurs
            10 +      # état global du jeu
            5         # Métadonnées
        )
    
    def encode_state(self, game_state: Dict) -> np.ndarray:
        """
        Encode l'état du jeu en vecteur numérique
        
        Args:
            game_state: Dictionnaire contenant l'état complet du jeu
            
        Returns:
            Vecteur numpy représentant l'état
        """
        features = []
        
        # 1. Encoder la main du joueur
        hand_features = self._encode_hand(game_state['my_hand'])
        features.extend(hand_features)
        
        # 2. Encoder les cartes posées
        played_features = self._encode_played_cards(game_state['my_played'])
        features.extend(played_features)
        
        # 3. Encoder les informations sur les adversaires
        opponents_features = self._encode_opponents(game_state['opponents'])
        features.extend(opponents_features)
        
        # 4. Encoder l'état global
        global_features = self._encode_global_state(game_state)
        features.extend(global_features)
        
        # 5. Métadonnées
        meta_features = [
            game_state['phase'] == 'draw',  # Phase de pioche
            game_state['phase'] == 'play',  # Phase de jeu
            game_state['is_my_turn'],
            game_state['skip_turns'],
            game_state['heritage']
        ]
        features.extend(meta_features)
        
        return np.array(features, dtype=np.float32)
    
    def _encode_hand(self, hand: List[Dict]) -> List[float]:
        """Encode la main du joueur"""
        features = [0.0] * 50
        
        for i, card in enumerate(hand[:10]):  # Max 10 cartes
            card_type = self.card_types.get(card['type'], 0)
            features[i * 5] = card_type / len(self.card_types)
            features[i * 5 + 1] = card.get('smiles', 0) / 5.0
            features[i * 5 + 2] = card.get('cost', 0) / 10.0
            features[i * 5 + 3] = card.get('salary', 0) / 4.0
            features[i * 5 + 4] = card.get('studies', 0) / 6.0
        
        return features
    
    def _encode_played_cards(self, played: Dict) -> List[float]:
        """Encode les cartes posées"""
        features = []
        
        categories = ['vie professionnelle', 'vie personnelle', 'acquisitions', 
                     'cartes spéciales', 'effet permanent']
        
        for category in categories:
            cards = played.get(category, [])
            # Nombre de cartes
            features.append(len(cards) / 10.0)
            # Smiles totaux
            total_smiles = sum(c.get('smiles', 0) for c in cards)
            features.append(total_smiles / 20.0)
            # Types de cartes présentes
            for card_type in ['job', 'study', 'salary', 'marriage', 'child']:
                has_type = any(c['type'] == card_type for c in cards)
                features.append(float(has_type))
        
        # Ajouter des features spécifiques
        features.append(self._has_job(played))
        features.append(self._is_married(played))
        features.append(self._count_studies(played) / 6.0)
        features.append(self._count_salaries(played) / 10.0)
        features.append(self._count_children(played) / 5.0)
        
        # Padding pour atteindre 100 features
        while len(features) < 100:
            features.append(0.0)
        
        return features[:100]
    
    def _encode_opponents(self, opponents: List[Dict]) -> List[float]:
        """Encode les informations sur les adversaires"""
        features = []
        
        for opponent in opponents[:4]:  # Max 4 adversaires
            features.append(opponent.get('hand_count', 0) / 10.0)
            features.append(opponent.get('smiles', 0) / 30.0)
            features.append(float(opponent.get('has_job', False)))
            features.append(float(opponent.get('is_married', False)))
            features.append(opponent.get('skip_turns', 0) / 3.0)
        
        # Padding
        while len(features) < 20:
            features.append(0.0)
        
        return features[:20]
    
    def _encode_global_state(self, game_state: Dict) -> List[float]:
        """Encode l'état global du jeu"""
        return [
            game_state.get('deck_count', 0) / 150.0,
            game_state.get('discard_count', 0) / 50.0,
            game_state.get('turn_number', 0) / 100.0,
            game_state.get('num_players', 2) / 5.0,
            float(game_state.get('casino_open', False)),
            float(game_state.get('arc_en_ciel_mode', False)),
            game_state.get('my_position', 0) / 30.0,
            game_state.get('leader_position', 0) / 30.0,
            game_state.get('position_diff', 0) / 20.0,
            float(game_state.get('can_win_next_turn', False))
        ]
    
    def _has_job(self, played: Dict) -> float:
        """Vérifie si le joueur a un métier"""
        vie_pro = played.get('vie professionnelle', [])
        return float(any(c['type'] == 'job' for c in vie_pro))
    
    def _is_married(self, played: Dict) -> float:
        """Vérifie si le joueur est marié"""
        vie_perso = played.get('vie personnelle', [])
        return float(any(c['type'] == 'marriage' for c in vie_perso))
    
    def _count_studies(self, played: Dict) -> int:
        """Compte le nombre d'études"""
        vie_pro = played.get('vie professionnelle', [])
        total = 0
        for card in vie_pro:
            if card['type'] == 'study':
                total += card.get('levels', 1)
        return total
    
    def _count_salaries(self, played: Dict) -> int:
        """Compte le nombre de salaires"""
        vie_pro = played.get('vie professionnelle', [])
        return sum(1 for c in vie_pro if c['type'] == 'salary')
    
    def _count_children(self, played: Dict) -> int:
        """Compte le nombre d'enfants"""
        vie_perso = played.get('vie personnelle', [])
        return sum(1 for c in vie_perso if c['type'] == 'child')


# ============================================
# 2. RÉSEAU DE NEURONES (DQN)
# ============================================

class SmileDQN(nn.Module):
    """Réseau de neurones pour le Deep Q-Learning"""
    
    def __init__(self, state_size: int, action_size: int):
        super(SmileDQN, self).__init__()
        
        # Architecture du réseau
        self.fc1 = nn.Linear(state_size, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(128, 128)
        self.fc4 = nn.Linear(128, action_size)
        
        self.dropout = nn.Dropout(0.2)
        self.batch_norm1 = nn.BatchNorm1d(256)
        self.batch_norm2 = nn.BatchNorm1d(256)
        
    def forward(self, x):
        """Forward pass"""
        x = torch.relu(self.batch_norm1(self.fc1(x)))
        x = self.dropout(x)
        x = torch.relu(self.batch_norm2(self.fc2(x)))
        x = self.dropout(x)
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        return x


# ============================================
# 3. AGENT IA
# ============================================

class SmileAIAgent:
    """Agent IA utilisant Deep Q-Learning"""
    
    def __init__(self, state_size: int, action_size: int, device: str = 'cpu'):
        self.state_size = state_size
        self.action_size = action_size
        self.device = torch.device(device)
        
        # Hyperparamètres
        self.gamma = 0.95
        self.epsilon = 0.1
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.batch_size = 64
        self.memory_size = 10000
        
        # Mémoire de replay
        self.memory = deque(maxlen=self.memory_size)
        
        # Réseaux
        self.policy_net = SmileDQN(state_size, action_size).to(self.device)
        self.target_net = SmileDQN(state_size, action_size).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        # Optimiseur
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        
        # Métriques
        self.total_steps = 0
        self.episodes_trained = 0
    
    def remember(self, state, action, reward, next_state, done):
        """Stocke une transition dans la mémoire"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state: np.ndarray, valid_actions: List[int]) -> int:
        """
        Choisit une action basée sur l'état actuel
        """
        if np.random.rand() <= self.epsilon:
            return random.choice(valid_actions)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.policy_net(state_tensor).cpu().numpy()[0]
            
            masked_q = np.full(self.action_size, -np.inf)
            masked_q[valid_actions] = q_values[valid_actions]
            
            return int(np.argmax(masked_q))
    
    def replay(self):
        """Entraîne le réseau sur un batch"""
        if len(self.memory) < self.batch_size:
            return 0.0
        
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        states = torch.FloatTensor(np.array(states)).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(np.array(next_states)).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        current_q = self.policy_net(states).gather(1, actions.unsqueeze(1))
        
        with torch.no_grad():
            next_q = self.target_net(next_states).max(1)[0]
            target_q = rewards + (1 - dones) * self.gamma * next_q
        
        loss = self.criterion(current_q.squeeze(), target_q)
        
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.total_steps += 1
        return loss.item()
    
    def update_target_network(self):
        """Met à jour le réseau cible"""
        self.target_net.load_state_dict(self.policy_net.state_dict())
    
    def save(self, filepath: str):
        """Sauvegarde le modèle"""
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'total_steps': self.total_steps,
            'episodes_trained': self.episodes_trained
        }, filepath)
        print(f"Modèle sauvegardé dans {filepath}")
    
    def load(self, filepath: str):
        """Charge le modèle"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.total_steps = checkpoint['total_steps']
        self.episodes_trained = checkpoint['episodes_trained']
        print(f"Modèle chargé depuis {filepath}")


# ============================================
# 4. GESTIONNAIRE D'ACTIONS
# ============================================

class ActionManager:
    """Gère l'encodage et le décodage des actions"""
    
    def __init__(self):
        self.action_types = {
            'draw_deck': 0,
            'draw_discard': 1,
            'play_card': 2,
            'discard_card': 12,
            'skip_turn': 22,
            'select_target': 23,
            'select_salary': 28,
        }
        
        self.action_size = 100
    
    def get_valid_actions(self, game_state: Dict) -> List[int]:
        valid_actions = []
        
        phase = game_state['phase']
        my_hand = game_state['my_hand']
        can_draw = phase == 'draw'
        can_play = phase == 'play'
        
        if can_draw:
            valid_actions.append(self.action_types['draw_deck'])
            if game_state.get('discard_count', 0) > 0:
                valid_actions.append(self.action_types['draw_discard'])
        
        if can_play:
            for i, card in enumerate(my_hand[:10]):
                if self._can_play_card(card, game_state):
                    valid_actions.append(self.action_types['play_card'] + i)
            
            for i in range(min(len(my_hand), 10)):
                valid_actions.append(self.action_types['discard_card'] + i)
        
        valid_actions.append(self.action_types['skip_turn'])
        
        return valid_actions
    
    def _can_play_card(self, card: Dict, game_state: Dict) -> bool:
        card_type = card['type']
        my_played = game_state['my_played']
        
        if card_type == 'job':
            return not self._has_job(my_played)
        elif card_type == 'study':
            return not self._has_job(my_played)
        elif card_type == 'salary':
            return self._has_job(my_played)
        elif card_type == 'marriage':
            return not self._is_married(my_played) and self._has_flirt(my_played)
        elif card_type == 'child':
            return self._is_married(my_played)
        
        return True
    
    def _has_job(self, played: Dict) -> bool:
        return any(c['type'] == 'job' for c in played.get('vie professionnelle', []))
    
    def _is_married(self, played: Dict) -> bool:
        return any(c['type'] == 'marriage' for c in played.get('vie personnelle', []))
    
    def _has_flirt(self, played: Dict) -> bool:
        return any(c['type'] == 'flirt' for c in played.get('vie personnelle', []))
    
    def decode_action(self, action_idx: int, game_state: Dict) -> Dict:
        if action_idx == self.action_types['draw_deck']:
            return {'type': 'draw', 'source': 'deck'}
        
        elif action_idx == self.action_types['draw_discard']:
            return {'type': 'draw', 'source': 'discard'}
        
        elif self.action_types['play_card'] <= action_idx < self.action_types['discard_card']:
            idx = action_idx - self.action_types['play_card']
            if idx < len(game_state['my_hand']):
                return {'type': 'play_card', 'card_id': game_state['my_hand'][idx]['id']}
        
        elif self.action_types['discard_card'] <= action_idx < self.action_types['skip_turn']:
            idx = action_idx - self.action_types['discard_card']
            if idx < len(game_state['my_hand']):
                return {'type': 'discard_card', 'card_id': game_state['my_hand'][idx]['id']}
        
        elif action_idx == self.action_types['skip_turn']:
            return {'type': 'skip_turn'}
        
        return {'type': 'invalid'}


# ============================================
# 5. FONCTION DE RÉCOMPENSE
# ============================================

class RewardCalculator:
    """Calcule les récompenses pour l'apprentissage"""
    
    @staticmethod
    def calculate_reward(prev_state: Dict, action: Dict, new_state: Dict, 
                        game_over: bool, won: bool) -> float:
        
        reward = 0.0
        
        # Fin de partie
        if game_over:
            if won:
                return 100.0
            else:
                final_position = new_state.get('final_position', 4)
                return -50.0 + (20.0 * (5 - final_position))
        
        # Gain de smiles
        diff = new_state.get('my_smiles', 0) - prev_state.get('my_smiles', 0)
        reward += diff * 2.0
        
        # Métier
        if not RewardCalculator._has_job(prev_state) and RewardCalculator._has_job(new_state):
            reward += 5.0
        
        # Mariage
        if not RewardCalculator._is_married(prev_state) and RewardCalculator._is_married(new_state):
            reward += 3.0
        
        # Enfants
        c1 = RewardCalculator._count_children(prev_state)
        c2 = RewardCalculator._count_children(new_state)
        if c2 > c1:
            reward += 2.0 * (c2 - c1)
        
        # Perte d’éléments importants
        if RewardCalculator._has_job(prev_state) and not RewardCalculator._has_job(new_state):
            reward -= 10.0
        
        if RewardCalculator._is_married(prev_state) and not RewardCalculator._is_married(new_state):
            reward -= 5.0
        
        # Proximité de la victoire
        pdiff = prev_state.get('position_diff', 0) - new_state.get('position_diff', 0)
        reward += pdiff * 0.5
        
        # Passer son tour
        if action.get('type') == 'skip_turn':
            reward -= 0.5
        
        # Coups durs reçus
        h1 = len(prev_state.get('received_hardships', []))
        h2 = len(new_state.get('received_hardships', []))
        if h2 > h1:
            reward -= 3.0 * (h2 - h1)
        
        return reward
    
    @staticmethod
    def _has_job(state: Dict) -> bool:
        return any(c['type'] == 'job' for c in state.get('my_played', {}).get('vie professionnelle', []))
    
    @staticmethod
    def _is_married(state: Dict) -> bool:
        return any(c['type'] == 'marriage' for c in state.get('my_played', {}).get('vie personnelle', []))
    
    @staticmethod
    def _count_children(state: Dict) -> int:
        return sum(1 for c in state.get('my_played', {}).get('vie personnelle', []) if c['type'] == 'child')


# ============================================
# 6. MAIN
# ============================================

if __name__ == "__main__":
    encoder = GameStateEncoder()
    action_manager = ActionManager()
    
    agent = SmileAIAgent(encoder.state_size, action_manager.action_size)
    
    print(f"Agent IA initialisé :")
    print(f"  - Taille de l'état : {encoder.state_size}")
    print(f"  - Taille de l'espace d'actions : {action_manager.action_size}")
    print(f"  - Epsilon : {agent.epsilon}")
    print(f"  - Paramètres : {sum(p.numel() for p in agent.policy_net.parameters())}")
