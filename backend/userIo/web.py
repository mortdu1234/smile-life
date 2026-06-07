from typing import Sequence, TYPE_CHECKING

from .interface import UserIO, IOType
if TYPE_CHECKING:
    from ..core.Player import Player
    from ..core.cards.Card import Card
    from ..core.cards.acquisitions.Acquisition import Acquisition

from gevent.queue import Queue


class WebIO(UserIO):
    def __init__(self):
        self._queue: Queue = Queue()
        self.pending: dict | None = None

    def _ask(self, prompt: str, options: list, kind: IOType) -> "Player | Card | None":
        self.pending = {
            "kind": kind,
            "prompt": prompt,
            "options": [o.to_dict() for o in options],
        }
        index = self._queue.get()  # bloque la greenlet, libère les autres
        self.pending = None
        return options[index]

    def ask_player(self, prompt: str, players: list["Player"], kind: IOType) -> "Player | None":
        return self._ask(prompt, players, kind)

    def ask_card(self, prompt: str, cards: list["Card"], kind: IOType) -> "Card | None":
        return self._ask(prompt, cards, kind)

    def ask_salaries(self, acquisition: "Acquisition", salaries: Sequence["Card"], cost: int) -> list["Card"]:
        """Affiche l'overlay de sélection de salaires.
        Bloque la greenlet jusqu'à ce que le joueur valide une sélection dont la somme >= cost.
        Retourne la liste des cartes salaire sélectionnées.
        """
        print("[DEBUG] WebIO.ask_salaries() | start")
        self.pending = {
            "ui_component": "salary-selector",
            "prompt": f"Payer {acquisition.name if hasattr(acquisition, 'name') else 'acquisition'} ({cost})",
            "cost": cost,
            "cards": [s.to_dict() for s in salaries],
        }
        # Le frontend retourne une liste d'indices
        indices: list[int] = self._queue.get()
        self.pending = None
        print("[DEBUG] WebIO.ask_salaries() | end")
        return [salaries[i] for i in indices]

    def submit(self, index: int) -> None:
        """Appelé par la route Flask quand l'utilisateur choisit (choix simple)."""
        self._queue.put(index)

    def submit_indices(self, indices: list[int]) -> None:
        """Appelé par la route Flask quand l'utilisateur valide une sélection multiple."""
        self._queue.put(indices)