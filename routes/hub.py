"""
Blueprint Flask /hub
Gère : index (liste des salles), création, rejoindre, lobby, preset, quitter.
Toute logique métier est déléguée à backend.hub.
"""
from flask import Blueprint, request, redirect, url_for, session, render_template, jsonify

from backend.hub import (
    create_room, get_room, get_open_rooms,
    join_room, leave_room, set_preset,
)
from backend.game import load_presets

hub_bp = Blueprint(
    "hub",
    __name__,
    template_folder="templates",
    url_prefix="/hub",
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _require_pseudo() -> tuple[str | None, str | None]:
    pseudo = request.form.get("pseudo", "").strip()
    if not pseudo:
        return None, "Veuillez entrer un pseudo."
    return pseudo, None


# ── Index ──────────────────────────────────────────────────────────────────────

@hub_bp.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        action = request.form.get("action")
        pseudo, error = _require_pseudo()

        if not error:
            if action == "create":
                max_players = int(request.form.get("max_players", 4))
                room = create_room(pseudo, max_players)
                session["pseudo"] = pseudo
                session["game_id"] = room["id"]
                return redirect(url_for("hub.lobby", game_id=room["id"]))

            elif action == "join":
                game_id = request.form.get("game_id", "").strip().upper()
                room, error = join_room(game_id, pseudo)
                if not error:
                    session["pseudo"] = pseudo
                    session["game_id"] = room["id"]
                    return redirect(url_for("hub.lobby", game_id=room["id"]))

    return render_template("index.html", games=get_open_rooms(), error=error)


# ── Lobby ──────────────────────────────────────────────────────────────────────

@hub_bp.route("/lobby/<game_id>", methods=["GET"])
def lobby(game_id):
    room = get_room(game_id)
    if not room:
        return redirect(url_for("hub.index"))

    pseudo = session.get("pseudo", "Invité")
    error = request.args.get("error")

    # Si la partie a déjà démarré (ex: rechargement de page après lancement)
    if room["status"] == "playing":
        return redirect(url_for("game.play", game_id=game_id))

    return render_template(
        "lobby.html",
        room=room,
        pseudo=pseudo,
        error=error,
        presets=load_presets(),
        is_host=(room["host"] == pseudo),
    )


# ── Statut JSON (polling des non-hôtes) ───────────────────────────────────────

@hub_bp.route("/lobby/<game_id>/status")
def room_status(game_id):
    """Retourne le statut de la room en JSON pour le polling côté client."""
    room = get_room(game_id)
    if not room:
        return jsonify({"status": "not_found"}), 404
    return jsonify({"status": room["status"]})


# ── Sélection du preset (host uniquement) ─────────────────────────────────────

@hub_bp.route("/lobby/<game_id>/preset", methods=["POST"])
def choose_preset(game_id):
    pseudo = session.get("pseudo")
    preset_id = request.form.get("preset_id", "").strip()

    _, error = set_preset(game_id, pseudo, preset_id)
    if error:
        return redirect(url_for("hub.lobby", game_id=game_id, error=error))

    return redirect(url_for("hub.lobby", game_id=game_id))


# ── Quitter la salle ───────────────────────────────────────────────────────────

@hub_bp.route("/lobby/<game_id>/leave")
def leave(game_id):
    pseudo = session.pop("pseudo", None)
    session.pop("game_id", None)
    if pseudo:
        leave_room(game_id, pseudo)
    return redirect(url_for("hub.index"))