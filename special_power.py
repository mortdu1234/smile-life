"""
Extension pour gérer les pouvoirs spéciaux des métiers et cartes spéciales
"""
from flask import request
from flask_socketio import emit
from constants import socketio, games, player_sessions, get_game_state_for_player, apply_hardship_effect
from card_classes import Card, Player, CardFactory, HardshipCard, JobCard, StudyCard, SalaryCard, MarriageCard, AdulteryCard, HouseCard, TravelCard, ChildCard, SpecialCard, FlirtCard
import random

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
        
        player.hand.remove(card)
        player.add_card_to_played(card)
        
        # ✅ Envoyer la demande de cadeau à tous les autres joueurs
        for other in other_players:
            available_salaries = [c for c in other.played["vie professionnelle"] if isinstance(c, SalaryCard)]
            
            if available_salaries:
                socketio.emit('select_birthday_gift', {
                    'birthday_player_name': player.name,
                    'available_salaries': [s.to_dict() for s in available_salaries]
                }, room=other.session_id)
        
        game['phase'] = 'draw'
        game['current_player'] = (game['current_player'] + 1) % game['num_players']
        
        attempts = 0
        while not game['players'][game['current_player']].connected and attempts < game['num_players']:
            game['current_player'] = (game['current_player'] + 1) % game['num_players']
            attempts += 1
        
        # ✅ Mettre à jour tous les joueurs
        for p in game['players']:
            if p.connected:
                socketio.emit('game_updated', {
                    'game': get_game_state_for_player(game, p.id),
                    'message': f"🎂 C'est l'anniversaire de {player.name} !"
                }, room=p.session_id)

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
        # ✅ Chercher les métiers dans la MAIN du joueur
        available_jobs = [c for c in player.hand if isinstance(c, JobCard)]
        
        if not available_jobs:
            emit('error', {'message': 'Aucun métier disponible dans votre main'})
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
    
    # ✅ Chercher le métier dans la MAIN du joueur
    job = None
    for c in player.hand:
        if c.id == job_id and isinstance(c, JobCard):
            job = c
            player.hand.remove(c)  # ✅ Retirer de la main
            break
    
    if not job:
        emit('error', {'message': 'Métier non trouvé dans votre main'})
        return
    
    player.add_card_to_played(job)
    
    # 🆕 REPIOCHER UNE CARTE après avoir posé le métier
    if game['deck']:
        player.hand.append(game['deck'].pop())
    
    # La carte piston est déjà posée dans handle_play_special_card
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
                'message': f"🎯 {player.name} a obtenu un métier par piston et repioche 1 carte"
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
    cards_discarded = game['pending_special'].get('cards_discarded', 0)
    
    # 🆕 Repiocher : (cartes jouées + cartes défaussées) - 1
    # -1 car on ne repioche pas la carte Arc-en-ciel elle-même
    total_cards_used = cards_played + cards_discarded
    cards_to_draw = max(0, total_cards_used - 1)
    
    cards_drawn = 0
    for _ in range(cards_to_draw):
        if game['deck']:
            player.hand.append(game['deck'].pop())
            cards_drawn += 1
    
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
                'message': f"🌈 {player.name} a repioché {cards_drawn} carte(s) ({cards_played} posées + {cards_discarded} défaussées - 1)"
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



