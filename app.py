from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici_changez_la'
socketio = SocketIO(app, cors_allowed_origins="*")

# Définition des métiers
JOBS = {
    'architecte': {'salary': 3, 'studies': 4, 'status': 'rien', 'power': 'house_free'},
    'astronaute': {'salary': 4, 'studies': 6, 'status': 'rien', 'power': 'discard_pick'},
    'avocat': {'salary': 3, 'studies': 4, 'status': 'rien', 'power': 'no_divorce'},
    'bandit': {'salary': 4, 'studies': 0, 'status': 'rien', 'power': 'no_fire_tax'},
    'barman': {'salary': 1, 'studies': 0, 'status': 'intérimaire', 'power': 'unlimited_flirt'},
    'chef des ventes': {'salary': 3, 'studies': 3, 'status': 'rien', 'power': 'salary_discard'},
    'chef des achats': {'salary': 3, 'studies': 3, 'status': 'rien', 'power': 'acquisition_discard'},
    'chercheur': {'salary': 2, 'studies': 6, 'status': 'rien', 'power': 'extra_card'},
    'chirurgien': {'salary': 4, 'studies': 6, 'status': 'rien', 'power': 'no_illness_extra_study'},
    'designer': {'salary': 3, 'studies': 4, 'status': 'rien', 'power': 'none'},
    'ecrivain': {'salary': 1, 'studies': 0, 'status': 'rien', 'power': 'prix_possible'},
    'garagiste': {'salary': 2, 'studies': 1, 'status': 'rien', 'power': 'no_accident'},
    'gourou': {'salary': 3, 'studies': 0, 'status': 'rien', 'power': 'none'},
    'jardinier': {'salary': 1, 'studies': 1, 'status': 'rien', 'power': 'none'},
    'journaliste': {'salary': 2, 'studies': 3, 'status': 'rien', 'power': 'see_hands_prix_possible'},
    'médecin': {'salary': 4, 'studies': 6, 'status': 'rien', 'power': 'no_illness_extra_study'},
    'médium': {'salary': 1, 'studies': 0, 'status': 'rien', 'power': 'see_deck'},
    'militaire': {'salary': 1, 'studies': 0, 'status': 'fonctionnaire', 'power': 'no_attentat'},
    'pharmacien': {'salary': 3, 'studies': 5, 'status': 'rien', 'power': 'no_illness'},
    'pilote de ligne': {'salary': 4, 'studies': 5, 'status': 'rien', 'power': 'travel_free'},
    'pizzaiolo': {'salary': 2, 'studies': 0, 'status': 'rien', 'power': 'none'},
    'plombier': {'salary': 1, 'studies': 1, 'status': 'intérimaire', 'power': 'none'},
    'policier': {'salary': 1, 'studies': 1, 'status': 'fonctionnaire', 'power': 'block_bandit_gourou'},
    'prof anglais': {'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none'},
    'prof francais': {'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none'},
    'prof histoire': {'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none'},
    'prof maths': {'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none'},
    'serveur': {'salary': 1, 'studies': 0, 'status': 'intérimaire', 'power': 'none'},
    'stripteaser': {'salary': 1, 'studies': 0, 'status': 'intérimaire', 'power': 'none'},
    'grand prof': {'salary': 3, 'studies': 'P', 'status': 'fonctionnaire', 'power': 'none'}
}

FLIRT_LOCATIONS = ['bar', 'boite de nuit', 'camping', 'cinema', 'hotel', 'internet', 'parc', 'restaurant', 'theatre', 'zoo']
MARRIAGE_LOCATIONS = ['corps-nuds', 'montcuq', 'monteton', 'Sainte-Vierge', 'Fourqueux', 'Fourqueux', 'Fourqueux']
CHILDREN_NAMES = ['diana', 'harry', 'hermionne', 'lara', 'leia', 'luigi', 'luke', 'mario', 'rocky', 'zelda']
ANIMALS = [
    {'name': 'chat', 'smiles': 1},
    {'name': 'chien', 'smiles': 1},
    {'name': 'lapin', 'smiles': 1},
    {'name': 'licorne', 'smiles': 3},
    {'name': 'poussin', 'smiles': 1}
]

# Stockage des parties et des joueurs connectés
games = {}
player_sessions = {}  # {session_id: {game_id, player_id}}

def create_deck():
    """Crée un deck complet de cartes"""
    deck = []
    
    # Métiers
    for job in JOBS.keys():
        deck.append({'type': 'job', 'subtype': job, 'smiles': 2, 'id': str(uuid.uuid4())})
    
    # Études
    for _ in range(22):
        deck.append({'type': 'study', 'subtype': 'simple', 'smiles': 1, 'levels': 1, 'id': str(uuid.uuid4())})
    for _ in range(3):
        deck.append({'type': 'study', 'subtype': 'double', 'smiles': 1, 'levels': 2, 'id': str(uuid.uuid4())})
    
    # Salaires
    for level in range(1, 5):
        for _ in range(10):
            deck.append({'type': 'salary', 'subtype': level, 'smiles': level, 'id': str(uuid.uuid4())})
    
    # Flirts
    for loc in FLIRT_LOCATIONS:
        deck.append({'type': 'flirt', 'subtype': loc, 'smiles': 1, 'id': str(uuid.uuid4())})
        deck.append({'type': 'flirt', 'subtype': loc, 'smiles': 1, 'id': str(uuid.uuid4())})
    
    # Mariages
    for loc in MARRIAGE_LOCATIONS:
        deck.append({'type': 'marriage', 'subtype': loc, 'smiles': 3, 'id': str(uuid.uuid4())})
    
    # Adultères
    for _ in range(3):
        deck.append({'type': 'adultere', 'smiles': 1, 'id': str(uuid.uuid4())})
    
    # Enfants
    for name in CHILDREN_NAMES:
        deck.append({'type': 'child', 'subtype': name, 'smiles': 2, 'id': str(uuid.uuid4())})
    
    # Animaux
    for animal in ANIMALS:
        deck.append({'type': 'animal', 'subtype': animal['name'], 'smiles': animal['smiles'], 'id': str(uuid.uuid4())})
    
    # Maisons
    deck.append({'type': 'house', 'subtype': 'petite', 'cost': 6, 'smiles': 1, 'id': str(uuid.uuid4())})
    deck.append({'type': 'house', 'subtype': 'petite', 'cost': 6, 'smiles': 1, 'id': str(uuid.uuid4())})
    deck.append({'type': 'house', 'subtype': 'moyenne', 'cost': 8, 'smiles': 2, 'id': str(uuid.uuid4())})
    deck.append({'type': 'house', 'subtype': 'moyenne', 'cost': 8, 'smiles': 2, 'id': str(uuid.uuid4())})
    deck.append({'type': 'house', 'subtype': 'grande', 'cost': 10, 'smiles': 3, 'id': str(uuid.uuid4())})
    
    # Voyages
    for _ in range(5):
        deck.append({'type': 'travel', 'cost': 3, 'smiles': 1, 'id': str(uuid.uuid4())})
    
    # Cartes spéciales
    for special in ['anniversaire', 'arc en ciel', 'casino', 'chance', 'etoile filante', 'heritage', 'piston', 'troc', 'tsunami', 'vengeance']:
        deck.append({'type': 'special', 'subtype': special, 'smiles': 0, 'id': str(uuid.uuid4())})
    
    # Coups durs
    for _ in range(5):
        deck.append({'type': 'hardship', 'subtype': 'accident', 'id': str(uuid.uuid4())})
        deck.append({'type': 'hardship', 'subtype': 'burnout', 'id': str(uuid.uuid4())})
        deck.append({'type': 'hardship', 'subtype': 'divorce', 'id': str(uuid.uuid4())})
        deck.append({'type': 'hardship', 'subtype': 'impot', 'id': str(uuid.uuid4())})
        deck.append({'type': 'hardship', 'subtype': 'licenciement', 'id': str(uuid.uuid4())})
        deck.append({'type': 'hardship', 'subtype': 'maladie', 'id': str(uuid.uuid4())})
        deck.append({'type': 'hardship', 'subtype': 'redoublement', 'id': str(uuid.uuid4())})
    
    deck.append({'type': 'hardship', 'subtype': 'prison', 'id': str(uuid.uuid4())})
    deck.append({'type': 'hardship', 'subtype': 'attentat', 'id': str(uuid.uuid4())})
    
    # Autres
    deck.append({'type': 'other', 'subtype': 'legion', 'smiles': 3, 'id': str(uuid.uuid4())})
    deck.append({'type': 'other', 'subtype': 'prix', 'smiles': 4, 'id': str(uuid.uuid4())})
    deck.append({'type': 'other', 'subtype': 'prix', 'smiles': 4, 'id': str(uuid.uuid4())})
    
    return deck

def calculate_smiles(player):
    """Calcule le total de smiles d'un joueur"""
    total = sum(card.get('smiles', 0) for card in player['played'])
    
    # Bonus licorne
    has_licorne = any(c['type'] == 'animal' and c['subtype'] == 'licorne' for c in player['played'])
    has_arc = any(c['type'] == 'special' and c['subtype'] == 'arc en ciel' for c in player['played'])
    has_etoile = any(c['type'] == 'special' and c['subtype'] == 'etoile filante' for c in player['played'])
    
    if has_licorne and has_arc and has_etoile:
        total += 3
    
    return total

def get_game_state_for_player(game, player_id):
    """Retourne l'état du jeu adapté pour un joueur spécifique"""
    game_copy = game.copy()
    
    # Masquer les mains des autres joueurs
    players_copy = []
    for i, player in enumerate(game['players']):
        player_data = player.copy()
        if i != player_id:
            # Ne pas envoyer la main complète des autres joueurs
            player_data['hand_count'] = len(player['hand'])
            player_data['hand'] = []
        players_copy.append(player_data)
    
    game_copy['players'] = players_copy
    game_copy['your_player_id'] = player_id
    
    return game_copy

@app.route('/')
def index():
    return render_template('index.html')

# WebSocket events
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
                game['players'][player_id]['connected'] = False
                socketio.emit('player_disconnected', {
                    'player_id': player_id,
                    'player_name': game['players'][player_id]['name']
                }, room=game_id)

@socketio.on('create_game')
def handle_create_game(data):
    """Créer une nouvelle partie multijoueur"""
    num_players = data.get('num_players', 2)
    player_name = data.get('player_name', 'Joueur 1')
    
    game_id = str(uuid.uuid4())[:8]  # Code court pour la partie
    deck = create_deck()
    random.shuffle(deck)
    
    # Créer le premier joueur (l'hôte)
    players = [{
        'id': 0,
        'name': player_name,
        'hand': [deck.pop() for _ in range(5)],
        'played': [],
        'skip_turns': 0,
        'has_been_bandit': False,
        'heritage': 0,
        'received_hardships': [],
        'connected': True,
        'session_id': request.sid
    }]
    
    # Ajouter des slots vides pour les autres joueurs
    for i in range(1, num_players):
        players.append({
            'id': i,
            'name': f'En attente...',
            'hand': [],
            'played': [],
            'skip_turns': 0,
            'has_been_bandit': False,
            'heritage': 0,
            'received_hardships': [],
            'connected': False,
            'session_id': None
        })
    
    game = {
        'id': game_id,
        'players': players,
        'deck': deck,
        'discard': [],
        'current_player': 0,
        'casino': None,
        'phase': 'waiting',  # waiting, playing
        'num_players': num_players,
        'players_joined': 1,
        'created_at': datetime.now().isoformat(),
        'host_id': 0
    }
    
    games[game_id] = game
    player_sessions[request.sid] = {'game_id': game_id, 'player_id': 0}
    
    join_room(game_id)
    
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
    
    # Trouver un slot libre
    player_id = None
    for i, player in enumerate(game['players']):
        if not player['connected']:
            player_id = i
            break
    
    if player_id is None:
        emit('error', {'message': 'La partie est complète'})
        return
    
    # Configurer le joueur
    game['players'][player_id]['name'] = player_name
    game['players'][player_id]['hand'] = [game['deck'].pop() for _ in range(5)]
    game['players'][player_id]['connected'] = True
    game['players'][player_id]['session_id'] = request.sid
    game['players_joined'] += 1
    
    player_sessions[request.sid] = {'game_id': game_id, 'player_id': player_id}
    join_room(game_id)
    
    emit('game_joined', {
        'game_id': game_id,
        'player_id': player_id,
        'game': get_game_state_for_player(game, player_id)
    })
    
    # Notifier tous les joueurs
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
    game['current_player'] = random.randint(0, game['players_joined'] - 1)
    
    # Envoyer l'état du jeu à chaque joueur
    for player in game['players']:
        if player['connected']:
            socketio.emit('game_started', {
                'game': get_game_state_for_player(game, player['id'])
            }, room=player['session_id'])

@socketio.on('draw_card')
def handle_draw_card(data):
    """Piocher une carte"""
    source = data.get('source', 'deck')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        emit('error', {'message': 'Session non trouvée'})
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    
    if game_id not in games:
        emit('error', {'message': 'Partie non trouvée'})
        return
    
    game = games[game_id]
    
    if game['current_player'] != player_id:
        emit('error', {'message': 'Ce n\'est pas votre tour'})
        return
    
    player = game['players'][player_id]
    
    if source == 'deck':
        if not game['deck']:
            # Fin de partie
            scores = [(p['name'], calculate_smiles(p), p['id']) for p in game['players'] if p['connected']]
            scores.sort(key=lambda x: x[1], reverse=True)
            socketio.emit('game_over', {'scores': scores}, room=game_id)
            return
        
        card = game['deck'].pop()
        player['hand'].append(card)
        game['phase'] = 'play'
        
    elif source == 'discard':
        if not game['discard']:
            emit('error', {'message': 'Défausse vide'})
            return
        
        card = game['discard'].pop()
        player['played'].append(card)
        game['phase'] = 'draw'
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
        
        # Passer les joueurs déconnectés
        while not game['players'][game['current_player']]['connected']:
            game['current_player'] = (game['current_player'] + 1) % game['num_players']
    
    # Envoyer la mise à jour à tous les joueurs
    for p in game['players']:
        if p['connected']:
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p['id'])
            }, room=p['session_id'])

@socketio.on('play_card')
def handle_play_card(data):
    """Jouer une carte"""
    card_id = data.get('card_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        emit('error', {'message': 'Session non trouvée'})
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    
    if game_id not in games:
        emit('error', {'message': 'Partie non trouvée'})
        return
    
    game = games[game_id]
    
    if game['current_player'] != player_id:
        emit('error', {'message': 'Ce n\'est pas votre tour'})
        return
    
    if game['phase'] != 'play':
        emit('error', {'message': 'Vous devez d\'abord piocher'})
        return
    
    player = game['players'][player_id]
    #########
    # effectue la vérification de si il peut jouer la carte ou non



    ####
    # Trouver la carte
    card = next((c for c in player['hand'] if c['id'] == card_id), None)
    if not card:
        emit('error', {'message': 'Carte non trouvée'})
        return
    
    # Retirer la carte de la main
    player['hand'] = [c for c in player['hand'] if c['id'] != card_id]
    
    # Ajouter aux cartes jouées
    player['played'].append(card)
    
    # Changer de phase et de joueur
    game['phase'] = 'draw'
    game['current_player'] = (game['current_player'] + 1) % game['num_players']
    
    # Passer les joueurs déconnectés
    while not game['players'][game['current_player']]['connected']:
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
    
    # Envoyer la mise à jour à tous les joueurs
    for p in game['players']:
        if p['connected']:
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p['id'])
            }, room=p['session_id'])

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)