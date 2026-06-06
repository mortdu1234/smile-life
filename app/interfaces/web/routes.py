"""
app/interfaces/web/routes.py — Routes HTTP (lobby, login…)
"""
import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from app.session.room_manager import room_manager

PRESETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "preset")

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
def index():
    return render_template("lobby.html", rooms=room_manager.list_rooms())


@web_bp.route("/room/create", methods=["POST"])
def create_room():
    import json
    num_players = int(request.form.get("num_players", 2))
    host_name   = request.form.get("name", "Hôte")

    # Lire la config deck envoyée par le lobby (JSON { card_id: count })
    deck_config = None
    deck_config_raw = request.form.get("deck_config", "")
    print("Raw deck_config from form:", deck_config_raw)
    if deck_config_raw:
        try:
            raw = json.loads(deck_config_raw)
            deck_config = {k: int(v) for k, v in raw.items() if int(v) > 0}
        except (ValueError, TypeError, AttributeError):
            deck_config = None  # fallback : counts par défaut du JSON

    room = room_manager.create_room(
        host_id=host_name,
        num_players=num_players,
        deck_config=deck_config,
    )
    return redirect(url_for("web.game", room_id=room.id))


@web_bp.route("/room/<room_id>")
def game(room_id: str):
    room = room_manager.get_room(room_id)
    if room is None:
        return redirect(url_for("web.index"))
    return render_template("game.html", room=room)


# ------------------------------------------------------------------ #
#  API Présets                                                         #
# ------------------------------------------------------------------ #

@web_bp.route("/api/presets")
def list_presets():
    """Retourne la liste des présets disponibles (id, label, description)."""
    presets = []
    if not os.path.isdir(PRESETS_DIR):
        return jsonify([])
    for filename in sorted(os.listdir(PRESETS_DIR)):
        if not filename.endswith(".json"):
            continue
        filepath = os.path.join(PRESETS_DIR, filename)
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            presets.append({
                "id":          data.get("id", filename[:-5]),
                "label":       data.get("label", filename[:-5]),
                "description": data.get("description", ""),
            })
        except (json.JSONDecodeError, OSError):
            continue
    return jsonify(presets)


@web_bp.route("/api/presets/<preset_id>")
def get_preset(preset_id: str):
    """Retourne le deck complet d'un préset."""
    # Sécurité : interdit les traversées de répertoire
    if "/" in preset_id or "\\" in preset_id or preset_id.startswith("."):
        abort(400)
    filepath = os.path.join(PRESETS_DIR, f"{preset_id}.json")
    if not os.path.isfile(filepath):
        abort(404)
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except (json.JSONDecodeError, OSError):
        abort(500)