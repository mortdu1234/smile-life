"""
Cartes animaux.
"""
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.card import Card
from app.core.io_context import emit

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class AnimalCard(Card):
    """Carte animal de base."""

    def __init__(self, animal_name: str, smiles: int, image_path: str):
        super().__init__(image_path)
        self.animal_name: str = animal_name
        self.smiles: int = smiles

    def __str__(self) -> str:
        return f"{self.animal_name} — AnimalCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "animal", "subtype": self.animal_name})
        return base

    def get_card_rule(self) -> str:
        return f"Carte Animal ({self.animal_name}) — {self.smiles} smiles. Jouable à tout moment.\n"

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        return True, ""

    def play_card(self, game: "Game", current_player: "Player") -> None:
        super().play_card(game, current_player)


class LicorneAnimal(AnimalCard):
    """Licorne — combo licorne + arc-en-ciel + étoile filante = +3 smiles."""
    pass


class DragonAnimal(AnimalCard):
    """Dragon — si Daenerys posée, brûle une carte adverse."""

    def __init__(self, animal_name: str, smiles: int, image_path: str):
        super().__init__(animal_name, smiles, image_path)

    def apply_card_effect(self, game, current_player):
        from app.cards.concrete.personal.children import DaenerysChild
        if not any(isinstance(c, DaenerysChild) for c in current_player.get_all_played_cards()):
            return True
        opponents = [p for p in game.players if p != current_player]
        if not opponents:
            return True
        # On cible tous les adversaires en une seule interaction
        all_targets = {
            p.id: [c.to_dict() for c in p.get_all_played_cards()]
            for p in opponents
        }
        emit("select_burn_card", {
            "card_id": self.id,
            "opponents": [p.to_dict() for p in opponents],
            "targets_by_player": all_targets,
        }, room=current_player.session_id)
        game.pending_interaction = {
            "type": "burn_card_selection",
            "card_id": self.id,
            "player_id": current_player.id,
        }
        return False

    def resolve(self, game, current_player, data):
        # data = {"selections": [{"player_id": X, "card_id": Y}, ...]}
        for selection in data.get("selections", []):
            target = game.players[selection["player_id"]]
            card = target.get_played_card_by_id(selection["card_id"])
            if card:
                target.remove_card_from_played(card)
                game.discard.append(card)

class Chien(AnimalCard):
    pass

class Chat(AnimalCard):
    pass

class Crapaud(AnimalCard):
    pass

class Lapin(AnimalCard):
    pass

class Poussin(AnimalCard):
    pass
