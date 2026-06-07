"""
Couche de stockage in-memory.
Interface propre pour migrer vers PostgreSQL : remplacer les fonctions
get/set/delete par des requêtes SQLAlchemy sans toucher au reste du code.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core.Game import Game

# ── Stockages in-memory ────────────────────────────────────────────────────────

# Salles d'attente  { game_id: dict }
_rooms: dict[str, dict] = {}

# Parties en cours  { game_id: Game }
_games: dict[str, "Game"] = {}


# ── Rooms (salles d'attente) ───────────────────────────────────────────────────

def room_save(room: dict) -> None:
    _rooms[room["id"]] = room


def room_get(game_id: str) -> dict | None:
    return _rooms.get(game_id.upper())


def room_delete(game_id: str) -> None:
    _rooms.pop(game_id.upper(), None)


def rooms_open() -> list[dict]:
    """Retourne les salles en attente avec de la place."""
    return [
        r for r in _rooms.values()
        if r["status"] == "waiting" and len(r["players"]) < r["max_players"]
    ]


# ── Games (parties en cours) ───────────────────────────────────────────────────

def game_save(game: "Game") -> None:
    _games[game.id] = game


def game_get(game_id: str) -> "Game | None":
    return _games.get(game_id.upper())


def game_delete(game_id: str) -> None:
    _games.pop(game_id.upper(), None)