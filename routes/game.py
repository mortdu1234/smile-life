"""
Blueprint Flask /game
"""
from flask import Blueprint, request, redirect, url_for, session, render_template, jsonify, abort
from backend.core.Game import Game
from backend.game import (
    start_game, get_game,
    draw_from_deck, draw_from_discard,
    place_card, discard_from_hand,
    discard_job, discard_wedding, discard_adultery,
    skip_turn, next_turn,
)
from backend.hub import set_preset
from flask_socketio import join_room

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

def _card_id_from_body() -> tuple[int | None, str | None]:
    data = request.get_json(silent=True) or {}
    raw = data.get("card_id")
    if raw is None:
        return None, "card_id manquant."
    try:
        return int(raw), None
    except (TypeError, ValueError):
        return None, "card_id invalide."

def _action_response(success: bool, reason: str, game_id: str):
    if success:
        game = get_game(game_id)
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
        if not game or pseudo not in [p.name for p in game.players]:
            return
        # Room personnelle pour recevoir sa propre main
        join_room(f"player_{pseudo}_{game_id}")
        # Room commune pour les futures features (chat, etc.)
        join_room(game_id)
        print(f"[WS] ✅ {pseudo} a rejoint les rooms de {game_id}")
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
    pseudo = _require_pseudo()
    success, reason = draw_from_deck(game_id, pseudo)
    return _action_response(success, reason, game_id)

@game_bp.route("/<game_id>/draw-discard", methods=["POST"])
def draw_discard(game_id):
    pseudo = _require_pseudo()
    success, reason = draw_from_discard(game_id, pseudo)
    return _action_response(success, reason, game_id)



# ── Pose / défausse depuis la main ─────────────────────────────────────────────

@game_bp.route("/<game_id>/place", methods=["POST"])
def place(game_id):
    pseudo = _require_pseudo()
    card_id, err = _card_id_from_body()
    if err:
        return jsonify({"ok": False, "error": err}), 400
    success, reason = place_card(game_id, pseudo, card_id)
    return _action_response(success, reason, game_id)

@game_bp.route("/<game_id>/discard", methods=["POST"])
def discard(game_id):
    pseudo = _require_pseudo()
    card_id, err = _card_id_from_body()
    if err:
        return jsonify({"ok": False, "error": err}), 400
    success, reason = discard_from_hand(game_id, pseudo, card_id)
    return _action_response(success, reason, game_id)


# ── Défausse de cartes posées ──────────────────────────────────────────────────

@game_bp.route("/<game_id>/discard-job", methods=["POST"])
def discard_job_route(game_id):
    pseudo = _require_pseudo()
    card_id, err = _card_id_from_body()
    if err:
        return jsonify({"ok": False, "error": err}), 400
    success, reason = discard_job(game_id, pseudo, card_id)
    return _action_response(success, reason, game_id)

@game_bp.route("/<game_id>/discard-wedding", methods=["POST"])
def discard_wedding_route(game_id):
    pseudo = _require_pseudo()
    card_id, err = _card_id_from_body()
    if err:
        return jsonify({"ok": False, "error": err}), 400
    success, reason = discard_wedding(game_id, pseudo, card_id)
    return _action_response(success, reason, game_id)

@game_bp.route("/<game_id>/discard-adultery", methods=["POST"])
def discard_adultery_route(game_id):
    pseudo = _require_pseudo()
    card_id, err = _card_id_from_body()
    if err:
        return jsonify({"ok": False, "error": err}), 400
    success, reason = discard_adultery(game_id, pseudo, card_id)
    return _action_response(success, reason, game_id)


# ── Tour ───────────────────────────────────────────────────────────────────────

@game_bp.route("/<game_id>/skip", methods=["POST"])
def skip(game_id):
    pseudo = _require_pseudo()
    success, reason = skip_turn(game_id, pseudo)
    return _action_response(success, reason, game_id)

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
    return jsonify({"pending": player.get_interface().pending})


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