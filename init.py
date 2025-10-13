from flask import render_template, request
from flask_socketio import emit, join_room
from card_classes import Card, Player, CardFactory, HardshipCard, JobCard, StudyCard, SalaryCard, MarriageCard, AdulteryCard, HouseCard, TravelCard, ChildCard, SpecialCard, FlirtCard
from constants import app, socketio, games, player_sessions, get_game_state_for_player, apply_hardship_effect, check_game
import random
import uuid
from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    if request.sid in player_sessions:
        session_info = player_sessions[request.sid]
        game_id = session_info['game_id']
        player_id = session_info['player_id']
        
        if game_id in games:
            game = games[game_id]
            if player_id < len(game['players']):
                game['players'][player_id].connected = False
                socketio.emit('player_disconnected', {
                    'player_id': player_id,
                    'player_name': game['players'][player_id].name
                }, room=game_id)

@socketio.on('create_game')
def handle_create_game(data):
    """Créer une nouvelle partie multijoueur"""
    num_players = data.get('num_players', 2)
    player_name = data.get('player_name', 'Joueur 1')
    
    game_id = str(uuid.uuid4())[:8]
    deck = CardFactory.create_deck()
    print(f"Deck créé avec {len(deck)} cartes")
    random.shuffle(deck)
    
    ##################
    # TESTS affichage des cartes
    ##################
    # cards_distribution = ""
    # invert_deck = deck[::-1]
    # for i in range(len(deck)):
    #     cards_distribution += f"{i} : {str(invert_deck[i])} - {invert_deck[i].id}\n"
    # with open("distribution.txt", 'w') as file:
    #     file.write(cards_distribution)
    #################


    player_0 = Player(0, player_name)
    player_0.hand = [deck.pop() for _ in range(5)]
    player_0.session_id = request.sid
    
    players = [player_0]
    
    for i in range(1, num_players):
        player = Player(i, 'En attente...')
        player.connected = False
        players.append(player)
    
    game = {
        'id': game_id,
        'players': players,
        'deck': deck,
        'discard': [],
        'current_player': 0,
        'casino': {
            'open': False,
            'first_bet': None,
            'second_bet': None
        },
        'phase': 'waiting',
        'num_players': num_players,
        'players_joined': 1,
        'created_at': datetime.now().isoformat(),
        'host_id': 0,
        'pending_hardship': None,
        'pending_special': None
    }
    
    games[game_id] = game
    player_sessions[request.sid] = {'game_id': game_id, 'player_id': 0}
    
    join_room(game_id)
    
    print(f"Partie créée: {game_id}, deck: {len(game['deck'])} cartes")
    
    emit('game_created', {
        'game_id': game_id,
        'player_id': 0,
        'game': get_game_state_for_player(game, 0)
    })

@socketio.on('join_game')
def handle_join_game(data):
    """Rejoindre une partie existante"""
    game_id = data.get('game_id')
    player_name = data.get('player_name', 'Joueur')
    
    if game_id not in games:
        emit('error', {'message': 'Partie non trouvée'})
        return
    
    game = games[game_id]
    
    if game['phase'] != 'waiting':
        emit('error', {'message': 'La partie a déjà commencé'})
        return
    
    player_id = None
    for i, player in enumerate(game['players']):
        if not player.connected:
            player_id = i
            break
    
    if player_id is None:
        emit('error', {'message': 'La partie est complète'})
        return
    
    player = game['players'][player_id]
    player.name = player_name
    player.hand = [game['deck'].pop() for _ in range(5)]
    player.connected = True
    player.session_id = request.sid
    game['players_joined'] += 1
    
    player_sessions[request.sid] = {'game_id': game_id, 'player_id': player_id}
    join_room(game_id)
    
    emit('game_joined', {
        'game_id': game_id,
        'player_id': player_id,
        'game': get_game_state_for_player(game, player_id)
    })
    
    socketio.emit('player_joined', {
        'player_id': player_id,
        'player_name': player_name,
        'players_joined': game['players_joined'],
        'num_players': game['num_players']
    }, room=game_id)

@socketio.on('start_game')
def handle_start_game(data):
    """Démarrer la partie (seulement l'hôte)"""
    game_id = data.get('game_id')
    
    if game_id not in games:
        emit('error', {'message': 'Partie non trouvée'})
        return
    
    game = games[game_id]
    session_info = player_sessions.get(request.sid)
    
    if not session_info or session_info['player_id'] != game['host_id']:
        emit('error', {'message': 'Seul l\'hôte peut démarrer la partie'})
        return
    
    if game['players_joined'] < 2:
        emit('error', {'message': 'Il faut au moins 2 joueurs pour commencer'})
        return
    
    game['phase'] = 'draw'
    
    connected_players = [i for i, p in enumerate(game['players']) if p.connected]
    if connected_players:
        game['current_player'] = random.choice(connected_players)
    
    print(f"Partie démarrée: {game_id}, joueur actuel: {game['current_player']}")
    
    for player in game['players']:
        if player.connected:
            socketio.emit('game_started', {
                'game': get_game_state_for_player(game, player.id)
            }, room=player.session_id)
