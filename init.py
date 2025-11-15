from flask import render_template, request, send_from_directory
from flask_socketio import emit, join_room
from card_classes import *
from constants import app, socketio, games, player_sessions, get_game_state_for_player, update_all_player, CardFactory, card_builders
import random
import uuid
from datetime import datetime
import os

@app.route('/')
def index():
    print("[start] : index")
    return render_template('index.html')

@app.route('/ressources/<path:filename>')
def serve_image(filename):
    """Servir les images des cartes"""
    print("[start] : serve_image ")
    ressources_dir = os.path.join(os.path.dirname(__file__), 'ressources')
    return send_from_directory(ressources_dir, filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Servir les fichiers statiques (CSS, JS)"""
    print(f"[start] : serve_static - {filename}")
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_dir, filename)

@socketio.on('connect')
def handle_connect():
    print("[start] : handle_connect")
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print("[start] : handle_disconnect")
    print(f'Client disconnected: {request.sid}')
    if request.sid in player_sessions:
        session_info = player_sessions[request.sid]
        game_id = session_info['game_id']
        player_id = session_info['player_id']
        
        if game_id in games:
            game = games[game_id]
            if player_id < len(game.players):
                game.players[player_id].connected = False
                print("[appel] : player_disconnected")
                socketio.emit('player_disconnected', {
                    'player_id': player_id,
                    'player_name': game.players[player_id].name
                }, room=game_id)

@socketio.on('update_deck_config')
def handle_update_deck_config(data):
    """Mettre à jour la configuration du deck pendant la phase d'attente"""
    print("[start] : handle_update_deck_config")
    game_id = data.get('game_id')
    deck_config = data.get('deck_config')
    
    if game_id not in games:
        emit('error', {'message': 'Partie non trouvée'})
        return
    
    game: 'Game' = games[game_id]
    session_info = player_sessions.get(request.sid)
    
    # ✨ Vérifier que c'est l'hôte
    if not session_info or session_info['player_id'] != game.host_id:
        emit('error', {'message': 'Seul l\'hôte peut modifier le deck'})
        return
    
    # ✨ Vérifier que la partie n'a pas démarré
    if game.phase != 'waiting':
        emit('error', {'message': 'Le deck ne peut être modifié qu\'en phase d\'attente'})
        return
    
    new_deck = CardFactory.create_custom_deck(deck_config)
    random.shuffle(new_deck)
    
    # ✨ Remplacer le deck
    game.deck = new_deck
    
    print(f"Deck mis à jour: {len(game.deck)} cartes restantes")
    
    # ✨ Notifier tous les joueurs
    socketio.emit('deck_updated', {
        'message': 'Le deck a été mis à jour par l\'hôte',
        'deck_count': len(game.deck),
        'game' : game.to_dict()
    }, room=game_id)


@app.route('/api/card_rule/<card_id>')
def get_card_rule(card_id):
    if card_id in card_builders:
        try:
            card = card_builders[card_id]()
            return {
                'success': True,
                'rule': card.get_card_rule(),
                'name': getattr(card, 'name', card_id),
                'type': card.type if hasattr(card, 'type') else 'unknown',
                'image': card.image if hasattr(card, 'image') else None  # ✅ AJOUT
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    return {'success': False, 'error': 'Carte non trouvée'}, 404


@socketio.on('create_game')
def handle_create_game(data):
    """Créer une nouvelle partie multijoueur"""
    print("[start] : handle_create_game")
    num_players = data.get('num_players', 2)
    player_name = data.get('player_name', 'Joueur 1')
    
    game_id = str(uuid.uuid4())[:8]
    

    player_0 = Player(0, player_name)
    player_0.session_id = request.sid
    
    
    
    game = Game(game_id, [], num_players)
    game.add_player(player_0)


    games[game_id] = game
    player_sessions[request.sid] = {'game_id': game_id, 'player_id': 0}
    
    join_room(game_id)
    
    print(f"Partie créée: {game_id}, deck: {len(game.deck)} cartes")
    
    print("[appel] : game_created")
    emit('game_created', {
        'game_id': game_id,
        'player_id': 0,
        'game': get_game_state_for_player(game, 0)
    })

@socketio.on('join_game')
def handle_join_game(data):
    """Rejoindre une partie existante"""
    print("[start] : handle_join_game")
    game_id = data.get('game_id')
    player_name = data.get('player_name', 'Joueur')
    
    game: 'Game' = games.get(game_id)
    player_id = len(game.players)
    game.add_player(Player(player_id, player_name))
    player_sessions[request.sid] = {'game_id': game_id, 'player_id': player_id}

    join_room(game_id)
    update_all_player(game, "")

    print("[appel] game_joined")
    emit('game_joined', {
        'game_id': game_id,
        'player_id': player_id,
        'game': get_game_state_for_player(game, player_id)
    })
    
    print('[appel] : player_joined')
    socketio.emit('player_joined', {
        'player_id': player_id,
        'player_name': player_name,
        'players_joined': game.players_joined,
        'num_players': game.num_players
    }, room=game_id)

@socketio.on('start_game')
def handle_start_game(data):
    """Démarrer la partie (seulement l'hôte)"""
    print("[start] : handle_start_game")
    game_id = data.get('game_id')
    
    if game_id not in games:
        emit('error', {'message': 'Partie non trouvée'})
        return
    
    game: 'Game' = games[game_id]
    session_info = player_sessions.get(request.sid)
    
    if not session_info or session_info['player_id'] != game.host_id:
        emit('error', {'message': 'Seul l\'hôte peut démarrer la partie'})
        return
    
    if game.players_joined < 2:
        emit('error', {'message': 'Il faut au moins 2 joueurs pour commencer'})
        return
    
    game.phase = 'draw'
    # distributions des 5 cartes par joueurs
    for player in game.players:
        if player.connected:
            player.hand = [game.deck.pop() for _ in range(5)]


    # choix du joueur qui commence
    connected_players = game.players
    if connected_players:
        game.current_player = random.choice(connected_players).id
    
    print(f"Partie démarrée: {game_id}, joueur actuel: {game.current_player}")
    
    for player in game.players:
        if player.connected:
            print("[appel] : game_started")
            socketio.emit('game_started', {
                'game': get_game_state_for_player(game, player.id)
            }, room=player.session_id)
