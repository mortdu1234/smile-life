from flask import Flask, render_template, jsonify, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import uuid
from datetime import datetime
from card_classes import Card, Player, CardFactory, HardshipCard, JobCard, StudyCard, SalaryCard, MarriageCard, AdulteryCard, HouseCard, TravelCard, ChildCard, SpecialCard, FlirtCard

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
        'last_discard': game['discard'][-1].to_dict() if game['discard'] else None,
        'current_player': game['current_player'],
        'casino': {
            'open': game['casino']['open'],
            'first_bet': {
                'player_id': game['casino']['first_bet']['player_id'],
                'player_name': game['players'][game['casino']['first_bet']['player_id']].name,
                'salary_level': None  # Secret !
            } if game['casino']['first_bet'] else None,
            'second_bet': {
                'player_id': game['casino']['second_bet']['player_id'],
                'player_name': game['players'][game['casino']['second_bet']['player_id']].name,
                'salary_level': None  # Secret !
            } if game['casino']['second_bet'] else None
        },
        'phase': game['phase'],
        'num_players': game['num_players'],
        'players_joined': game['players_joined'],
        'your_player_id': player_id,
        'pending_hardship': game.get('pending_hardship'),
        'pending_special': game.get('pending_special')
    }
    print(f"État du jeu pour joueur {player_id}: deck={game_state['deck_count']}, discard={len(game_state['discard'])}, phase={game_state['phase']}, casino_open={game_state['casino']['open']}")
    return game_state

def apply_hardship_effect(game, hardship_card, target_player, attacker_player):
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
        target_player.skip_turns = 1
        target_player.received_hardships.append(hardship_type)
        return True, f"{target_player.name} doit passer 1 tour"
    
    elif hardship_type == 'burnout':
        target_player.skip_turns = 1
        target_player.received_hardships.append(hardship_type)
        return True, f"{target_player.name} doit passer 1 tour"
    
    elif hardship_type == 'divorce':
        marriage_cards = [c for c in target_player.played["vie personnelle"] if isinstance(c, MarriageCard)]
        if marriage_cards:
            marriage_to_remove = marriage_cards[-1]
            target_player.remove_card_from_played(marriage_to_remove)
            game['discard'].append(marriage_to_remove)
            
            adultery_cards = [c for c in target_player.played["vie personnelle"] if isinstance(c, AdulteryCard)]
            if adultery_cards:
                adultery = adultery_cards[0]
                target_player.remove_card_from_played(adultery)
                game['discard'].append(adultery)
                
                children_cards = [c for c in target_player.played["vie personnelle"] if isinstance(c, ChildCard)]
                for child in children_cards:
                    target_player.remove_card_from_played(child)
                    game['discard'].append(child)
                
                adultery_flirts = [c for c in target_player.played["cartes spéciales"] if isinstance(c, FlirtCard)]
                for flirt in adultery_flirts:
                    target_player.remove_card_from_played(flirt)
                    game['discard'].append(flirt)
                
                target_player.received_hardships.append(hardship_type)
                return True, f"{target_player.name} a divorcé et perdu son adultère, ses enfants et ses flirts adultères"
            
            target_player.received_hardships.append(hardship_type)
            return True, f"{target_player.name} a divorcé"
        return False, f"{target_player.name} n'est pas marié"
    
    elif hardship_type == 'impot':
        salary_cards = [c for c in target_player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
        if salary_cards:
            card_to_remove = salary_cards[-1]
            target_player.remove_card_from_played(card_to_remove)
            game['discard'].append(card_to_remove)
            target_player.received_hardships.append(hardship_type)
            return True, f"{target_player.name} a perdu 1 salaire"
        return False, f"{target_player.name} n'a pas de salaire"
    
    elif hardship_type == 'licenciement':
        job_card = target_player.get_job()
        if job_card:
            target_player.remove_card_from_played(job_card)
            game['discard'].append(job_card)
            target_player.received_hardships.append(hardship_type)
            return True, f"{target_player.name} a été licencié"
        return False, f"{target_player.name} n'a pas de métier"
    
    elif hardship_type == 'maladie':
        target_player.skip_turns = 1
        target_player.received_hardships.append(hardship_type)
        return True, f"{target_player.name} est malade (passe 1 tour)"
    
    elif hardship_type == 'redoublement':
        study_cards = [c for c in target_player.played["vie professionnelle"] if isinstance(c, StudyCard)]
        if study_cards:
            card_to_remove = study_cards[-1]
            target_player.remove_card_from_played(card_to_remove)
            game['discard'].append(card_to_remove)
            target_player.received_hardships.append(hardship_type)
            return True, f"{target_player.name} a perdu une étude"
        return False, f"{target_player.name} n'a pas d'études à perdre"
    
    elif hardship_type == 'prison':
        target_player.skip_turns = 3
        target_player.received_hardships.append(hardship_type)
        return True, f"{target_player.name} est en prison pour 3 tours"
    
    elif hardship_type == 'attentat':
        children_cards = [c for c in attacker_player.played["vie personnelle"] if isinstance(c, ChildCard)]
        total_children_removed = len(children_cards)
        
        for child in children_cards:
            attacker_player.remove_card_from_played(child)
            game['discard'].append(child)
        
        attacker_player.received_hardships.append(hardship_type)
        
        if total_children_removed > 0:
            return True, f"Attentat ! {attacker_player.name} perd {total_children_removed} enfant(s)"
        else:
            return True, f"Attentat ! {attacker_player.name} n'avait pas d'enfant"
    
    return True, f"Malus {hardship_type} appliqué à {target_player.name}"

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
    cards_distribution = ""
    invert_deck = deck[::-1]
    for i in range(len(deck)):
        cards_distribution += f"{i} : {str(invert_deck[i])} - {invert_deck[i].id}\n"
    with open("distribution.txt", 'w') as file:
        file.write(cards_distribution)
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

@socketio.on('skip_turn')
def handle_skip_turn(data):
    """Passer son tour manuellement"""
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
    
    if player.skip_turns > 0:
        player.skip_turns -= 1
        message = f"{player.name} passe son tour ({player.skip_turns} tour(s) restant(s))"
    else:
        message = f"{player.name} passe son tour volontairement"
    
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

@socketio.on('pick_card')
def give_card(data):
    """Donner une carte au joueur"""
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
    player = game['players'][player_id]

    if source == 'deck':
        if not game['deck']:
            scores = [(p.name, p.calculate_smiles(), p.id) for p in game['players'] if p.connected]
            scores.sort(key=lambda x: x[1], reverse=True)
            socketio.emit('game_over', {'scores': scores}, room=game_id)
            return
        
        card = game['deck'].pop()
        player.hand.append(card)
        
        print(f"Joueur {player_id} a pris dans le deck, reste {len(game['deck'])} cartes")
        socketio.emit('game_updated', {
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
        
        if isinstance(card, HardshipCard):
            player.hand.append(card)
            game['phase'] = 'play'
            
            for p in game['players']:
                if p.connected and p.id == player_id:
                    socketio.emit('select_hardship_target', {
                        'card': card.to_dict(),
                        'available_targets': [
                            {'id': i, 'name': p.name} 
                            for i, p in enumerate(game['players']) 
                            if p.connected and i != player_id
                        ],
                        'from_discard': True
                    }, room=p.session_id)
        elif isinstance(card, (HouseCard, TravelCard)):
            player.hand.append(card)
            game['phase'] = 'play'
        else:
            player.add_card_to_played(card)
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

@socketio.on('select_salaries_for_purchase')
def handle_select_salaries(data):
    """Le joueur sélectionne les salaires pour payer une acquisition"""
    card_id = data.get('card_id')
    salary_ids = data.get('salary_ids', [])
    use_heritage = data.get('use_heritage', 0)
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
    player = game['players'][player_id]
    
    card = None
    for c in player.hand:
        if c.id == card_id:
            card = c
            break
    
    if not card or not isinstance(card, (HouseCard, TravelCard)):
        emit('error', {'message': 'Carte non valide'})
        return
    
    required = card.cost if isinstance(card, HouseCard) else 3
    
    job = player.get_job()
    if job:
        if isinstance(card, HouseCard) and job.power == 'house_free':
            required = 0
        elif isinstance(card, TravelCard) and job.power == 'travel_free':
            required = 0
    
    if required == 0:
        player.hand.remove(card)
        player.add_card_to_played(card)
        
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
        return
    
    if use_heritage > player.heritage:
        emit('error', {'message': f'Vous n\'avez que {player.heritage} d\'héritage disponible'})
        return
    
    selected_salaries = []
    for salary_id in salary_ids:
        for salary in player.played["vie professionnelle"]:
            if isinstance(salary, SalaryCard) and salary.id == salary_id:
                selected_salaries.append(salary)
                break
    
    total_salaries = sum(s.level for s in selected_salaries)
    total = total_salaries + use_heritage
    
    if total < required:
        emit('error', {'message': f'Montant insuffisant : {total}/{required} (minimum requis)'})
        return
    
    if use_heritage > 0:
        player.heritage -= use_heritage
    
    for salary in selected_salaries:
        player.played["vie professionnelle"].remove(salary)
        player.played["salaire dépensé"].append(salary)
    
    player.hand.remove(card)
    player.add_card_to_played(card)
    
    game['phase'] = 'draw'
    game['current_player'] = (game['current_player'] + 1) % game['num_players']
    
    attempts = 0
    while not game['players'][game['current_player']].connected and attempts < game['num_players']:
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
        attempts += 1
    
    card_name = getattr(card, 'house_type', 'un voyage')
    for p in game['players']:
        if p.connected:
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p.id),
                'message': f"{player.name} a acheté {card_name} (salaires: {total_salaries}, héritage: {use_heritage})"
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

@socketio.on('discard_played_card')
def handle_discard_played_card(data):
    """Défausser une carte déjà posée (métier, mariage ou adultère)"""
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
    
    if game['phase'] != 'draw':
        emit('error', {'message': 'Vous ne pouvez défausser qu\'avant de piocher'})
        return
    
    player = game['players'][player_id]
    
    card = None
    all_cards = player.get_all_played_cards()
    for c in all_cards:
        if c.id == card_id:
            card = c
            break
    
    if not card:
        emit('error', {'message': 'Carte non trouvée'})
        return
    
    if not isinstance(card, (JobCard, MarriageCard, AdulteryCard)):
        emit('error', {'message': 'Seuls les métiers, mariages et adultères peuvent être défaussés'})
        return
    
    player.remove_card_from_played(card)
    game['discard'].append(card)
    
    card_type = "métier" if isinstance(card, JobCard) else ("mariage" if isinstance(card, MarriageCard) else "adultère")
    
    for p in game['players']:
        if p.connected:
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p.id),
                'message': f"{player.name} a défaussé son {card_type}"
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
        emit('error', {'message': 'Carte non trouvée dans votre main'})
        return
    
    # Carte d'attaque
    if isinstance(card, HardshipCard):
        if target_player_id is None:
            available_targets = []
            for i, p in enumerate(game['players']):
                if p.connected and i != player_id:
                    job = p.get_job()
                    is_immune = False
                    
                    if job:
                        immunities = {
                            'accident': ['no_accident'],
                            'maladie': ['no_illness', 'no_illness_extra_study'],
                            'attentat': ['no_attentat'],
                            'divorce': ['no_divorce'],
                            'licenciement': ['no_fire_tax'],
                            'impot': ['no_fire_tax']
                        }
                        
                        if card.hardship_type in immunities:
                            if job.power in immunities[card.hardship_type]:
                                is_immune = True
                    
                    available_targets.append({
                        'id': i,
                        'name': p.name,
                        'immune': is_immune
                    })
            
            if not available_targets:
                emit('error', {'message': 'Aucune cible disponible'})
                return
            
            emit('select_hardship_target', {
                'card': card.to_dict(),
                'available_targets': available_targets
            })
            return
        
        target = game['players'][target_player_id]
        success, message = apply_hardship_effect(game, card, target, player)
        
        if success:
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
                        'game': get_game_state_for_player(game, p.id),
                        'message': message
                    }, room=p.session_id)
        else:
            emit('error', {'message': message})
        return
    

    
    # Acquisition
    if isinstance(card, (HouseCard, TravelCard)):
        job = player.get_job()
        cost = card.cost if isinstance(card, HouseCard) else 3
        
        if job:
            if isinstance(card, HouseCard) and job.power == 'house_free':
                cost = 0
            elif isinstance(card, TravelCard) and job.power == 'travel_free':
                cost = 0
        
        if isinstance(card, HouseCard) and player.is_married() and cost > 0:
            cost = cost // 2
        
        if cost > 0:
            available_salaries = [c for c in player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
            
            if not available_salaries and player.heritage < cost:
                emit('error', {'message': f'Vous avez besoin de salaires ou d\'héritage pour acheter (coût: {cost})'})
                return
            
            emit('select_salaries_for_acquisition', {
                'card': card.to_dict(),
                'required_cost': cost,
                'available_salaries': [s.to_dict() for s in available_salaries],
                'heritage_available': player.heritage
            })
            return
        else:
            player.hand.remove(card)
            player.add_card_to_played(card)
            
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
                        'message': f"{player.name} a posé une carte (gratuite grâce au métier)"
                    }, room=p.session_id)
            return
    
    if isinstance(card, SpecialCard):
        print("la carte jouée est spéciale")
        handle_play_special_card(data)
        return
    
    # Vérifier si la carte peut être jouée
    can_play, message = card.can_be_played(player)
    
    if not can_play:
        emit('error', {'message': message})
        return
    
    if isinstance(card, MarriageCard):
        if not card.can_be_played(player):
            emit('error', {'message': 'Vous devez avoir un flirt pour jouer un mariage'})
            return
    
    # Jouer la carte
    player.hand.remove(card)
    player.add_card_to_played(card)
    
    # Mode arc-en-ciel
    if game.get('pending_special') and game['pending_special'].get('type') == 'arc_en_ciel':
        game['pending_special']['cards_played'] += 1
        cards_played = game['pending_special']['cards_played']
        max_cards = game['pending_special'].get('max_cards', 3)
        
        game['phase'] = 'play'
        
        for p in game['players']:
            if p.connected:
                socketio.emit('game_updated', {
                    'game': get_game_state_for_player(game, p.id),
                    'message': f"{player.name} a posé une carte ({cards_played}/{max_cards})"
                }, room=p.session_id)
        
        if cards_played >= max_cards:
            for _ in range(cards_played):
                if game['deck']:
                    player.hand.append(game['deck'].pop())
            
            game['pending_special'] = None
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
                        'message': f"🌈 {player.name} a repioché {cards_played} carte(s)"
                    }, room=p.session_id)
        return
    
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
                'message': f"{player.name} a posé une carte"
            }, room=p.session_id)

@socketio.on('play_special_card')
def handle_play_special_card(data):
    """Jouer une carte spéciale"""
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
    
    player = game['players'][player_id]
    
    card = None
    for c in player.hand:
        if c.id == card_id:
            card = c
            break
    
    if not card or not isinstance(card, SpecialCard):
        emit('error', {'message': 'Carte spéciale non trouvée'})
        return
    
    special_type = card.special_type
    if special_type == 'anniversaire':
        other_players = [p for i, p in enumerate(game['players']) if p.connected and i != player_id]
        
        if not other_players:
            emit('error', {'message': 'Aucun autre joueur connecté'})
            return
        
        for other in other_players:
            available_salaries = [c for c in other.played["vie professionnelle"] if isinstance(c, SalaryCard)]
            
            if available_salaries:
                socketio.emit('select_birthday_gift', {
                    'birthday_player_name': player.name,
                    'available_salaries': [s.to_dict() for s in available_salaries]
                }, room=other.session_id)
        
        player.hand.remove(card)
        player.add_card_to_played(card)
        
        game['phase'] = 'draw'
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
        
        attempts = 0
        while not game['players'][game['current_player']].connected and attempts < game['num_players']:
            game['current_player'] = (game['current_player'] + 1) % game['num_players']
            attempts += 1
    
    elif special_type == 'troc':
        other_players = [{'id': i, 'name': p.name, 'hand_count': len(p.hand)} 
                        for i, p in enumerate(game['players']) 
                        if p.connected and i != player_id and len(p.hand) > 0]
        
        if not other_players:
            emit('error', {'message': 'Aucun joueur avec des cartes disponibles'})
            return
        
        player.hand.remove(card)
        game['pending_special'] = {
            'type': 'troc',
            'card': card,
            'player_id': player_id
        }
        
        emit('select_troc_target', {
            'available_targets': other_players
        })
    
    elif special_type == 'piston':
        available_jobs = [c for c in game['deck'] if isinstance(c, JobCard)][:10]
        
        if not available_jobs:
            emit('error', {'message': 'Aucun métier disponible'})
            return
        
        player.hand.remove(card)
        player.add_card_to_played(card)
        game['pending_special'] = {
            'type': 'piston',
            'card': card,
            'player_id': player_id
        }
        
        emit('select_piston_job', {
            'available_jobs': [j.to_dict() for j in available_jobs]
        })
    
    elif special_type == 'vengeance':
        if not player.received_hardships:
            emit('error', {'message': 'Vous n\'avez reçu aucun coup dur'})
            return
        
        other_players = [{'id': i, 'name': p.name} 
                        for i, p in enumerate(game['players']) 
                        if p.connected and i != player_id]
        
        player.hand.remove(card)
        player.add_card_to_played(card)
        game['pending_special'] = {
            'type': 'vengeance',
            'card': card,
            'player_id': player_id
        }
        
        emit('select_vengeance', {
            'received_hardships': player.received_hardships,
            'available_targets': other_players
        })
    
    elif special_type == 'chance':
        player.hand.remove(card)
        player.add_card_to_played(card)
        if len(game['deck']) < 3:
            emit('error', {'message': 'Pas assez de cartes dans la pioche'})
            return
        
        choices = [game['deck'].pop() for _ in range(3)]
        
        emit('select_chance_card', {
            'cards': [c.to_dict() for c in choices]
        })
        
        game['pending_special'] = {
            'type': 'chance',
            'choices': choices,
            'player_id': player_id
        }
    
    elif special_type == 'arc en ciel':
        player.hand.remove(card)
        player.add_card_to_played(card)
        
        game['pending_special'] = {
            'type': 'arc_en_ciel',
            'player_id': player_id,
            'cards_played': 0,
            'max_cards': 3
        }
        
        game['phase'] = 'play'
        
        emit('arc_en_ciel_mode', {})
    
    elif special_type == 'etoile filante':
        player.hand.remove(card)
        player.add_card_to_played(card)
        if not game['discard']:
            emit('error', {'message': 'La défausse est vide'})
            return
        
        emit('select_from_discard', {
            'discard_cards': [c.to_dict() for c in game['discard']]
        })

    elif special_type == 'heritage':
        player.heritage += 3
        player.hand.remove(card)
        player.add_card_to_played(card)
        
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
                    'message': f"{player.name} a reçu un héritage de 3 💰"
                }, room=p.session_id)
    
    elif special_type == 'tsunami':
        affected = []
        all_cards = []
        
        player.hand.remove(card)
        player.add_card_to_played(card)

        for p in game['players']:
            if p.connected and len(p.hand) > 0:
                all_cards.extend(p.hand)
                p.hand = []
                affected.append(p.name)
        
        random.shuffle(all_cards)
        
        connected_players = [p for p in game['players'] if p.connected]
        if connected_players and all_cards:
            cards_per_player = len(all_cards) // len(connected_players)
            extra_cards = len(all_cards) % len(connected_players)
            
            card_index = 0
            for i, p in enumerate(connected_players):
                cards_to_give = cards_per_player + (1 if i < extra_cards else 0)
                p.hand = all_cards[card_index:card_index + cards_to_give]
                card_index += cards_to_give
        
        
        game['phase'] = 'draw'
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
        
        attempts = 0
        while not game['players'][game['current_player']].connected and attempts < game['num_players']:
            game['current_player'] = (game['current_player'] + 1) % game['num_players']
            attempts += 1
        
        message = f"🌊 Tsunami ! Les cartes de {', '.join(affected)} ont été mélangées et redistribuées !" if affected else "🌊 Tsunami ! Personne n'avait de cartes"
        
        for p in game['players']:
            if p.connected:
                socketio.emit('game_updated', {
                    'game': get_game_state_for_player(game, p.id),
                    'message': message
                }, room=p.session_id)
    
    elif special_type == 'casino':
        player.hand.remove(card)
        player.add_card_to_played(card)
        
        game['casino']['open'] = True
        game['casino']['first_bet'] = None
        game['casino']['second_bet'] = None
        game['casino']['opener_id'] = player_id  # Mémoriser qui a ouvert
        
        # Le joueur qui a ouvert le casino peut directement miser
        available_salaries = [c for c in player.hand if isinstance(c, SalaryCard)]
        
        if available_salaries:
            emit('select_casino_bet', {
                'available_salaries': [s.to_dict() for s in available_salaries],
                'is_opener': True,
                'message': 'Voulez-vous miser au casino ? (Optionnel - le casino reste ouvert même si vous refusez)'
            })
        else:
            # Le casino reste ouvert, on passe au joueur suivant
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
                        'message': f"🎰 {player.name} a ouvert le casino !"
                    }, room=p.session_id)
        
        return

@socketio.on('birthday_gift_selected')
def handle_birthday_gift(data):
    """Un joueur offre un salaire pour un anniversaire"""
    salary_id = data.get('salary_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game['players'][player_id]
    
    salary = None
    for s in player.played["vie professionnelle"]:
        if isinstance(s, SalaryCard) and s.id == salary_id:
            salary = s
            break
    
    if salary:
        birthday_player_id = (game['current_player'] - 1) % game['num_players']
        birthday_player = game['players'][birthday_player_id]
        
        player.remove_card_from_played(salary)
        birthday_player.add_card_to_played(salary)
        
        for p in game['players']:
            if p.connected:
                socketio.emit('game_updated', {
                    'game': get_game_state_for_player(game, p.id),
                    'message': f"🎂 {player.name} offre un salaire à {birthday_player.name}"
                }, room=p.session_id)

@socketio.on('troc_target_selected')
def handle_troc_target(data):
    """Échanger une carte avec un autre joueur"""
    target_id = data.get('target_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game['players'][player_id]
    target = game['players'][target_id]
    
    if not player.hand or not target.hand:
        emit('error', {'message': 'Impossible d\'échanger'})
        return
    
    troc_card = game['pending_special']['card']
    
    card1 = random.choice(player.hand)
    card2 = random.choice(target.hand)
    
    player.hand.remove(card1)
    target.hand.remove(card2)
    player.hand.append(card2)
    target.hand.append(card1)
    
    player.add_card_to_played(troc_card)
    game['pending_special'] = None
    
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
                'message': f"🔄 {player.name} a échangé une carte avec {target.name}"
            }, room=p.session_id)

@socketio.on('piston_job_selected')
def handle_piston_job(data):
    """Poser un métier sans condition"""
    job_id = data.get('job_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game['players'][player_id]
    
    job = None
    for c in game['deck']:
        if c.id == job_id and isinstance(c, JobCard):
            job = c
            game['deck'].remove(c)
            break
    
    if job:
        player.add_card_to_played(job)
        
        piston_card = game['pending_special']['card']
        player.add_card_to_played(piston_card)
        game['pending_special'] = None
        
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
                    'message': f"🎯 {player.name} a obtenu un métier par piston"
                }, room=p.session_id)

@socketio.on('vengeance_selected')
def handle_vengeance(data):
    """Renvoyer un coup dur"""
    hardship_type = data.get('hardship_type')
    target_id = data.get('target_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game['players'][player_id]
    target = game['players'][target_id]
    
    if hardship_type in player.received_hardships:
        player.received_hardships.remove(hardship_type)
        
        hardship_card = HardshipCard(hardship_type)
        success, message = apply_hardship_effect(game, hardship_card, target, player)
        
        vengeance_card = game['pending_special']['card']
        player.add_card_to_played(vengeance_card)
        game['pending_special'] = None
        
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
                    'message': f"⚔️ {player.name} se venge sur {target.name} : {message}"
                }, room=p.session_id)

@socketio.on('chance_card_selected')
def handle_chance_card(data):
    """Choisir une carte parmi 3"""
    card_id = data.get('card_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    game = games[game_id]
    
    if not game.get('pending_special') or game['pending_special']['type'] != 'chance':
        return
    
    choices = game['pending_special']['choices']
    selected = None
    
    for card in choices:
        if card.id == card_id:
            selected = card
            choices.remove(card)
            break
    
    if selected:
        player = game['players'][game['pending_special']['player_id']]
        player.hand.append(selected)
        
        game['deck'].extend(choices)
        random.shuffle(game['deck'])
        
        game['pending_special'] = None
        
        for p in game['players']:
            if p.connected:
                socketio.emit('game_updated', {
                    'game': get_game_state_for_player(game, p.id)
                }, room=p.session_id)

@socketio.on('arc_en_ciel_finished')
def handle_arc_finished(data):
    """Terminer le mode arc-en-ciel et repiocher"""
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    game = games[game_id]
    player = game['players'][session_info['player_id']]
    
    if not game.get('pending_special') or game['pending_special'].get('type') != 'arc_en_ciel':
        return
    
    cards_played = game['pending_special'].get('cards_played', 0)
    for _ in range(cards_played):
        if game['deck']:
            player.hand.append(game['deck'].pop())
    
    game['pending_special'] = None
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
                'message': f"🌈 {player.name} a repioché {cards_played} carte(s)"
            }, room=p.session_id)

@socketio.on('discard_card_selected')
def handle_discard_card_selected(data):
    """Choisir une carte de la défausse (étoile filante)"""
    card_id = data.get('card_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game['players'][player_id]
    
    card = None
    for c in game['discard']:
        if c.id == card_id:
            card = c
            break
    
    if not card:
        emit('error', {'message': 'Carte non trouvée'})
        return
    
    can_play, message = card.can_be_played(player)
    if not can_play:
        emit('error', {'message': f'Impossible de jouer cette carte : {message}'})
        return
    
    game['discard'].remove(card)
    player.add_card_to_played(card)
    
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
                'message': f"⭐ {player.name} a récupéré une carte de la défausse"
            }, room=p.session_id)


@socketio.on('place_casino_bet')
def handle_casino_bet(data):
    """Placer un pari au casino"""
    salary_id = data.get('salary_id')
    is_opener = data.get('is_opener', False)
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
    player = game['players'][player_id]
    
    # Vérifier que le casino est ouvert
    if not game['casino']['open']:
        emit('error', {'message': 'Le casino est fermé'})
        return
    
    # Vérifier qu'il y a de la place
    if game['casino']['first_bet'] and game['casino']['second_bet']:
        emit('error', {'message': 'Le casino est plein'})
        return
    
    # ✅ CHERCHER LE SALAIRE DANS LA MAIN
    salary_card = None
    for card in player.hand:
        if isinstance(card, SalaryCard) and card.id == salary_id:
            salary_card = card
            break
    
    if not salary_card:
        emit('error', {'message': 'Salaire non trouvé dans votre main'})
        return
    
    # Retirer le salaire de la main du joueur
    player.hand.remove(salary_card)
    
    # Premier pari
    if not game['casino']['first_bet']:
        game['casino']['first_bet'] = {
            'player_id': player_id,
            'salary_card': salary_card
        }
        
        message = f"🎰 {player.name} a misé au casino (1er pari - montant secret)"
        
        # Si c'est l'ouvreur, on passe au joueur suivant
        if is_opener:
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
    
    # Deuxième pari - résolution
    else:
        game['casino']['second_bet'] = {
            'player_id': player_id,
            'salary_card': salary_card
        }
        
        first_bet = game['casino']['first_bet']
        second_bet = game['casino']['second_bet']
        
        first_player = game['players'][first_bet['player_id']]
        second_player = game['players'][second_bet['player_id']]
        
        # Comparer les niveaux
        if first_bet['salary_card'].level == second_bet['salary_card'].level:
            # Égalité : le deuxième joueur gagne les deux salaires
            second_player.add_card_to_played(first_bet['salary_card'])
            second_player.add_card_to_played(second_bet['salary_card'])
            
            message = f"🎰 Casino ! {second_player.name} GAGNE les deux salaires (égalité) !"
        else:
            # Différent : le premier joueur gagne les deux salaires
            first_player.add_card_to_played(first_bet['salary_card'])
            first_player.add_card_to_played(second_bet['salary_card'])
            
            message = f"🎰 Casino ! {first_player.name} GAGNE les deux salaires !"
        
        # Fermer le casino après résolution
        game['casino']['first_bet'] = None
        game['casino']['second_bet'] = None
        game['casino']['opener_id'] = None
        
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


@socketio.on('skip_casino_bet')
def handle_skip_casino_bet(data):
    """L'ouvreur du casino décide de ne pas miser"""
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
    player = game['players'][player_id]
    
    # Vérifier que c'est bien l'ouvreur
    if game['casino'].get('opener_id') != player_id:
        emit('error', {'message': 'Seul l\'ouvreur peut refuser de miser'})
        return
    
    # Le casino reste ouvert, on passe au joueur suivant
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
                'message': f"🎰 {player.name} n'a pas misé. Le casino reste ouvert !"
            }, room=p.session_id)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)