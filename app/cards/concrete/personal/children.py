"""
Cartes enfants.
"""
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.card import Card
from app.core.io_context import emit

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


# ------------------------------------------------------------------ #
#  Marqueurs de genre                                                  #
# ------------------------------------------------------------------ #

class FemaleChild(Card):
    """Mixin — enfant féminin."""

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.special.cards import GirlPowerCard
        for card in current_player.get_played_effet_permanent():
            if isinstance(card, GirlPowerCard):
                current_player.remove_card_from_played(card)
                current_player.add_card_to_hand(card)
                card.effect(game, current_player)
        return True


class MaleChild(Card):
    """Mixin — enfant masculin."""


class GirlPowerChild(Card):
    """Mixin — enfant girl-power."""


# ------------------------------------------------------------------ #
#  ChildCard                                                           #
# ------------------------------------------------------------------ #

class ChildCard(Card):
    """Carte enfant de base."""

    def __init__(self, name: str, image_path: str):
        super().__init__(image_path)
        self.name: str = name
        self.smiles: int = 2

    def __str__(self) -> str:
        return f"{self.name} — ChildCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "child", "subtype": self.name})
        return base

    def get_card_rule(self) -> str:
        return (
            f"Carte Enfant ({self.name}) — {self.smiles} smiles.\n"
            "RÈGLES\n"
            "- Nécessite d'être marié(e).\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        from app.cards.concrete.personal.flirt import FlirtWithChildCard
        last_flirt = current_player.get_last_flirt()
        if isinstance(last_flirt, FlirtWithChildCard) and last_flirt.child_link is None:
            return True, ""
        if not current_player.is_married():
            return False, "Vous devez être marié(e) pour avoir un enfant"
        return True, ""

    def play_card(self, game: "Game", current_player: "Player") -> None:
        from app.cards.concrete.personal.flirt import FlirtWithChildCard
        last_flirt = current_player.get_last_flirt()
        if isinstance(last_flirt, FlirtWithChildCard) and last_flirt.child_link is None:
            last_flirt.child_link = self
        super().play_card(game, current_player)


# ------------------------------------------------------------------ #
#  Enfants concrets                                                    #
# ------------------------------------------------------------------ #

class AngelaChild(ChildCard, GirlPowerChild):
    pass


class BeatrixChild(ChildCard, FemaleChild):
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.acquisitions.cards import SabreCard
        for card in current_player.get_played_acquisitions():
            if isinstance(card, SabreCard):
                card.apply_card_effect(game, current_player)
        return True


class DaenerysChild(ChildCard, FemaleChild):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

    def apply_card_effect(self, game, current_player):
        from app.cards.concrete.animals.cards import DragonAnimal
        if not any(isinstance(c, DragonAnimal) for c in current_player.get_all_played_cards()):
            return True
        opponents = [p for p in game.players if p != current_player]
        if not opponents:
            return True
        emit("select_burn_card", {
            "card_id": self.id,
            "opponents": [p.to_dict() for p in opponents],
            "targets_by_player": {
                p.id: [c.to_dict() for c in p.get_all_played_cards()]
                for p in opponents
            },
        }, room=current_player.session_id)
        game.pending_interaction = {
            "type": "burn_card_selection",
            "card_id": self.id,
            "player_id": current_player.id,
        }
        return False

    def resolve(self, game, current_player, data):
        for selection in data.get("selections", []):
            target = game.players[selection["player_id"]]
            card = target.get_played_card_by_id(selection["card_id"])
            if card:
                target.remove_card_from_played(card)
                game.discard.append(card)


class DianaChild(ChildCard, FemaleChild):
    pass


class HarryChild(ChildCard, MaleChild):
    pass


class HermioneChild(ChildCard, FemaleChild):
    pass


class LaraChild(ChildCard, FemaleChild):
    pass


class LeiaChild(ChildCard, FemaleChild):
    pass


class LouiseChild(ChildCard, GirlPowerChild):
    pass


class LuigiChild(ChildCard, MaleChild):
    pass


class MarioChild(ChildCard, MaleChild):
    pass


class LukeChild(ChildCard, MaleChild):
    pass


class OlympeChild(ChildCard, GirlPowerChild):
    pass


class RockyChild(ChildCard, MaleChild):
    pass


class SimoneChild(ChildCard, GirlPowerChild):
    pass


class ZeldaChild(ChildCard, FemaleChild):
    pass
