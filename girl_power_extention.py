from flask import request
from flask_socketio import emit
from constants import *
from card_classes import *

@socketio.on('Burn_target_selected')
def handle_troc_target(data):
    print("[start] : Burn_target_selected")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, (DaenerysChild, DragonAnimal)):
        card.confirm_player_selection(data)

@socketio.on('discard_Burn_target_selection')
def handle_discard_troc_target_selection(data):
    print("[start] : discard_Burn_target_selection")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, (DaenerysChild, DragonAnimal)):
        card.discard_player_selection(data)