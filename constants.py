from flask import Flask, request
from flask_socketio import SocketIO, emit
from card_classes import *
import os

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici_changez_la'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration pour servir les images
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'ressources')

# Stockage des parties et des joueurs connectés
games = {}
player_sessions = {}  # {session_id: {game_id, player_id}}


def get_game_state_for_player(game: Game , player_id):
    """Retourne l'état du jeu adapté pour un joueur spécifique"""
    print("[start] : get_game_state_for_player")
    game_state = game.to_dict()
    # Remplacer le deck complet par juste le nombre de cartes
    game_state['deck_count'] = len(game.deck)
    game_state.pop('deck', None)  # Retirer la liste complète du deck
    
    # ✅ FIX: Convertir la défausse en dictionnaires
    if 'discard' in game_state and game_state['discard']:
        game_state['discard'] = [card.to_dict() if hasattr(card, 'to_dict') else card 
                                  for card in game.discard]
    
    # Ajouter la dernière carte défaussée si elle existe
    if len(game.discard) > 0:
        last_card = game.discard[-1]
        game_state["last_discard"] = last_card.to_dict() if hasattr(last_card, 'to_dict') else last_card
    else:
        game_state['last_discard'] = None

    return game_state

def check_game():
    print("[start]: check_game")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        emit('error', {'message': 'Session non trouvée'})
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    
    if game_id not in games:
        emit('error', {'message': 'Partie non trouvée'})
        return
    
    game: Game = games[game_id]
    return game.current_player, game, game_id

def update_all_player(game: Game, message):
    """Fonction legacy - redirige vers la méthode de la classe Game"""
    print("[start]: update_all_player (legacy)")
    game.broadcast_update(message)


def get_card_by_id(card_id, deck: list[Card]):
    """récupère une carte dans le deck par son id"""
    print("[start]: get_card_by_id")
    researched_card = None
    for card in deck:
        if card.id == card_id:
            researched_card = card
            break

    if not researched_card:
        emit('error', {'message': 'Carte non trouvée', "debug": "get_card_by_id"})
    return researched_card