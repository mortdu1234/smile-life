from flask_socketio import emit
from card_classes import Card, Player, HardshipCard, JobCard, StudyCard, SalaryCard, MarriageCard, AdulteryCard, HouseCard, TravelCard, ChildCard, SpecialCard, FlirtCard
from constants import app, socketio, games, player_sessions, get_game_state_for_player, apply_hardship_effect, check_game
from special_power import *
import init

@socketio.on('skip_turn')
def handle_skip_turn(data):
    """Passer son tour manuellement"""
    player_id, game, _ = check_game()

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
    player_id, game, game_id = check_game()

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
    player_id, game, game_id = check_game()
    
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
    player_id, game, _ = check_game()
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
    
    # ✅ Appliquer la réduction pour mariage AVANT validation
    if isinstance(card, HouseCard) and player.is_married() and required > 0:
        required = required // 2
    
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
            
@socketio.on('discard_during_arc')
def handle_discard_during_arc(data):
    """Défausser une carte pendant l'arc-en-ciel"""
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    
    if game['current_player'] != player_id:
        emit('error', {'message': 'Ce n\'est pas votre tour'})
        return
    
    # ✅ Vérifier qu'on est bien en mode arc-en-ciel
    if not game.get('pending_special') or game['pending_special'].get('type') != 'arc_en_ciel':
        emit('error', {'message': 'Vous n\'êtes pas en mode arc-en-ciel'})
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
    
    for p in game['players']:
        if p.connected:
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p.id),
                'message': f"{player.name} a défaussé une carte pendant l'arc-en-ciel"
            }, room=p.session_id)
            
@socketio.on('discard_card')
def handle_discard_card(data):
    """Défausser une carte"""
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    
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
    player_id, game, _ = check_game()
    
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
    player_id, game, _ = check_game()

    
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
        
        # ✅ Appliquer la réduction AVANT d'envoyer le modal
        if isinstance(card, HouseCard) and player.is_married() and cost > 0:
            cost = cost // 2
        
        if cost > 0:
            available_salaries = [c for c in player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
            
            if not available_salaries and player.heritage < cost:
                emit('error', {'message': f'Vous avez besoin de salaires ou d\'hÃ©ritage pour acheter (coÃ»t: {cost})'})
                return
            
            emit('select_salaries_for_acquisition', {
                'card': card.to_dict(),
                'required_cost': cost,  # ✅ Coût déjà réduit si marié
                'available_salaries': [s.to_dict() for s in available_salaries],
                'heritage_available': player.heritage
            })
            return
    
    # Carte spéciale
    if isinstance(card, SpecialCard):
        print("une carte jouée est spéciale")
        handle_play_special_card(data)
        return
    
    # Vérifier si la carte peut être jouée
    can_play, message = card.can_be_played(player)
    
    if not can_play:
        emit('error', {'message': message})
        return
    
    # carte Mariage
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




if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)