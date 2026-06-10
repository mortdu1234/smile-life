"""
Blueprint Flask /hub
Gère : index (liste des salles), création, rejoindre, lobby, preset,
       deck personnalisé, quitter.
Toute logique métier est déléguée à backend.hub.
"""
from flask import Blueprint, request, redirect, url_for, session, render_template, jsonify

from backend.hub import (
    create_room, get_room, get_open_rooms,
    join_room, leave_room, set_preset, set_custom_deck,
)
from backend.game import load_presets
from backend.core.cards.cardCatalog import get_catalog_nested, get_catalog_by_category, TYPE1_ORDER

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

    return render_template(url_for("index.html", games=get_open_rooms(), error=error))


# ── Lobby ──────────────────────────────────────────────────────────────────────

@hub_bp.route("/lobby/<game_id>", methods=["GET"])
def lobby(game_id):
    room = get_room(game_id)
    if not room:
        return redirect(url_for("hub.index"))

    pseudo = session.get("pseudo", "Invité")
    error = request.args.get("error")
    is_host = (room["host"] == pseudo)

    # Si la partie a déjà démarré (ex: rechargement de page après lancement)
    if room["status"] == "playing":
        return redirect(url_for("game.play", game_id=game_id))

    # Calcul du total de cartes dans le deck perso (pour l'affichage)
    custom_deck = room.get("custom_deck") or {}
    custom_deck_total = sum(custom_deck.values()) if custom_deck else 0

    return render_template(
        url_for("lobby.html",
        room=room,
        pseudo=pseudo,
        error=error,
        presets=load_presets(),
        is_host=is_host,
        catalog_nested=get_catalog_nested() if is_host else {},
        type1_tabs=TYPE1_ORDER,          # ← importer aussi depuis cardCatalog
        custom_deck_total=custom_deck_total,
        ))


# ── Statut JSON (polling des non-hôtes) ───────────────────────────────────────

@hub_bp.route("/lobby/<game_id>/status")
def room_status(game_id):
    room = get_room(game_id)
    if not room:
        return jsonify({"status": "not_found"}), 404
    return jsonify({
        "status": room["status"],
        "players": room["players"],
        "max_players": room["max_players"],
        "host": room["host"],
    })


# ── Sélection du preset (host uniquement) ─────────────────────────────────────

@hub_bp.route("/lobby/<game_id>/preset", methods=["POST"])
def choose_preset(game_id):
    pseudo = session.get("pseudo")
    preset_id = request.form.get("preset_id", "").strip()

    _, error = set_preset(game_id, pseudo, preset_id)
    if error:
        return redirect(url_for("hub.lobby", game_id=game_id, error=error))

    return redirect(url_for("hub.lobby", game_id=game_id))


# ── Deck personnalisé (host uniquement) ───────────────────────────────────────

@hub_bp.route("/lobby/<game_id>/custom-deck", methods=["POST"])
def custom_deck(game_id):
    """
    Reçoit un JSON { "deck": { card_id: count, ... } }
    et le stocke dans la room.
    """
    pseudo = session.get("pseudo")
    data = request.get_json(silent=True)

    if not data or "deck" not in data:
        return jsonify({"error": "Payload invalide."}), 400

    _, error = set_custom_deck(game_id, pseudo, data["deck"])
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"ok": True})


# ── Quitter la salle ───────────────────────────────────────────────────────────

@hub_bp.route("/lobby/<game_id>/leave")
def leave(game_id):
    pseudo = session.pop("pseudo", None)
    session.pop("game_id", None)
    if pseudo:
        leave_room(game_id, pseudo)
    return redirect(url_for("hub.index"))