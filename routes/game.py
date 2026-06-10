"""
Blueprint Flask /game
"""
from flask import Blueprint, request, redirect, url_for, session, render_template, jsonify, abort
from backend.core.Game import Game
from backend.game import (
    start_game, get_game
)
from backend.hub import set_preset
from flask_socketio import join_room
from backend.webSocket import broadcast_game

game_bp = Blueprint(
    "game",
    __name__,
    template_folder="templates",
    url_prefix="/game",
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _pseudo() -> str | None:
    return session.get("pseudo")

def _require_pseudo():
    pseudo = _pseudo()
    if not pseudo:
        abort(401, "Non connecté.")
    return pseudo

def _card_id_from_body() -> tuple[int | None, str]:
    """Permet de récupérer l'Id de la carte depuis le body de la requete"""
    data = request.get_json(silent=True) or {}
    raw = data.get("card_id")
    if raw is None:
        return None, "card_id manquant."
    try:
        return int(raw), ""
    except (TypeError, ValueError):
        return None, "card_id invalide."

def _action_response(success: bool, reason: str, game_id: str):
    if success:
        game = get_game(game_id)
        broadcast_game(game)
        pseudo = session.get("pseudo")
        state = game.to_dict(viewer=pseudo) if game else None
        return jsonify({"ok": True, "state": state})
    return jsonify({"ok": False, "error": reason or "Action impossible."}), 400


# ── Handlers WebSocket — enregistrés APRÈS init via register_socket_events ────

def register_socket_events(sio):
    @sio.on('connect')
    def on_connect():
        print(f"[WS] ⚡ connecté: {request.sid}")

    @sio.on('disconnect')
    def on_disconnect():
        print(f"[WS] déconnecté: {request.sid}")

    @sio.on('join')
    def on_join(data):
        game_id = data.get('game_id')
        pseudo  = data.get('pseudo')
        game = get_game(game_id)
        
        if not game:
            return
            
        # On permet de rejoindre la room du jeu même si on n'est pas sur la liste des joueurs actifs
        join_room(f"player_{pseudo}_{game_id}") # Utile pour voir la main du joueur switché
        join_room(game_id)                      # Utile pour les événements globaux
        
        print(f"[WS] 👁 {pseudo} observe la partie {game_id}")
        sio.emit('game_update', game.to_dict(viewer=pseudo), room=request.sid)

# ── Lancer la partie ───────────────────────────────────────────────────────────

@game_bp.route("/start", methods=["POST"])
def start():
    pseudo = _pseudo()
    if not pseudo:
        return redirect(url_for("hub.index"))

    game_id   = request.form.get("game_id", "").strip().upper()
    preset_id = request.form.get("preset_id", "").strip()

    if not game_id:
        abort(400, "game_id est requis.")

    if preset_id:
        _, error = set_preset(game_id, pseudo, preset_id)
        if error:
            return redirect(url_for("hub.lobby", game_id=game_id, error=error))

    game, error = start_game(game_id, pseudo)
    if error:
        return redirect(url_for("hub.lobby", game_id=game_id, error=error))

    return redirect(url_for("game.play", game_id=game_id))


# ── Vue principale ─────────────────────────────────────────────────────────────

@game_bp.route("/<game_id>")
def play(game_id):
    game = get_game(game_id)
    if not game:
        return redirect(url_for("hub.index"))

    pseudo = session.get("pseudo", "Invité")
    player_names = [p.name for p in game.players]
    if pseudo not in player_names:
        return redirect(url_for("hub.index"))

    current_player = game.get_current_player()
    my_player = next(p for p in game.players if p.name == pseudo)

    return render_template(
        "board.html",
        game=game,
        pseudo=pseudo,
        my_player=my_player,
        current_player=current_player,
        is_my_turn=(current_player.name == pseudo),
        deck_size=len(game.deck),
        discard_top=game.get_last_discard(),
    )

# ── OBSERVATEUR ───────────────────────────────────────────────────────────────────────


@game_bp.route("/<game_id>/observe/<player_name>")
def board_as(game_id, player_name):
    game = get_game(game_id)
    if not game:
        return redirect(url_for("hub.index"))

    player_names = [p.name for p in game.players]
    if player_name not in player_names:
        abort(404, "Joueur introuvable.")

    current_player = game.get_current_player()
    my_player = next(p for p in game.players if p.name == player_name)

    return render_template(
        "board-observer.html",
        game=game,
        pseudo=player_name,
        my_player=my_player,
        current_player=current_player,
        is_my_turn=(current_player.name == player_name),
        deck_size=len(game.deck),
        last_discard=game.get_last_discard(),
    )
# ── État JSON ──────────────────────────────────────────────────────────────────

@game_bp.route("/<game_id>/state")
def state(game_id):
    game = get_game(game_id)
    if not game:
        return jsonify({"error": "Partie introuvable."}), 404
    pseudo = session.get("pseudo")
    return jsonify(game.to_dict(viewer=pseudo))

# ── Pioche ─────────────────────────────────────────────────────────────────────

@game_bp.route("/<game_id>/draw", methods=["POST"])
def draw(game_id):
    game = get_game(game_id)
    if game:
        player_id = game.get_current_player().get_id()
        success, reason = game.draw_card_from_deck(player_id)
        return _action_response(success, reason, game_id)
    return _action_response(False, "[ERROR] Game non trouvée", game_id)

@game_bp.route("/<game_id>/draw-discard", methods=["POST"])
def draw_discard(game_id):
    game = get_game(game_id)
    if game:
        player_id = game.get_current_player().get_id()
        success, reason = game.draw_card_from_discard(player_id)
        return _action_response(success, reason, game_id)
    return _action_response(False, "[ERROR] Game non trouvée", game_id)




# ── Pose / défausse depuis la main ─────────────────────────────────────────────

@game_bp.route("/<game_id>/place", methods=["POST"])
def place(game_id):
    game = get_game(game_id)
    if game:
        player_id = game.get_current_player().get_id()
        card_id, reason = _card_id_from_body()
        if not card_id:
            return _action_response(False, reason, game_id)
        success, reason = game.place_card(player_id, card_id)
        return _action_response(success, reason, game_id)
    return _action_response(False, "[ERROR] Game non trouvée", game_id)


@game_bp.route("/<game_id>/discard", methods=["POST"])
def discard(game_id):
    """discard une carte depuis la main"""
    game = get_game(game_id)
    if game:
        player_id = game.get_current_player().get_id()
        card_id, reason = _card_id_from_body()
        if not card_id:
            return _action_response(False, reason, game_id)
        success, reason = game.discard_card_from_hand(player_id, card_id)
        return _action_response(success, reason, game_id)
    return _action_response(False, "[ERROR] Game non trouvée", game_id)



# ── Défausse de cartes posées ──────────────────────────────────────────────────

@game_bp.route("/<game_id>/discard-job", methods=["POST"])
def discard_job_route(game_id):
    """Permet d'effectuer une démission comme action"""
    game = get_game(game_id)
    if not game:
        print("[ERROR] Game non trouvée")
        return _action_response(False, "[ERROR] Game non trouvée", game_id)    
    player_id = game.get_current_player().get_id()
    card_id, reason = _card_id_from_body()
    if not card_id:
        print(reason)
        return _action_response(False, reason, game_id)
    success, reason = game.discard_job_card(player_id, card_id)
    return _action_response(success, reason, game_id)

@game_bp.route("/<game_id>/discard-wedding", methods=["POST"])
def discard_wedding_route(game_id):
    """Permet de divorcer volontairement"""
    game = get_game(game_id)
    if not game:
        print("[ERROR] Game non trouvée")
        return _action_response(False, "[ERROR] Game non trouvée", game_id)    
    player_id = game.get_current_player().get_id()
    card_id, reason = _card_id_from_body()
    if not card_id:
        print(reason)
        return _action_response(False, reason, game_id)
    success, reason = game.discard_wedding_card(player_id, card_id)
    return _action_response(success, reason, game_id)

@game_bp.route("/<game_id>/discard-adultery", methods=["POST"])
def discard_adultery_route(game_id):
    """Permet de supprimer volontairement son adultaire"""
    game = get_game(game_id)
    if not game:
        print("[ERROR] Game non trouvée")
        return _action_response(False, "[ERROR] Game non trouvée", game_id)    
    player_id = game.get_current_player().get_id()
    card_id, reason = _card_id_from_body()
    if not card_id:
        print(reason)
        return _action_response(False, reason, game_id)
    success, reason = game.discard_adultery_card(player_id, card_id)
    return _action_response(success, reason, game_id)


# ── Tour ───────────────────────────────────────────────────────────────────────

@game_bp.route("/<game_id>/skip", methods=["POST"])
def skip(game_id):
    game = get_game(game_id)
    if game:
        player_id = game.get_current_player().get_id()
        success, reason = game.skip_turn(player_id)
        return _action_response(success, reason, game_id)
    return _action_response(False, "[ERROR] Game non trouvée", game_id)




# ── UserIO ───────────────────────────────────────────────────────────────────────

@game_bp.route("/<game_id>/pending")
def pending(game_id):
    game = get_game(game_id)
    if not game:
        return jsonify({"pending": None})
    pseudo = session.get("pseudo")
    player = next((p for p in game.players if p.name == pseudo), None)
    if not player:
        return jsonify({"pending": None})
    return jsonify({"pending": player.get_interface().pending}) # type: ignore


@game_bp.route("/<game_id>/submit-indices", methods=["POST"])
def submit_indices(game_id):
    game = get_game(game_id)
    if not game:
        return jsonify({"ok": False, "error": "Partie introuvable."}), 404
    pseudo = session.get("pseudo")
    player = next((p for p in game.players if p.name == pseudo), None)
    if not player:
        return jsonify({"ok": False, "error": "Joueur introuvable."}), 404
    indices = (request.get_json() or {}).get("indices")
    if not isinstance(indices, list):
        return jsonify({"ok": False, "error": "indices manquants."}), 400
    player.get_interface().submit_indices(indices)
    return jsonify({"ok": True})

@game_bp.route("/<game_id>/dismiss", methods=["POST"])
def dismiss(game_id):
    game = get_game(game_id)
    if not game:
        return jsonify({"ok": False, "error": "Partie introuvable."}), 404
    pseudo = session.get("pseudo")
    player = next((p for p in game.players if p.name == pseudo), None)
    if not player:
        return jsonify({"ok": False, "error": "Joueur introuvable."}), 404
    player.get_interface().submit_dismiss()
    return jsonify({"ok": True})

@game_bp.route("/<game_id>/submit", methods=["POST"])
def submit(game_id):
    game = get_game(game_id)
    if not game:
        return jsonify({"ok": False, "error": "Partie introuvable."}), 404
    pseudo = session.get("pseudo")
    player = next((p for p in game.players if p.name == pseudo), None)
    if not player:
        return jsonify({"ok": False, "error": "Joueur introuvable."}), 404
    index = (request.get_json() or {}).get("index")
    if index is None:
        return jsonify({"ok": False, "error": "index manquant."}), 400
    player.get_interface().submit(index)
    return jsonify({"ok": True})


# ── CARTES SPECIALES ───────────────────────────────────────────────────────────────────────


@game_bp.route("/<game_id>/stop-arc-en-ciel", methods=["POST"])
def stop_arc_en_ciel(game_id):
    game = get_game(game_id)
    if game:
        player_id = game.get_current_player().get_id()
        success, reason = game.stop_arc_en_ciel(player_id)
        return _action_response(success, reason, game_id)
    return _action_response(False, "[ERROR] Game non trouvée", game_id)


@game_bp.route("/<game_id>/bet-on-casino", methods=["POST"])
def bet_on_casino(game_id):
    """Permet d'effectuer une mise au casino"""
    game = get_game(game_id)
    if not game:
        print("[ERROR] Game non trouvée")
        return _action_response(False, "[ERROR] Game non trouvée", game_id)    
    player_id = game.get_current_player().get_id()
    card_id, reason = _card_id_from_body()
    if not card_id:
        print(reason)
        return _action_response(False, reason, game_id)
    success, reason = game.bet_on_casino(player_id, card_id)
    return _action_response(success, reason, game_id)