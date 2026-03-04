import sys
from pathlib import Path

# Ajouter le répertoire racine au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model.Player import Player

player1 = Player("Player 1")