"""
app/session/room.py — Salle de jeu (lobby + partie).
"""
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.game import Game
    from app.core.player import Player


class Room:
    """Représente une salle : lobby puis partie active."""

    def __init__(self, room_id: str, host_id: str, num_players: int):
        self.id: str = room_id
        self.host_id: str = host_id
        self.num_players: int = num_players
        self.players: list["Player"] = []
        self.game: "Game | None" = None
        self.status: str = "waiting"  # waiting | in_progress | finished

    def add_player(self, player: "Player") -> None:
        if len(self.players) < self.num_players:
            self.players.append(player)

    def remove_player(self, player_id: int) -> None:
        self.players = [p for p in self.players if p.id != player_id]

    def start_game(self, deck: list) -> "Game":
        from app.core.game import Game
        self.game = Game(self.id, deck, self.num_players)
        for player in self.players:
            self.game.add_player(player)
        self.status = "in_progress"
        return self.game

    def is_full(self) -> bool:
        return len(self.players) >= self.num_players

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "host_id": self.host_id,
            "num_players": self.num_players,
            "players": [p.to_dict(hide_hand=True) for p in self.players],
            "status": self.status,
        }
