from flask_socketio import emit
from card_classes import *
from constants import app, socketio, check_game, update_all_player
from special_power import *
import init # pour avoir la route initiale /  # noqa: F401


#######################
# Passer son tour / tour suivant
#######################
@socketio.on('skip_turn')
def handle_skip_turn(data):
    """Passer son tour manuellement"""
    print("[start]: handle_skip_turn")
    player_id, game, _ = check_game()

    if game.current_player != player_id:
        emit('error', {'message': 'Ce n\'est pas votre tour'})
        return
    
    player = game.players[player_id]
    
    if player.skip_turns > 0:
        player.skip_turns -= 1
        message = f"{player.name} passe son tour ({player.skip_turns} tour(s) restant(s))"
    else:
        message = f"{player.name} passe son tour volontairement"
    
    game.next_player()
    update_all_player(game, message)

#######################
# Défausser une carte déja posée
#######################
@socketio.on('discard_played_card')
def handle_discard_played_card(data):
    """Défausser une carte déjà posée (métier, mariage ou adultère)"""
    print("[start]: handle_discard_played_card")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    current_player = game.players[player_id]
    card = None
    for c in current_player.get_all_played_cards():
        if c.id == card_id:
            card = c
            if getattr(card, "discard_play_card"):
                card.discard_play_card(game, current_player)
            break
    update_all_player(game, "")


##########################
# AquisitionCards
##########################
@socketio.on('select_salaries_for_purchase')
def handle_select_salaries(data):
    """Le joueur sélectionne les salaires pour payer une acquisition"""
    print("[start] : handle_select_salaries")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]

    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, AquisitionCard):
        card.confirm_salary_selection(data)
    
@socketio.on('cancel_select_salaries_for_purchase')
def handle_cancel_select_salarie(data):
    """le joueur annule la sélection d'achat d'une carte"""
    print("[start]: handle_cancel_select_salarie")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if card is not None and isinstance(card, AquisitionCard):
        card.discard_salary_selection(data)
    
#########################
# Hardship
#########################
@socketio.on('select_target_for_hardship')
def handle_select_target(data):
    print("[start] : handle_select_target")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, HardshipCard):
        card.confirm_target_selection(data)

@socketio.on('cancel_select_target_for_hardship')
def handle_cancel_select_target(data):
    print("[start] : handle_cancel_select_target")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    player = game.players[player_id]
    card = get_card_by_id(card_id, player.hand)
    if isinstance(card, HardshipCard):
        card.discard_target_selection(data)
    



#######################
# Piocher
#######################
@socketio.on('draw_card')
def handle_draw_card(data):
    """Piocher une carte"""
    print("[start]: handle_draw_card")
    source = data.get('source', 'deck')
    player_id, game, game_id = check_game()
    
    if game.current_player != player_id:
        emit('error', {'message': 'Ce n\'est pas votre tour'})
        return
    
    if game.phase != 'draw':
        emit('error', {'message': 'Vous avez déjà pioché'})
        return
    
    player = game.players[player_id]
    
    if source == 'deck':
        if not game.deck:
            scores = [(p.name, p.calculate_smiles(), p.id) for p in game.players if p.connected]
            scores.sort(key=lambda x: x[1], reverse=True)
            print("[appel] : game_over")
            socketio.emit('game_over', {'scores': scores}, room=game_id)
            return
        
        card = game.deck.pop()
        player.hand.append(card)
        game.phase = 'play'
        print(f"Joueur {player_id} a pioché dans le deck, reste {len(game.deck)} cartes")
        
    elif source == 'discard':
        if not game.discard:
            emit('error', {'message': 'Défausse vide'})
            return
        card = game.discard.pop()
        if card.can_be_played(player, game)[0]:
            player.hand.append(card)
            card.play_card(game, player)
            game.next_player()
        else:
            game.discard.append(card)
            emit('error', {'message': 'Vous ne pouvez pas jouer cette carte'})
            return
    update_all_player(game, "")



#######################
# défausser une carte
#######################
@socketio.on('discard_card')
def handle_discard_card(data):
    """Défausser une carte"""
    print("[start]: handle_discard_card")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()
    current_player = game.players[player_id]

    if game.current_player != player_id:
        emit('error', {'message': 'Ce n\'est pas votre tour'})
        return
    
    if game.phase != 'play':
        emit('error', {'message': 'Vous devez d\'abord piocher'})
        return
    
    player = game.players[player_id]

    
    card = None
    for c in player.hand:
        if c.id == card_id:
            card = c
            break
    
    if not card:
        emit('error', {'message': 'Carte non trouvée', 'debug': 'handle_discard_card'})
        return

    player.hand.remove(card)
    game.discard.append(card)
    
    # si on est en mode arc-en-ciel
    if game.arcEnCielMode:
        game.arcEnCielCard.add_card_played(game, current_player)
    else:
        game.next_player()
    update_all_player(game, "")
    

#######################
# Poser une carte
#######################
@socketio.on('play_card')
def handle_play_card(data):
    """Jouer une carte"""
    print("[start]: handle_play_card")
    card_id = data.get('card_id')
    player_id, game, _ = check_game()

    if game.current_player != player_id:
        emit('error', {'message': 'Ce n\'est pas votre tour'})
        return
    
    if game.phase != 'play':
        emit('error', {'message': 'Vous devez d\'abord piocher'})
        return
    
    current_player = game.players[player_id]
    card = get_card_by_id(card_id, current_player.hand)
    
    print(f"info sur la carte : type: {type(card)} id:{card.id}")

    success, message = card.can_be_played(current_player, game)
    if not success:
        emit("error", {'message': message})
        return
    
    card.play_card(game, current_player)
    # gestion du mode arc en ciel
    if game.arcEnCielMode:
        game.arcEnCielCard.add_card_played(game, current_player)
    update_all_player(game, "")
    

if __name__ == '__main__':
    print(f"[INFO] SocketIO async_mode: {socketio.async_mode}")
    print(f"[INFO] System: {os.name}")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)