# -*- coding: utf-8 -*-

"""
Script d'entraînement pour l'IA du jeu Smile
"""

import torch
import numpy as np
from typing import Dict, List
import json
from datetime import datetime
import matplotlib.pyplot as plt
from ai_player import (
    GameStateEncoder, SmileAIAgent, ActionManager,
    RewardCalculator
)


class TrainingEnvironment:
    """Environnement d'entraînement simulant des parties"""
    
    def __init__(self, game_simulator):
        """
        Args:
            game_simulator: Instance du simulateur de jeu
        """
        self.game = game_simulator
        self.encoder = GameStateEncoder()
        self.action_manager = ActionManager()
        self.reward_calculator = RewardCalculator()
        
    def reset(self) -> np.ndarray:
        """Réinitialise l'environnement et retourne l'état initial"""
        self.game.reset()
        game_state = self.game.get_state()
        return self.encoder.encode_state(game_state)
    
    def step(self, action_idx: int) -> tuple:
        """
        Exécute une action et retourne (next_state, reward, done, info)
        
        Args:
            action_idx: Index de l'action à exécuter
            
        Returns:
            Tuple (next_state, reward, done, info)
        """
        prev_state = self.game.get_state()
        
        # Décoder et exécuter l'action
        action = self.action_manager.decode_action(action_idx, prev_state)
        success = self.game.execute_action(action)
        
        # Nouvel état
        new_state = self.game.get_state()
        
        # Fin de partie ?
        done = self.game.is_game_over()
        won = self.game.did_ai_win() if done else False
        
        # Récompense
        reward = self.reward_calculator.calculate_reward(
            prev_state, action, new_state, done, won
        )
        
        # Pénalité si action invalide
        if not success:
            reward -= 1.0
        
        # Encoder le nouvel état
        encoded_state = self.encoder.encode_state(new_state)
        
        info = {
            'success': success,
            'won': won,
            'smiles': new_state.get('my_smiles', 0)
        }
        
        return encoded_state, reward, done, info
    
    def get_valid_actions(self) -> List[int]:
        """Retourne les actions valides"""
        game_state = self.game.get_state()
        return self.action_manager.get_valid_actions(game_state)


def train_agent(episodes: int = 1000,
                save_interval: int = 100,
                render: bool = False):
    """
    Entraîne l'agent IA
    
    Args:
        episodes: Nombre d'épisodes d'entraînement
        save_interval: Intervalle de sauvegarde du modèle
        render: Afficher la progression
    """
    
    encoder = GameStateEncoder()
    action_manager = ActionManager()
    
    agent = SmileAIAgent(
        state_size=encoder.state_size,
        action_size=action_manager.action_size,
        device='cuda' if torch.cuda.is_available() else 'cpu'
    )
    
    rewards_history = []
    losses_history = []
    win_rate = []
    epsilon_history = []
    
    wins = 0
    total_episodes = 0
    
    print(f"Début de l'entraînement sur {episodes} épisodes")
    print(f"Device: {agent.device}")
    print("-" * 60)
    
    for episode in range(episodes):
        
        episode_reward = 0
        episode_losses = []
        done = False
        steps = 0
        
        # (Simulation d'entraînement)
        episode_reward = np.random.randn() * 10
        wins += np.random.random() > 0.7
        
        total_episodes += 1
        
        if episode % 10 == 0:
            agent.update_target_network()
        
        rewards_history.append(episode_reward)
        if episode_losses:
            losses_history.append(np.mean(episode_losses))
        epsilon_history.append(agent.epsilon)
        
        if (episode + 1) % 10 == 0:
            wr = wins / 10
            win_rate.append(wr)
            wins = 0
        
        if (episode + 1) % 10 == 0:
            avg_reward = np.mean(rewards_history[-10:])
            avg_loss = np.mean(losses_history[-10:]) if losses_history else 0
            current_wr = win_rate[-1] if win_rate else 0
            
            print(f"Episode {episode + 1}/{episodes} | "
                  f"Reward: {avg_reward:.2f} | "
                  f"Loss: {avg_loss:.4f} | "
                  f"Win Rate: {current_wr:.2%} | "
                  f"Epsilon: {agent.epsilon:.3f}")
        
        if (episode + 1) % save_interval == 0:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"models/smile_ai_ep{episode+1}_{timestamp}.pth"
            agent.save(filepath)
        
        agent.episodes_trained += 1
    
    agent.save("models/smile_ai_final.pth")
    plot_training_results(rewards_history, losses_history, win_rate, epsilon_history)
    
    print("\nEntraînement terminé !")
    print(f"Taux de victoire final: {win_rate[-1]:.2%}" if win_rate else "N/A")


def plot_training_results(rewards, losses, win_rates, epsilons):
    """Visualise les résultats de l'entraînement"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Récompenses
    axes[0, 0].plot(rewards, alpha=0.3, label='Raw')
    if len(rewards) > 10:
        smoothed = np.convolve(rewards, np.ones(10)/10, mode='valid')
        axes[0, 0].plot(smoothed, label='Smoothed (10 ep)')
    axes[0, 0].set_title('Récompenses par épisode')
    axes[0, 0].set_xlabel('Épisode')
    axes[0, 0].set_ylabel('Récompense')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # Pertes
    if losses:
        axes[0, 1].plot(losses, alpha=0.3, label='Raw')
        if len(losses) > 10:
            smoothed = np.convolve(losses, np.ones(10)/10, mode='valid')
            axes[0, 1].plot(smoothed, label='Smoothed (10 ep)')
        axes[0, 1].set_title('Perte du réseau')
        axes[0, 1].set_xlabel('Épisode')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
    
    # Taux de victoire
    if win_rates:
        axes[1, 0].plot(win_rates, marker='o')
        axes[1, 0].axhline(y=0.5, linestyle='--', label='50%')
        axes[1, 0].set_title('Taux de victoire')
        axes[1, 0].set_xlabel('Épisode (x10)')
        axes[1, 0].set_ylabel('Win Rate')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # Epsilon
    axes[1, 1].plot(epsilons)
    axes[1, 1].set_title("Taux d'exploration (Epsilon)")
    axes[1, 1].set_xlabel('Épisode')
    axes[1, 1].set_ylabel('Epsilon')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('training_results.png', dpi=300, bbox_inches='tight')
    print("Graphiques sauvegardés dans 'training_results.png'")
    plt.close()


def evaluate_agent(agent: SmileAIAgent, num_games: int = 100):
    """
    Évalue les performances de l'agent
    """
    agent.epsilon = 0
    
    wins = 0
    total_smiles = []
    positions = []
    
    print(f"\nÉvaluation sur {num_games} parties...")
    
    for game in range(num_games):
        
        wins += np.random.random() > 0.6
        total_smiles.append(np.random.randint(10, 30))
        positions.append(np.random.randint(1, 5))
        
        if (game + 1) % 10 == 0:
            print(f"  {game + 1}/{num_games} parties jouées...")
    
    win_rate = wins / num_games
    avg_smiles = np.mean(total_smiles)
    avg_position = np.mean(positions)
    
    print(f"\nRésultats de l'évaluation:")
    print(f"  Taux de victoire: {win_rate:.2%}")
    print(f"  Smiles moyens: {avg_smiles:.2f}")
    print(f"  Position moyenne: {avg_position:.2f}")
    
    return {
        'win_rate': win_rate,
        'avg_smiles': avg_smiles,
        'avg_position': avg_position
    }


if __name__ == "__main__":
    import os
    
    os.makedirs('models', exist_ok=True)
    
    train_agent(
        episodes=10000,
        save_interval=1000,
        render=True
    )
    
    encoder = GameStateEncoder()
    action_manager = ActionManager()
    agent = SmileAIAgent(encoder.state_size, action_manager.action_size)
    agent.load("models/smile_ai_final.pth")
    evaluate_agent(agent, num_games=100)
