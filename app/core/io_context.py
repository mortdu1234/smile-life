"""
Contexte d'I/O injectable — découple la logique de jeu de Flask/SocketIO.

Utilisation dans les cartes :
    from app.core.io_context import emit

Configuration (dans app/__init__.py) :
    from app.core import io_context
    from flask_socketio import emit as socketio_emit
    io_context.set_emit(socketio_emit)
"""
from typing import Callable, Optional

_emit_fn: Optional[Callable] = None


def set_emit(fn: Callable) -> None:
    """Injecte la fonction emit de SocketIO."""
    global _emit_fn
    _emit_fn = fn


def emit(event: str, data: dict = None, room: str = None) -> None:
    """Émet un événement WebSocket si un emit a été injecté."""
    if _emit_fn is not None:
        kwargs = {}
        if room is not None:
            kwargs["room"] = room
        _emit_fn(event, data or {}, **kwargs)
    else:
        print(f"[io_context] emit non configuré — événement ignoré : {event}")
