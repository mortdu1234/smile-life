"""
Extension pour gérer les pouvoirs spéciaux des métiers et cartes spéciales
"""
from turtle import update
from flask import request
from flask_socketio import emit
from constants import *
from card_classes import *
import random


@socketio.on('handle_play_special_card')
def handle_play_special_card(data):
    """Jouer une carte spéciale"""
    print("[start]: handle_play_special_card")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()

    if game.current_player != player_id:
        emit('error', {'message': 'Ce n\'est pas votre tour'})
        return
    
    player = game.players[player_id]
    
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
        other_players = [p for i, p in enumerate(game.players) if p.connected and i != player_id]
        
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

        next_player(game)
        update_all_player(game, f"🎂 C'est l'anniversaire de {player.name} !")
        
    elif special_type == 'troc':
        other_players = [{'id': i, 'name': p.name, 'hand_count': len(p.hand)} 
                        for i, p in enumerate(game.players) 
                        if p.connected and i != player_id and len(p.hand) > 0]
        
        if not other_players:
            emit('error', {'message': 'Aucun joueur avec des cartes disponibles'})
            return
        
        player.hand.remove(card)
        game.pending_special = {
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
        game.pending_special = {
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
                        for i, p in enumerate(game.players) 
                        if p.connected and i != player_id]
        
        player.hand.remove(card)
        player.add_card_to_played(card)
        game.pending_special = {
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
        if len(game.deck) < 3:
            emit('error', {'message': 'Pas assez de cartes dans la pioche'})
            return
        
        choices = [game.deck.pop() for _ in range(3)]
        
        emit('select_chance_card', {
            'cards': [c.to_dict() for c in choices]
        })
        
        game.pending_special = {
            'type': 'chance',
            'choices': choices,
            'player_id': player_id
        }
    
    elif special_type == 'arc en ciel':
        player.hand.remove(card)
        player.add_card_to_played(card)
        
        game.pending_special = {
            'type': 'arc_en_ciel',
            'player_id': player_id,
            'card_bets': 0,
            'cards_played': 0, 
            'cards_discarded': 0,
            'max_cards': 3
        }
        
        game.phase = 'play'
        update_all_player(game, f"🌈 {player.name} active l'Arc-en-ciel !")    
        
    elif special_type == 'etoile filante':
        player.hand.remove(card)
        player.add_card_to_played(card)
        if not game.discard:
            emit('error', {'message': 'La défausse est vide'})
            return
        
        emit('select_from_discard', {
            'discard_cards': [c.to_dict() for c in game.discard]
        })

    elif special_type == 'heritage':
        player.heritage += 3
        player.hand.remove(card)
        player.add_card_to_played(card)
        
        next_player(game)
        update_all_player(game, f"{player.name} a reçu un héritage de 3 💰")
    
    elif special_type == 'tsunami':
        affected = []
        all_cards = []
        
        player.hand.remove(card)
        player.add_card_to_played(card)

        for p in game.players:
            if p.connected and len(p.hand) > 0:
                all_cards.extend(p.hand)
                p.hand = []
                affected.append(p.name)
        
        random.shuffle(all_cards)
        
        connected_players = [p for p in game.players if p.connected]
        if connected_players and all_cards:
            cards_per_player = len(all_cards) // len(connected_players)
            extra_cards = len(all_cards) % len(connected_players)
            
            card_index = 0
            for i, p in enumerate(connected_players):
                cards_to_give = cards_per_player + (1 if i < extra_cards else 0)
                p.hand = all_cards[card_index:card_index + cards_to_give]
                card_index += cards_to_give
        
        
        next_player(game)
        
        message = f"🌊 Tsunami ! Les cartes de {', '.join(affected)} ont été mélangées et redistribuées !" if affected else "🌊 Tsunami ! Personne n'avait de cartes"
        update_all_player(game, message)
    
    elif special_type == 'casino':
        player.hand.remove(card)
        player.add_card_to_played(card)
        
        game.casino['open'] = True
        game.casino['first_bet'] = None
        game.casino['second_bet'] = None
        game.casino['opener_id'] = player_id  # Mémoriser qui a ouvert
        
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
            next_player(game)
            update_all_player(game, f"🎰 {player.name} a ouvert le casino !")
        
        return

@socketio.on('birthday_gift_selected')
def handle_birthday_gift(data):
    """Un joueur offre un salaire pour un anniversaire"""
    print("[start] : handle_birthday_gift")
    salary_id = data.get('salary_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    salary = None
    for s in player.played["vie professionnelle"]:
        if isinstance(s, SalaryCard) and s.id == salary_id:
            salary = s
            break
    
    if salary:
        birthday_player_id = (game.current_player - 1) % game.num_players
        birthday_player = game.players[birthday_player_id]
        
        player.remove_card_from_played(salary)
        birthday_player.add_card_to_played(salary)
        
        update_all_player(game, f"🎂 {player.name} offre un salaire à {birthday_player.name}")
        
@socketio.on('troc_target_selected')
def handle_troc_target(data):
    """Échanger une carte avec un autre joueur"""
    print("[start] : handle_troc_target")
    target_id = data.get('target_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    target = game.players[target_id]
    
    if not player.hand or not target.hand:
        emit('error', {'message': 'Impossible d\'échanger'})
        return
    
    troc_card = game.pending_special['card']
    
    card1 = random.choice(player.hand)
    card2 = random.choice(target.hand)
    
    player.hand.remove(card1)
    target.hand.remove(card2)
    player.hand.append(card2)
    target.hand.append(card1)
    
    player.add_card_to_played(troc_card)
    game.pending_special = None
    
    next_player(game)
    update_all_player(game, f"🔄 {player.name} a échangé une carte avec {target.name}")

@socketio.on('piston_job_selected')
def handle_piston_job(data):
    """Poser un métier sans condition"""
    print("[start] : handle_piston_job")
    job_id = data.get('job_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    job = None
    for c in player.hand:
        if c.id == job_id and isinstance(c, JobCard):
            job = c
            player.hand.remove(c)
            break
    
    if not job:
        emit('error', {'message': 'Métier non trouvé dans votre main'})
        return
    
    player.add_card_to_played(job)
    game.pending_special = None

    if have_special_power(job.job_name):
        # Exécuter le pouvoir instantané directement (pas via do_instant_power)
        job_name = job.job_name

        if game.deck:
            player.hand.append(game.deck.pop())
        
        if job_name == "chef des ventes":
            handle_chef_des_ventes(player, game)
        elif job_name == "chef des achats":
            handle_chef_des_achats(player, game)
        elif job_name == "chercheur":
            handle_chercheur(player, game)
        elif job_name == "journaliste":
            handle_journaliste(player, game)
        elif job_name == "médium":
            handle_medium(player, game)
        elif job_name == "astronaute":
            handle_astronaute(player, game)
    else:
        next_player(game)

@socketio.on("piston_job_cancel")
def handle_piston_cancel(data):
    """annule le fait d'utiliser piston"""
    print("[start] : handle_piston_cancel")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    piston = None
    for card in player.played["cartes speciales"]:
        if isinstance(card, SpecialCard) and card.special_type == "piston":
            piston = card
            break

    if piston:
        player.remove_card_from_played(piston)
        player.hand.append(piston)
        
        game.phase = 'play'
        update_all_player(game, f"{player.name} a annulé une carte")
        print("le joueur a annulé piston")

@socketio.on('vengeance_selected')
def handle_vengeance(data):
    """Renvoyer un coup dur"""
    print("[start] : handle_vengeance")
    hardship_type = data.get('hardship_type')
    target_id = data.get('target_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    target = game.players[target_id]
    
    if hardship_type in player.received_hardships:
        player.received_hardships.remove(hardship_type)
        
        hardship_card = HardshipCard(hardship_type)
        success, message = apply_hardship_effect(game, hardship_card, target, player)
        
        vengeance_card = game.pending_special['card']
        player.add_card_to_played(vengeance_card)
        game.pending_special = None
        
        next_player(game)
        update_all_player(game, f"⚔️ {player.name} se venge sur {target.name} : {message}")
        
@socketio.on('chance_card_selected')
def handle_chance_card(data):
    """Choisir une carte parmi 3"""
    print("[start] : handle_chance_card")
    card_id = data.get('card_id')
    _, game, _ = check_game()
    
    if not game.get('pending_special') or game.pending_special['type'] != 'chance':
        return
    
    choices = game.pending_special['choices']
    selected = None
    
    for card in choices:
        if card.id == card_id:
            selected = card
            choices.remove(card)
            break
    
    if selected:
        player = game.players[game.pending_special['player_id']]
        player.hand.append(selected)
        
        game.deck.extend(choices)
        random.shuffle(game.deck)
        
        game.pending_special = None
        update_all_player(game, "")

@socketio.on('arc_en_ciel_finished')
def handle_arc_finished(data):
    """Terminer le mode arc-en-ciel et repiocher"""
    print("[start] : handle_arc_finished")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    game = games[game_id]
    player = game.players[session_info['player_id']]
    
    if not game.get('pending_special') or game.pending_special.get('type') != 'arc_en_ciel':
        return
    
    cards_played = game.pending_special.get('cards_played', 0)
    cards_discarded = game.pending_special.get('cards_discarded', 0)
    card_bets = game.pending_special.get('card_bets', 0)
    
    total_cards_used = cards_played + cards_discarded + card_bets
    cards_to_draw = max(0, total_cards_used)
    
    cards_drawn = 0
    for _ in range(cards_to_draw):
        if game.deck:
            player.hand.append(game.deck.pop())
            cards_drawn += 1
    
    game.pending_special = None

    next_player(game)
    update_all_player(game, f"🌈 {player.name} a repioché {cards_drawn} carte(s) ({cards_played} posées + {cards_discarded} défaussées + {card_bets} pariée - 1)")

@socketio.on('discard_card_selected')
def handle_discard_card_selected(data):
    """Choisir une carte de la défausse (étoile filante)"""
    print("[start] : handle_discard_card_selected")
    card_id = data.get('card_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    card = None
    for c in game.discard:
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
    
    game.discard.remove(card)
    player.add_card_to_played(card)
    
    next_player(game)
    update_all_player(game, f"⭐ {player.name} a récupéré une carte de la défausse")

@socketio.on('place_casino_bet')
def handle_casino_bet(data):
    """Placer un pari au casino"""
    print("[start] : handle_casino_bet")
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
    player = game.players[player_id]
    
    # Vérifier que le casino est ouvert
    if not game.casino['open']:
        emit('error', {'message': 'Le casino est fermé'})
        return
    
    # Vérifier qu'il y a de la place
    if game.casino['first_bet'] and game.casino['second_bet']:
        emit('error', {'message': 'Le casino est plein'})
        return
    
    # ✅ CHERCHER LE SALAIRE DANS LA MAIN
    
    salary_card = get_card_by_id(salary_id, player.hand)
    
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
    
    # Premier pari - ✅ STOCKER UNIQUEMENT LES DONNÉES SÉRIALISABLES
    if not game.casino['first_bet']:
        game.casino['first_bet'] = {
            'player_id': player_id,
            'player_name': player.name,  # ✅ AJOUT
            'salary_id': salary_card.id,  # ✅ AJOUT
            'salary_level': salary_card.level  # ✅ STOCKER LE NIVEAU
        }
        
        message = f"🎰 {player.name} a misé au casino (1er pari - montant secret)"
        
        # Si c'est l'ouvreur, on passe au joueur suivant
        if is_opener:
            if not (game.get('pending_special') and game.pending_special.get('type') == 'arc_en_ciel'):
                next_player(game)
            else:
                game.pending_special['card_bets'] += 1
        
        update_all_player(game, message)
    
    # Deuxième pari - résolution
    else:
        game.casino['second_bet'] = {
            'player_id': player_id,
            'player_name': player.name,  # ✅ AJOUT
            'salary_id': salary_card.id,  # ✅ AJOUT
            'salary_level': salary_card.level  # ✅ STOCKER LE NIVEAU
        }
        
        first_bet = game.casino['first_bet']
        second_bet = game.casino['second_bet']
        
        first_player = game.players[first_bet['player_id']]
        second_player = game.players[second_bet['player_id']]
        
        if first_player.id == second_player.id:
            print("YOUSK : le meme joueur a jouer au casino 2 fois")

        # ✅ RÉCUPÉRER LES CARTES SALAIRE DEPUIS LES IDs
        first_salary = get_card_by_id(first_bet['salary_id'], [salary_card])  # Peut être dans la main du second joueur
        # Chercher partout
        for p in game.players:
            if not first_salary:
                first_salary = get_card_by_id(first_bet['salary_id'], p.hand)
            if not first_salary:
                # Chercher dans les cartes jouées
                for cards in p.played.values():
                    first_salary = get_card_by_id(first_bet['salary_id'], cards)
                    if first_salary:
                        break
        
        second_salary = salary_card  # Le second est forcément celui qu'on vient de jouer

        # Comparer les niveaux
        if first_bet['salary_level'] == second_bet['salary_level']:
            # Égalité : le deuxième joueur gagne les deux salaires
            if first_salary:
                second_player.add_card_to_played(first_salary)
            second_player.add_card_to_played(second_salary)
            
            message = f"🎰 Casino ! {second_player.name} GAGNE les deux salaires (égalité) !"
        else:
            # Différent : le premier joueur gagne les deux salaires
            if first_salary:
                first_player.add_card_to_played(first_salary)
            first_player.add_card_to_played(second_salary)
            
            message = f"🎰 Casino ! {first_player.name} GAGNE les deux salaires !"
        
        # Fermer le casino après résolution
        game.casino['first_bet'] = None
        game.casino['second_bet'] = None
        game.casino['opener_id'] = None
        
        if not (game.get('pending_special') and game.pending_special.get('type') == 'arc_en_ciel'):
            next_player(game)
        else:
            game.pending_special['card_bets'] += 1
            
        update_all_player(game, message)
    
    # ✅ SUPPRIMÉ : next_player et update_all_player dupliqués
    
@socketio.on('skip_casino_bet')
def handle_skip_casino_bet(data):
    """L'ouvreur du casino décide de ne pas miser"""
    print("[start] : handle_skip_casino_bet")
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
    player = game.players[player_id]
    
    # Vérifier que c'est bien l'ouvreur
    if game.casino.get('opener_id') != player_id:
        emit('error', {'message': 'Seul l\'ouvreur peut refuser de miser'})
        return

    if game.get('pending_special') and game.pending_special.get('type') == 'arc_en_ciel':
        # Le casino reste ouvert, on passe au joueur suivant
        game.pending_special['cards_played'] += 1
    else:
        next_player(game)

    update_all_player(game, f"🎰 {player.name} n'a pas misé. Le casino reste ouvert !")

#####################
# Métiers avec pouvoirs spéciaux
#####################
def have_special_power(job_name):
    """Vérifier si un métier a un pouvoir spécial"""
    print(" [start] : have_special_power")
    # Liste des métiers avec pouvoirs spéciaux instantanés
    special_jobs = [
        "astronaute", "chef des ventes", "chef des achats", 
        "chercheur", "journaliste", "médium", "bandit"
    ]   
    return job_name in special_jobs

def do_instant_power(job_card, data, player: Player, game):
    """Exécute le pouvoir instantané d'un métier"""
    print("[start] : do_instant_power")
    job_name = job_card.job_name
    
    if job_card in player.hand:
        player.hand.remove(job_card)
    player.add_card_to_played(job_card)
    
    if job_name == "chef des ventes":
        handle_chef_des_ventes(player, game)
    elif job_name == "chef des achats":
        handle_chef_des_achats(player, game)
    elif job_name == "chercheur":
        handle_chercheur(player, game)
    elif job_name == "journaliste":
        handle_journaliste(player, game)
    elif job_name == "médium":
        handle_medium(player, game)
    elif job_name == "astronaute":
        handle_astronaute(player, game)
    elif job_name == "bandit":
        print("le joeuur a été bandit")
        player.has_been_bandit = True
        next_player(game)  
        update_all_player(game, f"🚀 {player.name} est devenu bandit")


# ASTRONAUTE
def handle_astronaute(player, game):
    """Astronaute : permettre au joueur de jouer une carte de la défausse"""
    print("[start] : handle_astronaute")
    
    # Filtrer les cartes de la défausse (exclure les coups durs)
    available_cards = [c for c in game.discard if not isinstance(c, HardshipCard)]
    
    if not available_cards:
        # Aucune carte disponible dans la défausse
        next_player(game)
        update_all_player(game, f"🚀 {player.name} est devenu astronaute (défausse vide)")
        return
    
    # Envoyer la liste des cartes disponibles au joueur
    emit('select_astronaute_card', {
        'cards': [c.to_dict() for c in available_cards]
    })

@socketio.on('astronaute_card_selected')
def handle_astronaute_selection(data):
    """Astronaute : sélectionner une carte de la défausse"""
    print("[start] : handle_astronaute_selection")
    card_id = data.get('card_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    # Trouver la carte dans la défausse
    selected_card = None
    for card in game.discard:
        if card.id == card_id:
            selected_card = card
            break
    
    if not selected_card:
        emit('error', {'message': 'Carte non trouvée'})
        return
    
    # Vérifier que le joueur peut la poser
    can_play, message = selected_card.can_be_played(player)
    if not can_play:
        emit('error', {'message': f'Impossible de poser cette carte : {message}'})
        return
    
    # Retirer de la défausse et poser
    game.discard.remove(selected_card)

    # ✅ Vérifier si c'est une acquisition (nécessite paiement)
    if isinstance(selected_card, (HouseCard, TravelCard)):
        # Ajouter à la main pour gérer le paiement
        player.hand.append(selected_card)
        
        # Repiocher une carte bonus
        # if game.deck:
        #    player.hand.append(game.deck.pop())
        
        # Rester en phase play pour que le joueur puisse acheter
        game.phase = 'play'
        
        update_all_player(game, f"🚀 {player.name} a récupéré une acquisition - achetez-la maintenant")
    else:
        # Carte normale : poser directement
        player.add_card_to_played(selected_card)

# CHEF DES VENTES
@socketio.on('chef_ventes_salary_selected')
def handle_chef_ventes_selection(data):
    """Chef des ventes : sélectionner un salaire de la défausse"""
    print("[start]: handle_chef_ventes_selection")
    salary_id = data.get('salary_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    # Trouver le salaire dans la défausse
    selected_salary = None
    for card in game.discard:
        if card.id == salary_id and isinstance(card, SalaryCard):
            selected_salary = card
            break
    
    if not selected_salary:
        emit('error', {'message': 'Salaire non trouvé'})
        return
    
    # Vérifier que le joueur peut le poser
    can_play, message = selected_salary.can_be_played(player)
    if not can_play:
        emit('error', {'message': f'Impossible de poser ce salaire : {message}'})
        return
    
    # Retirer de la défausse et poser
    game.discard.remove(selected_salary)
    player.add_card_to_played(selected_salary)
    
    next_player(game)
    update_all_player(game, f"💼 {player.name} a récupéré un salaire de la défausse grâce au chef des ventes")

def handle_chef_des_ventes(player, game):
    """Chef des ventes : afficher les salaires de la défausse"""
    print("[start]: handle_chef_des_ventes")
    available_salaries = [c for c in game.discard if isinstance(c, SalaryCard) and c.level <= 3]
    
    if not available_salaries:
        # si il n'y a pas de salaire dans la défausse jsute poser le métier
        next_player(game)
        update_all_player(game, f"🛒 {player.name} est devenu chef des achats (aucune acquisition disponible)")
        return
    
    emit('select_chef_ventes_salary', {
        'salaries': [s.to_dict() for s in available_salaries]
    })

@socketio.on('cancel_chef_ventes_salary_selection')
def handle_cancel_chef_vente_job():
    print("[start] : handle_cancel_chef_vente_job")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    # Trouver le métier chef des achats dans les cartes posées
    chef_ventes = None
    for card in player.played["vie professionnelle"]:
        if isinstance(card, JobCard) and card.job_name == 'chef des ventes':
            chef_ventes = card
            break
    
    if chef_ventes:
        # Retirer des cartes posées et remettre dans la main
        player.remove_card_from_played(chef_ventes)
        player.hand.append(chef_ventes)
        
        # Rester en phase play pour que le joueur puisse jouer autre chose
        game.phase = 'play'
        update_all_player(game, f"{player.name} a annulé le chef des achats")

# CHEF DES ACHATS
def handle_chef_des_achats(player, game):
    """Chef des achats : afficher les acquisitions de la défausse"""
    print("[start]: handle_chef_des_achats")
    available_acquisitions = [c for c in game.discard if isinstance(c, HouseCard)]
    
    if not available_acquisitions:
        # Pas d'acquisitions : poser le métier normalement et passer au joueur suivant
        next_player(game)
        update_all_player(game, f"🛒 {player.name} est devenu chef des achats (aucune acquisition disponible)")
        return
    
    # ✅ Stocker qu'on est en mode chef des achats pour permettre l'annulation
    game.pending_special = {
        'type': 'chef_achats_selection',
        'player_id': player.id
    }
    
    emit('select_chef_achats_acquisition', {
        'acquisitions': [a.to_dict() for a in available_acquisitions]
    })

@socketio.on('chef_achats_acquisition_selected')
def handle_chef_achats_selection(data):
    """Chef des achats : sélectionner une acquisition de la défausse et l'acheter"""
    print("[start]: handle_chef_achats_selection")
    acquisition_id = data.get('acquisition_id')
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    # Trouver l'acquisition dans la défausse
    selected_acquisition = None
    for card in game.discard:
        if card.id == acquisition_id and isinstance(card, HouseCard):
            selected_acquisition = card
            break
    
    if not selected_acquisition:
        emit('error', {'message': 'Acquisition non trouvée'})
        return

    # ✅ Changer le type de pending_special
    
    # Calculer le coût
    job = player.get_job()
    cost = selected_acquisition.cost
    
    # Appliquer réduction mariage si applicable
    if isinstance(selected_acquisition, HouseCard) and player.is_married() and cost > 0:
        cost = cost // 2
    
    # ✅ STOCKER l'ID de la carte dans pending_special avec le nouveau type
    game.pending_special = {
        'type': 'chef_achats_purchase',
        'acquisition_id': acquisition_id,
        'player_id': player_id
    }
    
    # Proposer l'achat avec sélection de salaires
    available_salaries = [c for c in player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
    
    emit('select_salaries_for_acquisition_chef_achat', {
        'card': selected_acquisition.to_dict(),
        'required_cost': cost,
        'available_salaries': [s.to_dict() for s in available_salaries],
        'heritage_available': player.heritage
    })

@socketio.on('cancel_chef_achats_job')
def handle_cancel_chef_achats_job():
    """Annuler complètement le chef des achats - le métier retourne dans la main"""
    print("[start] : handle_cancel_chef_achats_job")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    # Trouver le métier chef des achats dans les cartes posées
    chef_achats = None
    for card in player.played["vie professionnelle"]:
        if isinstance(card, JobCard) and card.job_name == 'chef des achats':
            chef_achats = card
            break
    
    if chef_achats:
        # Retirer des cartes posées et remettre dans la main
        player.remove_card_from_played(chef_achats)
        player.hand.append(chef_achats)
        
        # Nettoyer pending_special (chef_achats_selection ou chef_achats_purchase)
        if game.get('pending_special') and game.pending_special.get('type') in ['chef_achats_selection', 'chef_achats_purchase']:
            game.pending_special = None
        
        # Rester en phase play pour que le joueur puisse jouer autre chose
        game.phase = 'play'
        update_all_player(game, f"{player.name} a annulé le chef des achats")

@socketio.on('cancel_chef_achats_purchase')
def handle_cancel_chef_achats():
    """Annuler un achat chef des achats"""
    print("[start] : handle_cancel_chef_achats")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    game = games[game_id]
    
    if game.get('pending_special') and game.pending_special.get('type') == 'chef_achats_purchase':
        game.pending_special = None
    update_all_player(game, "poser le métier chef des achats sans acheter")

@socketio.on('confirm_chef_achats_without_purchase')
def handle_confirm_chef_achats_without_purchase():
    """Confirmer le chef des achats sans acheter - le métier reste posé"""
    print("[start] : handle_confirm_chef_achats_without_purchase")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    # Le métier est déjà posé, on passe juste au joueur suivant
    next_player(game)
    update_all_player(game, f"💼 {player.name} est devenu chef des achats (sans achat)")

# CHERCHEUR
@socketio.on('chercheur_confirm')
def handle_chercheur_confirmation(data):
    """Chercheur : confirmer et continuer"""
    print("[start] : handle_chercheur_confirmation")
    session_info = player_sessions.get(request.sid)
    give_card(data)

    if not session_info:
        return
    
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    next_player(game)
    update_all_player(game, f"🔬 {player.name} a posé le métier chercheur et pioché une carte supplémentaire")

def handle_loose_chercheur_job():
    """retire une carte de la main du joueur"""
    print("[start] : handle_loose_chercheur_job")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]

    idx_selected_card = random.randint(0, len(player.hand)-1)
    selected_card = player.hand.pop(idx_selected_card)
    game.discard.append(selected_card)
    return


def handle_chercheur(player, game):
    """Chercheur : piocher une carte en plus"""
    # La carte est déjà posée dans do_instant_power, on pioche juste une carte bonus
    print("[start] : handle_chercheur")
    if game.deck:
        extra_card = game.deck.pop()
        player.hand.append(extra_card)
    
    # Passer au joueur suivant
    next_player(game)
    update_all_player(game, f"🔬 {player.name} est devenu chercheur et pioche une carte bonus")


# JOURNALISTE
@socketio.on('journaliste_confirm')
def handle_journaliste_confirmation(data):
    """Journaliste : afficher les mains puis continuer"""
    print("[start] : handle_journaliste_confirmation")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]

    next_player(game)
    update_all_player(game, f"📰 {player.name} a posé le métier journaliste")

def handle_journaliste(player, game):
    """Journaliste : afficher les mains de tous les joueurs"""
    # Retirer le métier journaliste de la main (il sera posé dans app.py)
    # Ici on prépare juste les données
    print("[start] : handle_journaliste")
    hands_info = {}
    for p in game.players:
        if p.connected and p.id != player.id:
            hands_info[p.name] = [c.to_dict() for c in p.hand]
    
    emit('show_all_hands', {
        'hands': hands_info
    })

# MÉDIUM
@socketio.on('medium_confirm')
def handle_medium_confirmation(data):
    """Médium : afficher les 13 prochaines cartes puis continuer"""
    print("[start] : handle_medium_confirmation")
    session_info = player_sessions.get(request.sid)
    
    if not session_info:
        return
    
    game_id = session_info['game_id']
    player_id = session_info['player_id']
    game = games[game_id]
    player = game.players[player_id]
    
    next_player(game)
    update_all_player(game, f"🔮 {player.name} a posé le métier médium")

def handle_medium(player, game):
    """Médium : afficher les 13 prochaines cartes de la pioche"""
    print("[start] : handle_medium")
    # Montrer les 13 prochaines cartes sans les retirer
    next_cards_count = min(13, len(game.deck))
    next_cards = game.deck[-next_cards_count:] if next_cards_count > 0 else []
    next_cards = list(reversed(next_cards)) 

    emit('show_next_cards', {
        'cards': [c.to_dict() for c in next_cards],
        'total': len(game.deck)
    })