"""
GameState — snapshot sérialisable de la partie.

Utilisé par interfaces/web/serializers.py pour envoyer l'état au client.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameState:
    """Représentation immuable (snapshot) de l'état du jeu à un instant T."""

    game_id: str
    players: list[dict[str, Any]]
    deck_count: int
    discard: list[dict[str, Any]]
    current_player: int
    phase: str
    num_players: int
    players_joined: int
    host_id: int
    casino: dict[str, Any]
    pending_hardship: Any
    arc_en_ciel: bool
    arc_en_ciel_card: dict[str, Any]
    last_discard: Any = None
    pending_interaction_type: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.game_id,
            "players": self.players,
            "deck_count": self.deck_count,
            "discard": self.discard,
            "current_player": self.current_player,
            "phase": self.phase,
            "num_players": self.num_players,
            "players_joined": self.players_joined,
            "host_id": self.host_id,
            "casino": self.casino,
            "pending_hardship": self.pending_hardship,
            "arc_en_ciel": self.arc_en_ciel,
            "arc_en_ciel_card": self.arc_en_ciel_card,
            "last_discard": self.last_discard,
            "pending_interaction_type": self.pending_interaction_type,
        }