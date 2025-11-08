"""
Extension pour gérer les pouvoirs spéciaux des métiers et cartes spéciales
"""
from flask import request
from flask_socketio import emit
from constants import *
from card_classes import *



################
# ANNIVERSAIRE
################
@socketio.on('birthday_gift_selected')
def handle_birthday_gift(data):
    """Un joueur offre un salaire pour un anniversaire"""
    print("[start] : handle_birthday_gift")
    card_id = data.get('card_id')
    current_player_id, game, _ = check_game()
    player = game.players[current_player_id]
    card = get_card_by_id(card_id, player.hand)
    print(f"carte récupéré : {player.to_dict()}\n\n{card}\n\n{card_id}")
    if isinstance(card, AnniversaireCard):
        print("ok")
        card.give_salary_to_player(data)


################
# TROC
################
@socketio.on('troc_target_selected')
def handle_troc_target(data):
    """Échanger une carte avec un autre joueur"""
    print("[start] : handle_troc_target")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, TrocCard):
        card.confirm_player_selection(data)

@socketio.on('discard_troc_target_selection')
def handle_discard_troc_target_selection(data):
    """annuler un troc"""
    print("[start] : handle_discard_troc_target_selection")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, TrocCard):
        card.discard_player_selection(data)

####################
# Pitons
####################
@socketio.on('piston_job_selected')
def handle_piston_job(data):
    """Poser un métier sans condition"""
    print("[start] : handle_piston_job")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, PistonCard):
        card.confirm_job_selection(data)

@socketio.on("piston_job_cancel")
def handle_piston_cancel(data):
    """annule le fait d'utiliser piston"""
    print("[start] : handle_piston_cancel")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, PistonCard):
        card.discard_job_selection(data)





####################
# Vengeance
####################
@socketio.on('vengeance_selected')
def handle_vengeance(data):
    """Renvoyer un coup dur"""
    print("[start] : handle_vengeance")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, VengeanceCard):
        card.confirm_vengeance_selection(data)
    return

@socketio.on('vengeance_discard')
def handle_discard_vengeance(data):
    """Renvoyer un coup dur"""
    print("[start] : handle_discard_vengeance")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, VengeanceCard):
        card.discard_vengeance_selection(data)
        

####################
# Chance
####################
@socketio.on('chance_card_selected')
def handle_chance_card(data):
    """Choisir une carte parmi 3"""
    print("[start] : handle_chance_card")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    print(card_id, player.name)
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, ChanceCard):
        card.confirm_card_selection(data)
    
@socketio.on('discard_chance_card_selected')
def handle_discard_chance_card(data):
    """Choisir une carte parmi 3"""
    print("[start] : handle_discard_chance_card")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, ChanceCard):
        card.discard_card_selection(data)
    

####################
# Arc en ciel
####################
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

    game.next_player()
    update_all_player(game, f"🌈 {player.name} a repioché {cards_drawn} carte(s) ({cards_played} posées + {cards_discarded} défaussées + {card_bets} pariée - 1)")


####################
# Etoile Filante
####################
@socketio.on('star_card_selected')
def handle_star_card_selected(data):
    """Choisir une carte parmi 3"""
    print("[start] : handle_star_card_selected")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, EtoileFilanteCard):
        card.confirm_card_selection(data)

@socketio.on('discard_star_card_selected')
def handle_discard_star_card(data):
    """Choisir une carte parmi 3"""
    print("[start] : handle_discard_chance_card")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, EtoileFilanteCard):
        card.discard_card_selection(data)
 
 
####################
# Casino
####################
@socketio.on('want_to_bet')
def want_bet_to_casino(data):
    print("[start] : want_bet_to_casino")
    player_id, game, _ = check_game()
    card = game.casino_card
    current_player = game.players[player_id]
    if isinstance(card, CasinoCard):
        card.bet_on_casino(game, current_player)

@socketio.on('place_casino_bet')
def handle_casino_confirm_card(data):
    """Choisir une carte parmi 3"""
    print("[start] : handle_casino_confirm_card")
    player_id, game, _ = check_game()
    card = game.casino_card
    if isinstance(card, CasinoCard):
        card.confirm_bet_selection(data)
        

@socketio.on('discard_casino_bet')
def handle_casino_discard_card(data):
    """Choisir une carte parmi 3"""
    print("[start] : handle_casino_discard_card")
    player_id, game, _ = check_game()
    card = game.casino_card
    if isinstance(card, CasinoCard):
        card.discard_bet_selection(data)
 
#####################
# Métiers avec pouvoirs spéciaux
#####################

#####################
# ASTRONAUTE
#####################
@socketio.on('astronaute_card_selected')
def handle_astronaute_card_selected(data):
    print("[start] : handle_astronaute_card_selected")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, AstronauteJob):
        card.confirm_selection(data)

@socketio.on('discard_astronaute_card_selected')
def handle_discard_astronaute_card(data):
    print("[start] : handle_discard_astronaute_card")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, AstronauteJob):
        card.discard_selection(data)


#####################
# MÉDIUM
#####################
@socketio.on('medium_confirm')
def handle_medium_confirmation(data):
    print("[start] : handle_medium_confirmation")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, MediumJob):
        card.confirm_selection(data)


#####################
# JOURNALISTE
#####################
@socketio.on('journaliste_confirm')
def handle_journaliste_confirmation(data):
    print("[start] : handle_journaliste_confirmation")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, JournalisteJob):
        card.confirm_selection(data)

#####################
# CHEF DES VENTES
#####################
@socketio.on('chef_des_ventes_confirm')
def handle_chef_des_ventes_confirmation(data):
    print("[start] : handle_chef_des_ventes_confirmation")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, ChefDesVentesJob):
        card.confirm_selection(data)

@socketio.on('discard_chef_des_ventes')
def handle_discard_chef_des_ventes(data):
    print("[start] : handle_discard_chef_des_ventes")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, ChefDesVentesJob):
        card.discard_selection(data)

#####################
# CHEF DES ACHATS
#####################
@socketio.on('chef_des_achats_confirm')
def handle_chef_des_achats_confirmation(data):
    print("[start] : handle_chef_des_achats_confirmation")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, ChefDesAchatsJob):
        card.confirm_selection(data)

@socketio.on('discard_chef_des_achats')
def handle_discard_chef_des_achats(data):
    print("[start] : handle_discard_chef_des_achats")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, ChefDesAchatsJob):
        card.discard_selection(data)



