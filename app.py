from flask_socketio import emit
from card_classes import *
from constants import app, socketio, games, player_sessions, get_game_state_for_player, apply_hardship_effect, check_game, next_player
from special_power import *
import init
import random

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
        # ✅ NOUVEAU: Vérifier si c'est un JobCard avec pouvoir instantané
        elif isinstance(card, JobCard):
            # Vérifier si le métier a un pouvoir instantané
            if have_special_power(card.job_name):
                # Ajouter à la main pour que le joueur puisse l'activer
                player.hand.append(card)
                game['phase'] = 'play'
                # Le joueur verra la carte dans sa main avec un bouton "Jouer"
                # Quand il cliquera, do_instant_power() s'exécutera
            else:
                # Métier normal: posé directement
                if player.has_job():
                    # Ajouter à la main si le joueur a déjà un métier
                    player.hand.append(card)
                    game['phase'] = 'play'
                else:
                    can_play, message = card.can_be_played(player)
                    if can_play:
                        player.add_card_to_played(card)
                        game['phase'] = 'draw'
                        game['current_player'] = (game['current_player'] + 1) % game['num_players']
                        attempts = 0
                        while not game['players'][game['current_player']].connected and attempts < game['num_players']:
                            game['current_player'] = (game['current_player'] + 1) % game['num_players']
                            attempts += 1
                    else:
                        player.hand.append(card)
                        game['phase'] = 'play'
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

@socketio.on('discard_played_card')
def handle_discard_played_card(data):
    """Défausser une carte déjà posée (métier, mariage ou adultère)"""
    print("deffausse une carte")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    
    if game['current_player'] != player_id:
        emit('error', {'message': 'Ce n\'est pas votre tour'})
        return
    
    # 🆕 Récupérer la carte AVANT de vérifier la phase
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
    
    # 🆕 Vérifier si c'est un métier intérimaire
    is_temp_job = isinstance(card, JobCard) and card.status == 'intérimaire'
    
    # 🆕 Les métiers intérimaires peuvent être défaussés à tout moment
    # Les autres cartes seulement en phase 'draw'
    if not is_temp_job and game['phase'] != 'draw':
        emit('error', {'message': 'Vous ne pouvez défausser qu\'avant de piocher (sauf métiers intérimaires)'})
        return
    
    if not isinstance(card, (JobCard, MarriageCard, AdulteryCard)):
        emit('error', {'message': 'Seuls les métiers, mariages et adultères peuvent être défaussés'})
        return
    
    player.remove_card_from_played(card)
    game['discard'].append(card)
    
    # ✅ AJOUT : Si c'est un chercheur, défausser une carte aléatoire de la main
    if isinstance(card, JobCard) and card.job_name == 'chercheur':
        handle_loose_chercheur_job()
    
    message_suffix = ""
    # 🆕 Afficher le statut du métier dans le message
    card_type = "métier" if isinstance(card, JobCard) else ("mariage" if isinstance(card, MarriageCard) else "adultère")
    job_status = f" ({card.status})" if isinstance(card, JobCard) else ""
    
    if not is_temp_job:
        next_player(game)
    
    for p in game['players']:
        if p.connected:
            socketio.emit('game_updated', {
                'game': get_game_state_for_player(game, p.id),
                'message': f"{player.name} a défaussé son {card_type}{job_status}{message_suffix}"
            }, room=p.session_id)

def getCardLabel(card):
    """Retourne le label d'une carte pour l'affichage"""
    if isinstance(card, JobCard):
        return card.job_name
    elif isinstance(card, StudyCard):
        return 'Études x2' if card.study_type == 'double' else 'Études'
    elif isinstance(card, SalaryCard):
        return f'Salaire {card.level}'
    elif isinstance(card, FlirtCard):
        return f'Flirt ({card.location})'
    elif isinstance(card, MarriageCard):
        return f'Mariage ({card.location})'
    elif isinstance(card, ChildCard):
        return card.name
    elif isinstance(card, AnimalCard):
        return card.animal_name
    elif isinstance(card, HouseCard):
        return f'Maison {card.house_type}'
    elif isinstance(card, TravelCard):
        return 'Voyage'
    elif isinstance(card, HardshipCard):
        return card.hardship_type
    elif isinstance(card, SpecialCard):
        return card.special_type
    elif isinstance(card, AdulteryCard):
        return 'Adultère'
    elif isinstance(card, OtherCard):
        if card.card_type == 'legion':
            return "Légion d'honneur"
        elif card.card_type == 'prix':
            return 'Grand Prix'
    return 'Carte'

@socketio.on('select_salaries_for_purchase')
def handle_select_salaries(data):
    """Le joueur sélectionne les salaires pour payer une acquisition"""
    card_id = data.get('card_id')
    salary_ids = data.get('salary_ids', [])
    use_heritage = data.get('use_heritage', 0)
    player_id, game, _ = check_game()
    player = game['players'][player_id]
    
    # ✅ VÉRIFIER SI C'EST UN ACHAT CHEF DES ACHATS
    is_chef_achats = (game.get('pending_special') and 
                      game['pending_special'].get('type') == 'chef_achats_purchase')
    
    if is_chef_achats:
        # ✅ Récupérer la carte depuis la DÉFAUSSE
        acquisition_id = game['pending_special']['acquisition_id']
        card = None
        for c in game['discard']:
            if c.id == acquisition_id:
                card = c
                break
        
        if not card:
            emit('error', {'message': 'Carte non trouvée dans la défausse'})
            game['pending_special'] = None
            return
    else:
        # Cas normal : carte dans la main
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
            # ✅ MAINTENANT on modifie le pouvoir (après validation)
            job.power = 'None'
        elif isinstance(card, TravelCard) and job.power == 'travel_free':
            required = 0
    
    # ✅ Appliquer la réduction pour mariage AVANT validation
    if isinstance(card, HouseCard) and player.is_married() and required > 0:
        required = required // 2
    
    if required == 0:
        # ✅ Gérer selon l'origine
        if is_chef_achats:
            game['discard'].remove(card)
            game['pending_special'] = None
        else:
            player.hand.remove(card)
        
        player.add_card_to_played(card)
        
        next_player(game)
        
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
    
    # ✅ Gérer selon l'origine
    if is_chef_achats:
        game['discard'].remove(card)
        game['pending_special'] = None
    else:
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

@socketio.on('cancel_select_salaries_for_purchase')
def handle_cancel_select_salarie(data):
    """le joueur annule la sélection d'achat d'une carte"""
    card_id = data.get('card_id')
    salary_ids = data.get('salary_ids', [])
    use_heritage = data.get('use_heritage', 0)
    player_id, game, _ = check_game()
    player = game['players'][player_id]
    
    # ✅ VÉRIFIER SI C'EST UN ACHAT CHEF DES ACHATS
    is_chef_achats = (game.get('pending_special') and 
                      game['pending_special'].get('type') == 'chef_achats_purchase')
    
    if is_chef_achats:
        handle_cancel_chef_achats_job()

@socketio.on('discard_card')
def handle_discard_card(data):
    """Défausser une carte"""
    print("défausser une carte [handle discard_card]")
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
    
    # si on est en mode arc-en-ciel
    if not (game.get('pending_special') and game['pending_special'].get('type') == 'arc_en_ciel'):            
        next_player(game)
    else :
        game['pending_special']['cards_discarded'] += 1
    
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
    can_play, message = card.can_be_played(player)
    if not can_play:
        emit('error', {'message': message})
        return
    
    # Cartes Métiers avec pouvoirs spéciaux instantanés
    if isinstance(card, JobCard):
        if have_special_power(card.job_name):
            # ✅ MODIFICATION: Ne retirer de la main QUE DANS do_instant_power
            # Passer le card_id pour que do_instant_power le retire
            do_instant_power(card, data, player, game)
            return
        else:
            # Métier normal sans pouvoir spécial instantané
            # Vérifier si le joueur a un métier
            if player.has_job():
                emit('error', {'message': 'Vous avez déjà un métier'})
                return
            
            # Vérifier les études
            can_play, message = card.can_be_played(player)
            if not can_play:
                emit('error', {'message': message})
                return
            
            # Poser le métier normalement
            player.hand.remove(card)
            player.add_card_to_played(card)
            
            # Phase suivante
            next_player(game)
            
            for p in game['players']:
                if p.connected:
                    socketio.emit('game_updated', {
                        'game': get_game_state_for_player(game, p.id),
                        'message': f"{player.name} est devenu {card.job_name}"
                    }, room=p.session_id)
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
                # ✅ NE PAS modifier le pouvoir ici
                cost = 0
            elif isinstance(card, TravelCard) and job.power == 'travel_free':
                cost = 0
        
        # ✅ Appliquer la réduction AVANT d'envoyer le modal
        if isinstance(card, HouseCard) and player.is_married() and cost > 0:
            cost = cost // 2
        
        if cost >= 0:
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
        
        # 🆕 PLUS DE LIMITE DE CARTES
        game['phase'] = 'play'
        
        for p in game['players']:
            if p.connected:
                socketio.emit('game_updated', {
                    'game': get_game_state_for_player(game, p.id),
                    'message': f"{player.name} a posé une carte ({cards_played} carte(s) jouée(s))"
                }, room=p.session_id)
        
        # 🆕 Le joueur décide quand s'arrêter (via le bouton "Terminer")
        # Pas de fin automatique
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