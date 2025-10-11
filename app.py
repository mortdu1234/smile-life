from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import uuid
from datetime import datetime
from card_classes import Card, Player, CardFactory, HardshipCard, JobCard, StudyCard, SalaryCard, MarriageCard

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_ici_changez_la'
socketio = SocketIO(app, cors_allowed_origins="*")

# Stockage des parties et des joueurs connectés
games = {}
player_sessions = {}  # {session_id: {game_id, player_id}}

def get_game_state_for_player(game, player_id):
    """Retourne l'état du jeu adapté pour un joueur spécifique"""
    game_state = {
        'id': game['id'],
        'players': [
            player.to_dict(hide_hand=(i != player_id)) 
            for i, player in enumerate(game['players'])
        ],
        'deck_count': len(game['deck']),
        'discard': [card.to_dict() for card in game['discard']],
        'current_player': game['current_player'],
        'casino': game['casino'].to_dict() if game['casino'] else None,
        'phase': game['phase'],
        'num_players': game['num_players'],
        'players_joined': game['players_joined'],
        'your_player_id': player_id,
        'pending_hardship': game.get('pending_hardship')
    }
    print(f"État du jeu pour joueur {player_id}: deck={game_state['deck_count']}, discard={len(game_state['discard'])}, phase={game_state['phase']}")
    return game_state

def apply_hardship_effect(game, hardship_card, target_player):
    """Applique l'effet d'une carte malus sur un joueur cible"""
    hardship_type = hardship_card.hardship_type
    
    # Vérifier les immunités
    job = target_player.get_job()
    if job:
        immunities = {
            'accident': ['no_accident'],
            'maladie': ['no_illness', 'no_illness_extra_study'],
            'attentat': ['no_attentat'],
            'divorce': ['no_divorce'],
            'licenciement': ['no_fire_tax'],
            'impot': ['no_fire_tax']
        }
        
        if hardship_type in immunities:
            if job.power in immunities[hardship_type]:
                return False, f"{target_player.name} est protégé par son métier ({job.job_name})"
    
    # Appliquer les effets
    if hardship_type == 'accident':
        # Retirer une carte voyage si présente
        travel_cards = [c for c in target_player.played if c.to_dict()['type'] == 'travel']
        if travel_cards:
            target_player.played.remove(travel_cards[0])
            return True, f"{target_player.name} a perdu un voyage"
        return True, f"{target_player.name} n'avait pas de voyage à perdre"
    
    elif hardship_type == 'burnout':
        # Passe 2 tours
        target_player.skip_turns = 2
        return True, f"{target_player.name} doit passer 2 tours"
    
    elif hardship_type == 'divorce':
        # Retirer le mariage
        marriage_cards = [c for c in target_player.played if isinstance(c, MarriageCard)]
        if marriage_cards:
            target_player.played.remove(marriage_cards[0])
            return True, f"{target_player.name} a divorcé"
        return False, f"{target_player.name} n'est pas marié"
    
    elif hardship_type == 'impot':
        # Retirer 2 salaires
        salary_cards = [c for c in target_player.played if isinstance(c, SalaryCard)]
        removed = 0
        for _ in range(min(2, len(salary_cards))):
            target_player.played.remove(salary_cards[removed])
            removed += 1
        return True, f"{target_player.name} a perdu {removed} salaire(s)"
    
    elif hardship_type == 'licenciement':
        # Retirer le métier
        job_card = target_player.get_job()
        if job_card:
            target_player.played = [c for c in target_player.played if not isinstance(c, JobCard)]
            # Chômage: retirer aussi tous les salaires
            target_player.played = [c for c in target_player.played if not isinstance(c, SalaryCard)]
            return True, f"{target_player.name} a été licencié"
        return False, f"{target_player.name} n'a pas de métier"
    
    elif hardship_type == 'maladie':
        # Passe 1 tour et perd 1 salaire
        target_player.skip_turns = 1
        salary_cards = [c for c in target_player.played if isinstance(c, SalaryCard)]
        if salary_cards:
            target_player.played.remove(salary_cards[0])
        return True, f"{target_player.name} est malade (passe 1 tour et perd 1 salaire)"
    
    elif hardship_type == 'redoublement':
        # Retirer une carte étude
        study_cards = [c for c in target_player.played if isinstance(c, StudyCard)]
        if study_cards:
            target_player.played.remove(study_cards[0])
            return True, f"{target_player.name} a perdu une étude"
        return False, f"{target_player.name} n'a pas d'études à perdre"
    
    elif hardship_type == 'prison':
        # Passe 3 tours
        target_player.skip_turns = 3
        return True, f"{target_player.name} est en prison pour 3 tours"
    
    elif hardship_type == 'attentat':
        # Retirer toutes les cartes posées
        cards_count = len(target_player.played)
        target_player.played = []
        return True, f"{target_player.name} a tout perdu ({cards_count} cartes)"
    
    return True, f"Malus {hardship_type} appliqué à {target_player.name}"

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
        'casino': None,
        'phase': 'waiting',
        'num_players': num_players,
        'players_joined': 1,
        'created_at': datetime.now().isoformat(),
        'host_id': 0,
        'pending_hardship': None
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
    
    if game['phase'] != 'draw':
        emit('error', {'message': 'Vous avez déjà pioché'})
        return
    
    player = game['players'][player_id]
    
    # Vérifier si le joueur doit passer son tour
    if player.skip_turns > 0:
        player.skip_turns -= 1
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
        
        attempts = 0
        while not game['players'][game['current_player']].connected and attempts < game['num_players']:
            game['current_player'] = (game['current_player'] + 1) % game['num_players']
            attempts += 1
        
        for p in game['players']:
            if p.connected:
                socketio.emit('game_updated', {
                    'game': get_game_state_for_player(game, p.id),
                    'message': f"{player.name} passe son tour ({player.skip_turns + 1} tours restants)"
                }, room=p.session_id)
        return
    
    if source == 'deck':
        if not game['deck']:
            scores = [(p.name, p.calculate_smiles(), p.id) for p in game['players'] if p.connected]
            scores.sort(key=lambda x: x[1], reverse=True)
            socketio.emit('game_over', {'scores': scores}, room=game_id)
            return
        
        card = game['deck'].pop()
        player.hand.append(card)
        game['phase'] = 'play'
        
        print(f"Joueur {player_id} a pioché dans le deck, reste {len(game['deck'])} cartes")
        
    elif source == 'discard':
        if not game['discard']:
            emit('error', {'message': 'Défausse vide'})
            return
        
        card = game['discard'].pop()
        player.played.append(card)
        game['phase'] = 'draw'
        
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
        
        attempts = 0
        while not game['players'][game['current_player']].connected and attempts < game['num_players']:
            game['current_player'] = (game['current_player'] + 1) % game['num_players']
            attempts += 1
    
    for p in game['players']:
        if p.connected:
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p.id)
            }, room=p.session_id)

@socketio.on('play_card')
def handle_play_card(data):
    """Jouer une carte"""
    card_id = data.get('card_id')
    target_player_id = data.get('target_player_id')
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
    
    card = None
    for c in player.hand:
        if c.id == card_id:
            card = c
            break
    
    if not card:
        emit('error', {'message': 'Carte non trouvée'})
        return
    
    # Cas spécial: carte malus
    if isinstance(card, HardshipCard):
        if target_player_id is None:
            # Demander de choisir une cible
            game['pending_hardship'] = {
                'card_id': card_id,
                'player_id': player_id
            }
            
            for p in game['players']:
                if p.connected:
                    socketio.emit('select_hardship_target', {
                        'card': card.to_dict(),
                        'available_targets': [
                            {'id': i, 'name': p.name} 
                            for i, p in enumerate(game['players']) 
                            if p.connected and i != player_id
                        ]
                    }, room=p.session_id if p.id == player_id else None)
            return
        else:
            # Appliquer le malus
            target_player = game['players'][target_player_id]
            success, message = apply_hardship_effect(game, card, target_player)
            
            player.hand.remove(card)
            
            if success:
                target_player.received_hardships.append(card.hardship_type)
            
            game['discard'].append(card)
            game['pending_hardship'] = None
            
            # Passer au joueur suivant
            game['phase'] = 'draw'
            game['current_player'] = (game['current_player'] + 1) % game['num_players']
            
            attempts = 0
            while not game['players'][game['current_player']].connected and attempts < game['num_players']:
                game['current_player'] = (game['current_player'] + 1) % game['num_players']
                attempts += 1
            
            for p in game['players']:
                if p.connected:
                    socketio.emit('game_updated', {
                        'game': get_game_state_for_player(game, p.id),
                        'message': message
                    }, room=p.session_id)
            return
    
    # Carte normale
    can_play, error_message = card.can_be_played(player)
    if not can_play:
        emit('error', {'message': error_message})
        return
    
    player.hand.remove(card)
    player.played.append(card)
    
    game['phase'] = 'draw'
    game['current_player'] = (game['current_player'] + 1) % game['num_players']
    
    attempts = 0
    while not game['players'][game['current_player']].connected and attempts < game['num_players']:
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
        attempts += 1
    
    for p in game['players']:
        if p.connected:
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p.id)
            }, room=p.session_id)

@socketio.on('discard_card')
def handle_discard_card(data):
    """Défausser une carte"""
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
    
    card = None
    for c in player.hand:
        if c.id == card_id:
            card = c
            break
    
    if not card:
        emit('error', {'message': 'Carte non trouvée'})
        return
    
    player.hand.remove(card)
    game['discard'].append(card)
    
    game['phase'] = 'draw'
    game['current_player'] = (game['current_player'] + 1) % game['num_players']
    
    attempts = 0
    while not game['players'][game['current_player']].connected and attempts < game['num_players']:
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
        attempts += 1
    
    for p in game['players']:
        if p.connected:
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p.id)
            }, room=p.session_id)

@socketio.on('get_game_state')
def handle_get_game_state(data):
    """Récupérer l'état actuel du jeu"""
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
    
    emit('game_state', {
        'game': get_game_state_for_player(game, player_id)
    })


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)