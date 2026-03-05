"""
Cartes de vie personnelle : flirt, mariage, adultère.
"""
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.card import Card

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


# ------------------------------------------------------------------ #
#  FlirtCard                                                           #
# ------------------------------------------------------------------ #

class FlirtCard(Card):
    """Carte flirt."""

    def __init__(self, location: str, image_path: str):
        super().__init__(image_path)
        self.location: str = location
        self.smiles: int = 1

    def __str__(self) -> str:
        return f"{self.location} — FlirtCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "flirt", "subtype": self.location})
        return base

    def get_card_rule(self) -> str:
        return (
            f"Carte Flirt ({self.location}) — {self.smiles} smile(s).\n"
            "RÈGLES\n"
            "- Jouable sauf pendant un mariage (sans adultère).\n"
            "- Max 5 flirts sans mariage.\n"
            "- Si le dernier flirt posé d'un autre joueur est au même lieu, vous le volez.\n"
            "- Permet de se marier.\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if current_player.is_married() and not current_player.has_adultery():
            return False, "Vous êtes marié(e) sans adultère"
        return True, ""

    def steal_same_card(self, game: "Game", current_player: "Player") -> None:
        """Vole le dernier flirt de même lieu d'un autre joueur."""
        from app.cards.concrete.personal.marriage import MarriageCard  # évite import circulaire
        for player in game.players:
            if player == current_player:
                continue
            played_cards = player.played["vie personnelle"]
            idx = len(played_cards) - 1
            while idx >= 0:
                card = played_cards[idx]
                if isinstance(card, MarriageCard):
                    break
                if isinstance(card, FlirtCard):
                    if card.location == self.location:
                        player.remove_card_from_played(card)
                        current_player.add_card_to_played(card)
                    break
                idx -= 1

    def play_card(self, game: "Game", current_player: "Player") -> None:
        self.steal_same_card(game, current_player)
        super().play_card(game, current_player)


class FlirtWithChildCard(FlirtCard):
    """Flirt portant un lien vers un enfant."""

    def __init__(self, location: str, image_path: str):
        super().__init__(location, image_path)
        self.child_link = None  # type: ignore[assignment]


# ------------------------------------------------------------------ #
#  MarriageCard                                                        #
# ------------------------------------------------------------------ #

class MarriageCard(Card):
    """Carte mariage."""

    def __init__(self, location: str, image_path: str):
        super().__init__(image_path)
        self.location: str = location
        self.smiles: int = 3

    def __str__(self) -> str:
        return f"{self.location} — MarriageCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "marriage", "subtype": self.location})
        return base

    def get_card_rule(self) -> str:
        return (
            f"Carte Mariage ({self.location}) — {self.smiles} smiles.\n"
            "RÈGLES\n"
            "- Nécessite au moins 1 flirt.\n"
            "- Un seul mariage à la fois.\n"
            "- Divorce possible en défaussant la carte en début de tour.\n"
            "- Permet de poser des enfants et un adultère.\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if current_player.is_married():
            return False, "Vous êtes déjà marié(e)"
        if not current_player.has_any_flirt():
            return False, "Vous devez avoir un flirt pour vous marier"
        return True, ""

    def discard_play_card(self, game: "Game", effected_player: "Player") -> None:
        effected_player.remove_card_from_played(self)
        game.discard.append(self)
        if effected_player.id == game.current_player:
            game.next_player()

    def play_card(self, game: "Game", current_player: "Player") -> None:
        super().play_card(game, current_player)


# ------------------------------------------------------------------ #
#  AdulteryCard                                                        #
# ------------------------------------------------------------------ #

class AdulteryCard(Card):
    """Carte adultère."""

    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.smiles: int = 1

    def __str__(self) -> str:
        return "adultère — AdulteryCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["type"] = "adultere"
        return base

    def get_card_rule(self) -> str:
        return (
            f"Carte Adultère — {self.smiles} smile(s).\n"
            "RÈGLES\n"
            "- Nécessite d'être marié(e).\n"
            "- Un seul adultère à la fois.\n"
            "- Permet de flirter au-delà de la limite.\n"
            "- En cas de divorce, vous perdez mariage, enfants et adultère.\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if not current_player.is_married():
            return False, "Vous devez être marié(e) pour commettre un adultère"
        if current_player.has_adultery():
            return False, "Vous avez déjà un adultère"
        return True, ""

    def discard_play_card(self, game: "Game", effected_player: "Player") -> None:
        effected_player.remove_card_from_played(self)
        game.discard.append(self)
        if effected_player.id == game.current_player:
            game.next_player()

    def play_card(self, game: "Game", current_player: "Player") -> None:
        super().play_card(game, current_player)
