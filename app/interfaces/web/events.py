"""
app/interfaces/web/events.py — Handlers WebSocket SocketIO.
Fait le lien entre les événements réseau et le core.
"""
from flask_socketio import join_room
from app import socketio
from app.session.room_manager import room_manager
from app.core.player import Player


# ------------------------------------------------------------------ #
#  Helpers                                                             #
# ------------------------------------------------------------------ #

def _get_game_and_player(room_id: str, sid: str):
    """Retourne (game, player) ou (None, None) si introuvable."""
    room = room_manager.get_room(room_id)
    if room is None or room.game is None:
        return None, None
    game = room.game
    player = next((p for p in game.players if p.session_id == sid), None)
    return game, player


def _emit_error(sid: str, message: str):
    socketio.emit("error", {"message": message}, room=sid)


# ------------------------------------------------------------------ #
#  Connexion / Lobby                                                   #
# ------------------------------------------------------------------ #

@socketio.on("join")
def on_join(data: dict):
    """Un joueur rejoint une salle (depuis game.html)."""
    from flask import request
    room_id: str     = data.get("room_id", "")
    player_name: str = data.get("name", "Anonyme")

    room = room_manager.get_room(room_id)
    if room is None:
        return

    # Évite les doublons de session (reconnexion)
    existing = next((p for p in room.players if p.name == player_name), None)
    if existing:
        existing.session_id = request.sid
        existing.connected = True
        join_room(room_id)
        socketio.emit("room_updated", room.to_dict(), room=room_id)
        if room.game:
            room.game.broadcast_update(f"{player_name} s'est reconnecté.")
        return

    player_id = len(room.players)
    player = Player(player_id, player_name)
    player.session_id = request.sid
    room.add_player(player)
    join_room(room_id)

    socketio.emit("room_updated", room.to_dict(), room=room_id)


@socketio.on("join_waiting_room")
def on_join_waiting_room(data: dict):
    """
    Un joueur rejoint le canal socket de la salle d'attente (depuis room.html).
    Distinct de 'join' qui gère l'enregistrement en partie.
    """
    from flask import request
    room_id:     str = data.get("room_id", "")
    player_name: str = data.get("name", "")

    room = room_manager.get_room(room_id)
    if room is None:
        return

    # 1. Rejoindre le canal SocketIO AVANT tout emit
    join_room(room_id)

    # 2. Enregistrer le joueur (hôte ou non)
    if player_name:
        existing = next((p for p in room.players if p.name == player_name), None)
        if existing:
            existing.session_id = request.sid
            existing.connected = True
        elif len(room.players) < room.num_players:
            player_id = len(room.players)
            player = Player(player_id, player_name)
            player.session_id = request.sid
            room.add_player(player)

    state = _room_state(room)

    # 3. Unicast au joueur qui vient de rejoindre (il reçoit toujours son propre état)
    socketio.emit("room_updated", state, room=request.sid)

    # 4. Broadcast aux autres membres déjà dans la salle
    socketio.emit("room_updated", state, room=room_id, skip_sid=request.sid)


@socketio.on("start_game")
def on_start_game(data: dict):
    """L'hôte démarre la partie."""
    room_id: str = data.get("room_id", "")
    room = room_manager.get_room(room_id)
    if room is None:
        return

    from app.cards.loader import load_cards
    import random
    deck = load_cards(deck_config=room.deck_config)
    random.shuffle(deck)

    game = room.start_game(deck)

    # Distribution initiale (5 cartes par joueur)
    for player in game.players:
        for _ in range(5):
            if game.deck:
                player.hand.append(game.get_card_from_deck())

    game.phase = "draw"

    # Notifier tous les joueurs de la salle d'attente pour rediriger
    socketio.emit("game_started", {"room_id": room_id}, room=room_id)
    game.broadcast_update("La partie commence !")


@socketio.on("disconnect")
def on_disconnect():
    from flask import request
    for room in room_manager.list_rooms():
        for player in room.players:
            if player.session_id == request.sid:
                player.connected = False
                if room.game:
                    room.game.broadcast_update(f"{player.name} s'est déconnecté.")
                else:
                    # Salle d'attente : mettre à jour la liste
                    socketio.emit("room_updated", _room_state(room), room=room.id)
                return


# ------------------------------------------------------------------ #
#  Salle d'attente — Deck config                                       #
# ------------------------------------------------------------------ #

@socketio.on("update_deck_config")
def on_update_deck_config(data: dict):
    """L'hôte met à jour la config du deck depuis la salle d'attente."""
    from flask import request
    room_id     = data.get("room_id", "")
    deck_config = data.get("deck_config", {})

    room = room_manager.get_room(room_id)
    if room is None:
        return

    # Vérifier que l'émetteur est bien l'hôte
    host_player = next((p for p in room.players if p.name == room.host_id), None)
    if host_player and host_player.session_id != request.sid:
        socketio.emit(
            "deck_config_error",
            {"message": "Seul l'hôte peut modifier le deck"},
            room=request.sid,
        )
        return

    if room.game is not None:
        socketio.emit(
            "deck_config_error",
            {"message": "La partie est déjà en cours"},
            room=request.sid,
        )
        return

    # Valider et nettoyer : ne garder que les counts > 0
    try:
        room.deck_config = {k: int(v) for k, v in deck_config.items() if int(v) > 0}
    except (ValueError, TypeError):
        socketio.emit(
            "deck_config_error",
            {"message": "Config de deck invalide"},
            room=request.sid,
        )
        return

    # Broadcaster à toute la salle (hôte compris, pour confirmer)
    socketio.emit(
        "deck_config_updated",
        {"deck_config": room.deck_config},
        room=room_id,
    )


# ------------------------------------------------------------------ #
#  Actions de tour                                                     #
# ------------------------------------------------------------------ #

@socketio.on("draw_card")
def on_draw_card(data: dict):
    """Un joueur pioche depuis la pioche."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    success, reason = game.draw_card_from_deck(player.id)
    if not success:
        _emit_error(request.sid, reason)
        return

    game.broadcast_update()


@socketio.on("skip_turn")
def on_skip_turn(data: dict):
    """Le joueur confirme qu'il passe son tour."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    success, reason = game.skip_turn(player.id)
    if not success:
        _emit_error(request.sid, reason)


@socketio.on("draw_from_discard")
def on_draw_from_discard(data: dict):
    """Un joueur pioche la dernière carte de la défausse et la joue directement."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    success, reason = game.draw_card_from_discard(player.id)
    if not success:
        _emit_error(request.sid, reason)
        return
    # broadcast_update est déjà appelé dans draw_card_from_discard


@socketio.on("play_card")
def on_play_card(data: dict):
    """Un joueur pose une carte."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    card_id: str = data.get("card_id", "")
    success, reason = game.play_card(player.id, card_id)
    if not success:
        _emit_error(request.sid, reason)


@socketio.on("discard_card")
def on_discard_card(data: dict):
    """Un joueur défausse une carte de sa main pour terminer son tour."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    card_id: str = data.get("card_id", "")
    success, reason = game.discard_card_from_hand(player.id, card_id)
    if not success:
        _emit_error(request.sid, reason)
        return

    game.broadcast_update(f"{player.name} défausse une carte.")


@socketio.on("discard_job")
def on_discard_job(data: dict):
    """Un joueur défausse un de ses métiers (début de tour ou intérimaire)."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    job_id: str | None = data.get("job_id")
    success, reason = game.discard_job_card(player.id, job_id)
    if not success:
        _emit_error(request.sid, reason)
        return

    game.broadcast_update(f"{player.name} se défausse d'un métier.")


@socketio.on("discard_marriage")
def on_discard_marriage(data: dict):
    """Un joueur divorce (défausse son mariage en début de tour)."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    success, reason = game.discard_marriage_card(player.id)
    if not success:
        _emit_error(request.sid, reason)
        return

    game.broadcast_update(f"{player.name} divorce !")


# ------------------------------------------------------------------ #
#  Cartes interactives — Coups durs                                    #
# ------------------------------------------------------------------ #

@socketio.on("confirm_hardship_target")
def on_confirm_hardship_target(data: dict):
    """Confirmation de la cible d'un coup dur — machine à états."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "hardship_target":
        return
    if interaction["player_id"] != player.id:
        _emit_error(request.sid, "Ce n'est pas votre interaction")
        return

    card = game.find_card_by_id(interaction["card_id"])
    if card is None:
        return

    game.pending_interaction = None
    card.resolve(game, player, data)
    game.next_player()
    game.broadcast_update(f"{player.name} joue un coup dur !")


@socketio.on("discard_hardship_target")
def on_discard_hardship_target(data: dict):
    """Annulation du coup dur — la carte reste en main, le tour continue."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "hardship_target":
        return
    if interaction["player_id"] != player.id:
        return

    game.pending_interaction = None
    # La carte reste en main — on ne passe PAS le tour
    game.broadcast_update()


# ------------------------------------------------------------------ #
#  Cartes interactives — Acquisitions (sélection des salaires)         #
# ------------------------------------------------------------------ #

@socketio.on("confirm_salary_selection")
def on_confirm_salary_selection(data: dict):
    """Confirmation de la sélection des salaires pour une acquisition."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "salary_selection":
        return
    if interaction["player_id"] != player.id:
        _emit_error(request.sid, "Ce n'est pas votre interaction")
        return

    card = game.find_card_by_id(interaction["card_id"])
    if card is None:
        return

    game.pending_interaction = None
    card.resolve(game, player, data)
    game.next_player()
    game.broadcast_update(f"{player.name} pose une acquisition.")


@socketio.on("discard_salary_selection")
def on_discard_salary_selection(data: dict):
    """Annulation de la sélection des salaires — la carte reste dans la main."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "salary_selection":
        return
    if interaction["player_id"] != player.id:
        return

    game.pending_interaction = None
    game.broadcast_update(f"{player.name} annule l'acquisition.")


# ------------------------------------------------------------------ #
#  Cartes interactives — Casino                                        #
# ------------------------------------------------------------------ #

@socketio.on("bet_on_casino")
def on_bet_on_casino(data: dict):
    """Un joueur mise au casino."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    if game.casino_card and game.casino_card.is_open:
        game.casino_card.bet_on_casino(game, player)
        game.broadcast_update()


@socketio.on("confirm_casino_bet")
def on_confirm_casino_bet(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_bet_selection"):
        card.confirm_bet_selection(data)


@socketio.on("discard_casino_bet")
def on_discard_casino_bet(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_bet_selection"):
        card.discard_bet_selection(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Médium / Journaliste                          #
# ------------------------------------------------------------------ #

@socketio.on("confirm_medium")
def on_confirm_medium(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)


@socketio.on("confirm_journalist")
def on_confirm_journalist(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Chance / Étoile Filante                       #
# ------------------------------------------------------------------ #

@socketio.on("confirm_chance_card")
def on_confirm_chance(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_card_selection"):
        card.confirm_card_selection(data)


@socketio.on("discard_chance_card")
def on_discard_chance(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_card_selection"):
        card.discard_card_selection(data)


@socketio.on("confirm_star_card")
def on_confirm_star(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_card_selection"):
        card.confirm_card_selection(data)


@socketio.on("discard_star_card")
def on_discard_star(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_card_selection"):
        card.discard_card_selection(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Daenerys / Dragon (brûler une carte)          #
# ------------------------------------------------------------------ #

@socketio.on("confirm_burn_card")
def on_confirm_burn(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_player_selection"):
        card.confirm_player_selection(data)


@socketio.on("discard_burn_card")
def on_discard_burn(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_player_selection"):
        card.discard_player_selection(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Girl Power                                    #
# ------------------------------------------------------------------ #

@socketio.on("confirm_girl_power")
def on_confirm_girl_power(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)


@socketio.on("discard_girl_power")
def on_discard_girl_power(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_selection"):
        card.discard_selection(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Piston (poser un métier)                      #
# ------------------------------------------------------------------ #

@socketio.on("confirm_piston_job")
def on_confirm_piston(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_job_selection"):
        card.confirm_job_selection(data)


@socketio.on("discard_piston_job")
def on_discard_piston(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_job_selection"):
        card.discard_job_selection(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Coup de Foudre                                #
# ------------------------------------------------------------------ #

@socketio.on("confirm_coup_de_foudre")
def on_confirm_coup_de_foudre(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)


@socketio.on("discard_coup_de_foudre")
def on_discard_coup_de_foudre(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_selection"):
        card.discard_selection(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Troc / Redistribution / Sabre                 #
# ------------------------------------------------------------------ #

@socketio.on("confirm_troc")
def on_confirm_troc(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_player_selection"):
        card.confirm_player_selection(data)


@socketio.on("discard_troc")
def on_discard_troc(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_player_selection"):
        card.discard_player_selection(data)


@socketio.on("confirm_redistribution")
def on_confirm_redistribution(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)


@socketio.on("confirm_sabre")
def on_confirm_sabre(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "sabre_selection":
        return
    if interaction["player_id"] != player.id:
        return

    card = game.find_card_by_id(interaction["card_id"])
    game.pending_interaction = None

    if card and hasattr(card, "resolve"):
        card.resolve(game, player, data)

    game.next_player()
    game.broadcast_update(f"{player.name} renvoie un coup dur !")


@socketio.on("discard_sabre")
def on_discard_sabre(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "sabre_selection":
        return
    if interaction["player_id"] != player.id:
        return

    game.pending_interaction = None
    game.next_player()
    game.broadcast_update()


# ------------------------------------------------------------------ #
#  Cartes interactives — Anniversaire                                  #
# ------------------------------------------------------------------ #

@socketio.on("give_birthday_salary")
def on_give_birthday_salary(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "give_salary_to_player"):
        data["player_id"] = player.id
        card.give_salary_to_player(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Vengeance                                     #
# ------------------------------------------------------------------ #

@socketio.on("confirm_vengeance")
def on_confirm_vengeance(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_vengeance_selection"):
        card.confirm_vengeance_selection(data)


@socketio.on("discard_vengeance")
def on_discard_vengeance(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_vengeance_selection"):
        card.discard_vengeance_selection(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Licenciement (sélection métier)               #
# ------------------------------------------------------------------ #

@socketio.on("confirm_licenciement_job")
def on_confirm_licenciement(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_select_job_licenciement"):
        card.confirm_select_job_licenciement(data)


@socketio.on("discard_licenciement_job")
def on_discard_licenciement(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_select_job_licenciement"):
        card.discard_select_job_licenciement(data)


# ------------------------------------------------------------------ #
#  Cartes interactives — Astronaute / Chef des Achats                  #
# ------------------------------------------------------------------ #

@socketio.on("confirm_astronaute")
def on_confirm_astronaute(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)


@socketio.on("discard_astronaute")
def on_discard_astronaute(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_selection"):
        card.discard_selection(data)


@socketio.on("confirm_chef_achats")
def on_confirm_chef_achats(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)


@socketio.on("discard_chef_achats")
def on_discard_chef_achats(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_selection"):
        card.discard_selection(data)


# ------------------------------------------------------------------ #
#  Helpers internes                                                    #
# ------------------------------------------------------------------ #

def _room_state(room) -> dict:
    """Sérialise l'état de la salle d'attente pour le broadcast."""
    return {
        "players": [
            {"name": p.name, "is_host": p.name == room.host_id}
            for p in room.players
        ],
        "num_players": room.num_players,
    }