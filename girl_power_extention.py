from flask import request
from flask_socketio import emit
from constants import check_game, get_card_by_id, socketio
from card_classes import *

#############################
# BURN
#############################
@socketio.on('Burn_target_selected')
def handle_burn_target(data):
    print("[start] : handle_burn_target")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, (DaenerysChild, DragonAnimal)):
        card.confirm_player_selection(data)

@socketio.on('discard_Burn_target_selection')
def handle_discard_burn_target_selection(data):
    print("[start] : handle_discard_burn_target_selection")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, (DaenerysChild, DragonAnimal)):
        card.discard_player_selection(data)
###############################
# SABRE
###############################
@socketio.on('sabre_selected')
def handle_sabre_target(data):
    print("[start] : handle_sabre_target")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.get_card_from_hand())
    if isinstance(card, SabreCard):
        card.confirm_sabre_selection(data)

@socketio.on('sabre_discard')
def handle_discard_sabre_target_selection(data):
    print("[start] : handle_discard_sabre_target_selection")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.get_card_from_hand())
    if isinstance(card, SabreCard):
        card.discard_sabre_selection(data)
#############################
# erreur d'étiquetage
#############################
@socketio.on('erreur_etiquetage_target_selected')
def handle_erreur_etiquetage_target(data):
    print("[start] : handle_erreur_etiquetage_target", data)
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, ErreurDetiquetageCard):
        card.confirm_target_selection(data)

@socketio.on('erreur_etiquetage_discard')
def handle_discard_erreur_etiquetage_selection(data):
    print("[start] : handle_discard_erreur_etiquetage_selection", data)
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, ErreurDetiquetageCard):
        card.discard_selection(data)

@socketio.on('erreur_etiquetage_children_selected')
def handle_erreur_etiquetage_child(data):
    print("[start] : handle_erreur_etiquetage_child", data)
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, ErreurDetiquetageCard):
        card.confirm_children_selection(data)
###############################
# Coup de Foudre
###############################
@socketio.on('coup_de_foudre_selected')
def handle_coup_de_foudre_target(data):
    print("[start] : handle_coup_de_foudre_target")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.get_card_from_hand())
    if isinstance(card, CoupDeFoudreCard):
        card.confirm_selection(data)

@socketio.on('coup_de_foudre_discard')
def handle_discard_coup_de_foudre_target_selection(data):
    print("[start] : handle_discard_coup_de_foudre_target_selection")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.get_card_from_hand())
    if isinstance(card, CoupDeFoudreCard):
        card.discard_selection(data)
###############################
# Girl Power
###############################
@socketio.on('girl_power_card_selected')
def handle_girl_power_card_selected(data):
    print("[start] : handle_girl_power_card_selected")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.get_card_from_hand())
    if isinstance(card, GirlPowerCard):
        card.confirm_selection(data)

@socketio.on('girl_power_discard')
def handle_girl_power_discard(data):
    print("[start] : handle_girl_power_discard")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.get_card_from_hand())
    if isinstance(card, GirlPowerCard):
        card.discard_selection(data)
###############################
# Redistribution des taches
###############################
@socketio.on('redistribution_finish')
def handle_redistribution_selected(data):
    print("[start] : handle_redistribution_selected")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.get_card_from_hand())
    if isinstance(card, RedistributionDesTachesCard):
        card.confirm_selection(data)
