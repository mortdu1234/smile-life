"""
app/session/room_manager.py — Singleton gérant toutes les salles actives.
"""
import uuid
from app.session.room import Room


class RoomManager:
    """Singleton : stocke et gère toutes les salles actives."""

    _instance: "RoomManager | None" = None

    def __new__(cls) -> "RoomManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._rooms: dict[str, Room] = {}
        return cls._instance

    # ------------------------------------------------------------------ #

    def create_room(self, host_id: str, num_players: int, deck_config=None) -> Room:
        room_id = str(uuid.uuid4())[:8]
        room = Room(room_id, host_id, num_players)
        room.deck_config = deck_config
        self._rooms[room_id] = room
        print(f"[RoomManager] Created room {room_id} with host {host_id} and deck_config {deck_config}")
        return room

    def get_room(self, room_id: str) -> Room | None:
        return self._rooms.get(room_id)

    def delete_room(self, room_id: str) -> None:
        self._rooms.pop(room_id, None)

    def list_rooms(self) -> list[Room]:
        return list(self._rooms.values())

    def get_room_by_player(self, player_id: int) -> Room | None:
        for room in self._rooms.values():
            if any(p.id == player_id for p in room.players):
                return room
        return None


# Instance partagée
room_manager = RoomManager()
