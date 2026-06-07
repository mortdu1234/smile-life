# backend/webSocket.py
from flask_socketio import SocketIO

_socketio: SocketIO | None = None

def init_socketio(sio: SocketIO) -> None:
    global _socketio
    _socketio = sio

def broadcast_game(game) -> None:
    if _socketio is None:
        return
    # Envoie un état personnalisé à chaque joueur avec SA propre main
    for player in game.players:
        state = game.to_dict(viewer=player.name)
        _socketio.emit('game_update', state, room=f"player_{player.name}_{game.id}")