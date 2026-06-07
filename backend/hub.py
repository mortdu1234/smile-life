"""
Logique métier du hub.
Gère le cycle de vie des salles d'attente (Room) :
  créer → rejoindre → quitter → démarrer → supprimer.

Aucune dépendance Flask ici.
"""
from __future__ import annotations

import random
import string

from .store import (
    room_save, room_get, room_delete, rooms_open,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _generate_code(length: int = 5) -> str:
    chars = string.ascii_uppercase + string.digits
    while True:
        code = "".join(random.choices(chars, k=length))
        if not room_get(code):
            return code


# ── API publique ───────────────────────────────────────────────────────────────

def create_room(host: str, max_players: int) -> dict:
    """
    Crée une nouvelle salle d'attente et la persiste.
    Retourne le dict room.
    """
    room = {
        "id": _generate_code(),
        "host": host,
        "players": [host],
        "max_players": max_players,
        "status": "waiting",   # waiting | playing | finished
        "preset_id": None,     # sélectionné depuis le lobby
    }
    room_save(room)
    return room


def get_room(game_id: str) -> dict | None:
    """Retourne la salle ou None."""
    return room_get(game_id)


def get_open_rooms() -> list[dict]:
    """Liste des salles où il reste de la place."""
    return rooms_open()


def join_room(game_id: str, pseudo: str) -> tuple[dict | None, str | None]:
    """
    Fait rejoindre `pseudo` à la salle `game_id`.
    Retourne (room, error). error est None en cas de succès.
    """
    room = room_get(game_id)
    if not room:
        return None, "Partie introuvable."
    if room["status"] != "waiting":
        return None, "Cette partie a déjà commencé."
    if len(room["players"]) >= room["max_players"]:
        return None, "Cette partie est complète."
    if pseudo in room["players"]:
        return None, "Ce pseudo est déjà pris dans cette partie."

    room["players"].append(pseudo)
    room_save(room)
    return room, None


def leave_room(game_id: str, pseudo: str) -> None:
    """
    Retire `pseudo` de la salle.
    Supprime la salle si elle est vide ; transfère le host sinon.
    """
    room = room_get(game_id)
    if not room:
        return

    if pseudo in room["players"]:
        room["players"].remove(pseudo)

    if not room["players"]:
        room_delete(game_id)
        return

    if room["host"] == pseudo:
        room["host"] = room["players"][0]

    room_save(room)


def set_preset(game_id: str, pseudo: str, preset_id: str) -> tuple[dict | None, str | None]:
    """
    L'hôte sélectionne un preset pour la partie.
    Retourne (room, error).
    """
    room = room_get(game_id)
    if not room:
        return None, "Partie introuvable."
    if room["host"] != pseudo:
        return None, "Seul l'hôte peut choisir le preset."
    if room["status"] != "waiting":
        return None, "La partie a déjà commencé."

    room["preset_id"] = preset_id
    room_save(room)
    return room, None


def mark_playing(game_id: str) -> None:
    """Passe la salle en statut 'playing' (appelé quand Game() est créé)."""
    room = room_get(game_id)
    if room:
        room["status"] = "playing"
        room_save(room)