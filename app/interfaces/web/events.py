"""
app/interfaces/web/events.py — Handlers WebSocket SocketIO.
Fait le lien entre les événements réseau et le core.
"""
from flask_socketio import join_room
from app import socketio
from app.session.room_manager import room_manager
from app.core.player import Player
import traceback

@socketio.on_error_default
def handle_error(e):
    traceback.print_exc()
    print(f"[SOCKETIO ERROR] {e}")

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

                all_disconnected = all(not p.connected for p in room.players)

                if all_disconnected:
                    # Délai de grâce de 30s avant de fermer
                    # (reconnexion possible après refresh)
                    import threading
                    room_id = room.id

                    def _close_if_still_empty():
                        r = room_manager.get_room(room_id)
                        if r is None:
                            return
                        if all(not p.connected for p in r.players):
                            room_manager.delete_room(room_id)
                            socketio.emit("room_closed", {"room_id": room_id})

                    t = threading.Timer(30.0, _close_if_still_empty)
                    t.daemon = True
                    t.start()
                    return

                if room.game:
                    room.game.broadcast_update(f"{player.name} s'est déconnecté.")
                else:
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


@socketio.on("stop_arc_en_ciel")
def on_stop_arc_en_ciel(data: dict):
    """Le joueur arrête volontairement son tour Arc-en-Ciel."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    success, reason = game.stop_arc_en_ciel(player.id)
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
    # game.play_card() gère déjà next_player() et broadcast_update() en interne.
    # Les handlers confirm_* gèrent les cartes interactives (pending_interaction).


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

@socketio.on("confirm_casino_bet")
def on_confirm_casino_bet(data: dict):
    """L'ouvreur mise (ou passe via bet_card_id=None)."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "casino_opener_bet":
        return
    if interaction["player_id"] != player.id:
        return
    card = game.find_card_by_id(interaction["card_id"])
    if card is None:
        return
    card.resolve_opener(game, player, data)

@socketio.on("discard_casino_bet")
def on_discard_casino_bet(data: dict):
    """L'ouvreur annule — le casino ne s'ouvre pas."""
    from flask import request
    print(f"[DEBUG] discard_casino_bet reçu : {data}")
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "casino_opener_bet":
        return
    if interaction["player_id"] != player.id:
        return

    # Annuler : remettre la carte casino en main, fermer le casino
    casino_card = game.find_card_by_id(interaction["card_id"])
    if casino_card:
        casino_card.is_open = False
        game.casino_card = None
        player.hand.append(casino_card)

    game.pending_interaction = None
    game.broadcast_update()


@socketio.on("bet_on_casino")
def on_bet_on_casino(data: dict):
    """Un joueur (non-ouvreur) mise pendant son propre tour."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    # Doit être son tour et en phase play
    if game.current_player != player.id:
        _emit_error(request.sid, "Ce n'est pas votre tour")
        return
    if game.phase != "play":
        _emit_error(request.sid, "Piochez d'abord")
        return
    if not game.casino_card or not game.casino_card.is_open:
        return
    game.casino_card.resolve_second(game, player, data)


# ------------------------------------------------------------------ #
#  POSER UN SALAIRE                          #
# ------------------------------------------------------------------ #

@socketio.on("confirm_salary_placement")
def on_confirm_salary_placement(data: dict):
    """Le joueur a choisi où poser son salaire (normal ou casino)."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "salary_placement":
        _emit_error(request.sid, "Aucune interaction en cours")
        return
    if interaction["player_id"] != player.id:
        _emit_error(request.sid, "Ce n'est pas votre interaction")
        return

    card = game.find_card_by_id(interaction["card_id"])
    if card is None:
        _emit_error(request.sid, "Carte introuvable")
        return

    choice = data.get("choice")  # "normal" ou "casino"
    if choice not in ("normal", "casino"):
        _emit_error(request.sid, "Choix invalide")
        return

    game.pending_interaction = None
    card.resolve_placement(game, player, choice)


@socketio.on("cancel_salary_placement")
def on_cancel_salary_placement(data: dict):
    """Le joueur annule — la carte est encore en main, rien à faire."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "salary_placement":
        return
    if interaction["player_id"] != player.id:
        return

    game.pending_interaction = None
    game.broadcast_update()

# ------------------------------------------------------------------ #
#  Cartes interactives — Médium / Journaliste                          #
# ------------------------------------------------------------------ #

@socketio.on("confirm_medium")
def on_confirm_medium(data: dict):
    """Le joueur ferme la fenêtre Médium — le tour a déjà passé lors de la pose."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    game.broadcast_update(f"{player.name} consulte la pioche.")


@socketio.on("confirm_journalist")
def on_confirm_journalist(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)
    game.next_player()
    game.broadcast_update(f"{player.name} observe les mains.")


# ------------------------------------------------------------------ #
#  Cartes interactives — Chance / Étoile Filante                       #
# ------------------------------------------------------------------ #

@socketio.on("confirm_chance_card")
def on_confirm_chance(data: dict):
    """Joueur choisit une carte parmi les 3 proposées par la Chance."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "chance_selection":
        return
    if interaction["player_id"] != player.id:
        _emit_error(request.sid, "Ce n'est pas votre interaction")
        return

    card = game.find_card_by_id(interaction["card_id"])
    if card is None:
        return

    # Sauvegarder les cartes proposées AVANT d'effacer pending_interaction
    data["offered_cards_objects"] = interaction.get("offered_cards", [])
    game.pending_interaction = None
    card.resolve(game, player, data)
    # Le joueur continue de jouer (phase play) — on ne passe PAS le tour
    game.phase = "play"
    game.broadcast_update(f"{player.name} pioche une carte via la Chance !")


@socketio.on("discard_chance_card")
def on_discard_chance(data: dict):
    """Le joueur annule la Chance — la carte reste en main, phase play continue."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "chance_selection":
        return
    if interaction["player_id"] != player.id:
        return

    # Remettre les 3 cartes au sommet de la pioche
    offered = interaction.get("offered_cards", [])
    for c in reversed(offered):
        game.deck.append(c)

    game.pending_interaction = None
    game.phase = "play"
    game.broadcast_update()


@socketio.on("confirm_star_card")
def on_confirm_star(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_card_selection"):
        card.confirm_card_selection(data)
    game.next_player()
    game.broadcast_update(f"{player.name} récupère une carte de la défausse.")


@socketio.on("discard_star_card")
def on_discard_star(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_card_selection"):
        card.discard_card_selection(data)
    game.next_player()
    game.broadcast_update()


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
    game.next_player()
    game.broadcast_update(f"{player.name} brûle une carte !")


@socketio.on("discard_burn_card")
def on_discard_burn(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_player_selection"):
        card.discard_player_selection(data)
    game.next_player()
    game.broadcast_update()


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
    game.next_player()
    game.broadcast_update(f"{player.name} utilise Girl Power !")


@socketio.on("discard_girl_power")
def on_discard_girl_power(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_selection"):
        card.discard_selection(data)
    game.next_player()
    game.broadcast_update()


# ------------------------------------------------------------------ #
#  Cartes interactives — Piston (poser un métier)                      #
# ------------------------------------------------------------------ #

@socketio.on("confirm_piston_job")
def on_confirm_piston(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "piston_job_selection":
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
    game.broadcast_update(f"{player.name} utilise le Piston !")


@socketio.on("discard_piston_job")
def on_discard_piston(data: dict):
    """Annulation : la carte Piston reste en main, tour inchangé."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "piston_job_selection":
        return
    if interaction["player_id"] != player.id:
        return

    # Remettre la carte Piston en main (elle avait été déplacée dans played)
    piston_card = game.find_card_by_id(interaction["card_id"])
    if piston_card:
        player.remove_card_from_played(piston_card)
        player.hand.append(piston_card)

    game.pending_interaction = None
    # Pas de next_player() : le joueur peut encore jouer/défausser
    game.broadcast_update()


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
    game.next_player()
    game.broadcast_update(f"{player.name} a un Coup de Foudre !")


@socketio.on("discard_coup_de_foudre")
def on_discard_coup_de_foudre(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_selection"):
        card.discard_selection(data)
    game.next_player()
    game.broadcast_update()


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
    game.next_player()
    game.broadcast_update(f"{player.name} fait un Troc !")


@socketio.on("discard_troc")
def on_discard_troc(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_player_selection"):
        card.discard_player_selection(data)
    game.next_player()
    game.broadcast_update()


@socketio.on("confirm_redistribution")
def on_confirm_redistribution(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)
    game.next_player()
    game.broadcast_update(f"{player.name} redistribue des cartes.")


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

@socketio.on("confirm_vengeance_hardship")
def on_confirm_vengeance_hardship(data: dict):
    """Étape 1 : le joueur a choisi quel coup dur rejouer."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "vengeance_hardship_selection":
        return
    if interaction["player_id"] != player.id:
        _emit_error(request.sid, "Ce n'est pas votre interaction")
        return

    card = game.find_card_by_id(interaction["card_id"])
    if card is None:
        return

    game.pending_interaction = None
    card.resolve_hardship(game, player, data)
    # resolve_hardship pose un nouveau pending_interaction (vengeance_target_selection)
    # OU appelle next_player()+broadcast si cible unique → on ne broadcast pas ici


@socketio.on("confirm_vengeance_target")
def on_confirm_vengeance_target(data: dict):
    """Étape 2 : le joueur a choisi la cible du coup dur."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "vengeance_target_selection":
        return
    if interaction["player_id"] != player.id:
        _emit_error(request.sid, "Ce n'est pas votre interaction")
        return

    card = game.find_card_by_id(interaction["card_id"])
    if card is None:
        return

    # Injecter hardship_id depuis l'interaction si pas dans data
    data.setdefault("hardship_id", interaction.get("hardship_id"))
    game.pending_interaction = None
    card.resolve_target(game, player, data)
    game.next_player()
    game.broadcast_update(f"{player.name} se venge !")


@socketio.on("discard_vengeance")
def on_discard_vengeance(data: dict):
    """Annulation à n'importe quelle étape : la carte Vengeance reste en main."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] not in (
        "vengeance_hardship_selection", "vengeance_target_selection"
    ):
        return
    if interaction["player_id"] != player.id:
        return

    # Remettre la carte Vengeance en main
    vengeance_card = game.find_card_by_id(interaction["card_id"])
    if vengeance_card:
        player.remove_card_from_played(vengeance_card)
        player.hand.append(vengeance_card)

    game.pending_interaction = None
    game.broadcast_update()


# ------------------------------------------------------------------ #
#  Cartes interactives — Licenciement (sélection métier)               #
# ------------------------------------------------------------------ #

@socketio.on("confirm_licenciement_job")
def on_confirm_licenciement(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "licenciement_job_selection":
        return
    # C'est le joueur actif (celui qui a joué le coup dur) qui répond
    if interaction["player_id"] != player.id:
        _emit_error(request.sid, "Ce n'est pas votre interaction")
        return

    card = game.find_card_by_id(interaction["card_id"])
    if card is None:
        return

    game.pending_interaction = None
    card.resolve(game, player, data)
    game.next_player()
    game.broadcast_update(f"{player.name} licencie un métier !")


@socketio.on("discard_licenciement_job")
def on_discard_licenciement(data: dict):
    """Annulation : on passe quand même le tour (le coup dur était déjà déclenché)."""
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return

    interaction = game.pending_interaction
    if not interaction or interaction["type"] != "licenciement_job_selection":
        return
    if interaction["player_id"] != player.id:
        return

    # Choisir un métier au hasard plutôt que d'annuler (la carte est déjà jouée)
    import random
    target_player = game.players[interaction["target_player_id"]]
    target_jobs = target_player.get_job()
    if target_jobs:
        random.choice(target_jobs).discard_play_card(game, target_player)

    game.pending_interaction = None
    game.next_player()
    game.broadcast_update()


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
    game.next_player()
    game.broadcast_update(f"{player.name} décolle en mission !")


@socketio.on("discard_astronaute")
def on_discard_astronaute(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_selection"):
        card.discard_selection(data)
    game.next_player()
    game.broadcast_update()


@socketio.on("confirm_chef_achats")
def on_confirm_chef_achats(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "confirm_selection"):
        card.confirm_selection(data)
    game.next_player()
    game.broadcast_update(f"{player.name} utilise le Chef des Achats !")


@socketio.on("discard_chef_achats")
def on_discard_chef_achats(data: dict):
    from flask import request
    game, player = _get_game_and_player(data.get("room_id", ""), request.sid)
    if game is None or player is None:
        return
    card = game.find_card_by_id(data.get("card_id", ""))
    if card and hasattr(card, "discard_selection"):
        card.discard_selection(data)
    game.next_player()
    game.broadcast_update()


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