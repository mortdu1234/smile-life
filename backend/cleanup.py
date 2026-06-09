"""
Nettoyage automatique des salles et parties inactives.

Deux timeouts configurables (en secondes) :
  - ROOM_TTL  : salle d'attente sans activité  → défaut 10 min
  - GAME_TTL  : partie en cours sans activité  → défaut 60 min

Lancement :  start_cleanup_worker()  (appelé une fois au démarrage de l'app).
Arrêt propre à la fermeture de l'interpréteur (thread daemon).
"""
from __future__ import annotations

import threading
import time
from datetime import datetime, timezone

from .store import (
    _rooms, _games,          # accès direct aux dicts internes
    room_delete, game_delete,
)

# ── Timeouts (secondes) ────────────────────────────────────────────────────────

ROOM_TTL: int = 10*60   # 10 minutes
GAME_TTL: int = 60*60   # 60 minutes
CHECK_INTERVAL: int = 60  # vérification toutes les 60 s

# ── Worker ─────────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _cleanup_once() -> None:
    """Supprime les salles et parties dont l'activité est expirée."""
    now = _now()

    # — Salles d'attente —
    stale_rooms = [
        room_id
        for room_id, room in list(_rooms.items())
        if (now - room["updated_at"]).total_seconds() > ROOM_TTL
    ]
    for room_id in stale_rooms:
        print(f"[cleanup] Salle expirée supprimée : {room_id}")
        room_delete(room_id)

    # — Parties en cours —
    stale_games = [
        game_id
        for game_id, game in list(_games.items())
        if (now - game.updated_at).total_seconds() > GAME_TTL
    ]
    for game_id in stale_games:
        print(f"[cleanup] Partie expirée supprimée : {game_id}")
        game_delete(game_id)


def _worker() -> None:
    while True:
        time.sleep(CHECK_INTERVAL)
        print("[CLEANER - INFO] check all session for a clean")
        try:
            _cleanup_once()
        except Exception as exc:          # ne jamais crasher le thread
            print(f"[cleanup] Erreur inattendue : {exc}")


_started = False
_lock = threading.Lock()


def start_cleanup_worker() -> None:
    """
    Lance le thread de nettoyage (idempotent : un seul thread même si
    appelé plusieurs fois, ex. rechargement de module en dev).
    """
    global _started
    with _lock:
        if _started:
            return
        t = threading.Thread(target=_worker, name="cleanup-worker", daemon=True)
        t.start()
        _started = True
        print(f"[cleanup] Worker démarré (room TTL={ROOM_TTL}s, game TTL={GAME_TTL}s)")