from .interface import UserIO, IOType
from ..backend.core.Player import Player
from ..backend.core.cards.Card import Card

import queue

class WebIO(UserIO):
    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self.pending: dict | None = None

    def _ask(self, prompt: str, options: list, kind: IOType) -> Player | Card | None:
        self.pending = {
            "kind": kind,
            "prompt": prompt,
            "options": [o.to_dict() for o in options],
        }
        index = self._queue.get()  # bloque jusqu'à la réponse du frontend
        self.pending = None
        return options[index]

    def ask_player(self, prompt: str, players: list[Player], kind: IOType) -> Player | None:
        return self._ask(prompt, players, kind)

    def ask_card(self, prompt: str, cards: list[Card], kind: IOType) -> Card | None:
        return self._ask(prompt, cards, kind)

    def submit(self, index: int) -> None:
        """Appelé par la route Flask quand l'utilisateur choisit."""
        self._queue.put(index)