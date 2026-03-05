"""
CardEffect — données pures décrivant l'effet d'une carte.

Les cartes décrivent leur effet, le moteur l'applique via le registre des actions.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CardEffect:
    """
    Description pure de l'effet d'une carte.

    Attributs :
        type      : identifiant de l'action à appliquer (clé dans ACTION_REGISTRY)
        target    : "self" | "opponent" | "all" | "chosen"
        params    : paramètres supplémentaires propres à l'action
        interactive : True si l'effet nécessite une interaction WebSocket
    """
    type: str
    target: str = "self"
    params: dict[str, Any] = field(default_factory=dict)
    interactive: bool = False

    def __repr__(self) -> str:
        return f"CardEffect(type={self.type!r}, target={self.target!r}, params={self.params})"
