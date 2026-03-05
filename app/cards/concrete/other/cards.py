"""
Autres cartes : Légion d'Honneur, Prix d'Excellence.
"""
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.card import Card

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class OtherCard(Card):
    def __init__(self, card_type: str, smiles: int, image_path: str):
        super().__init__(image_path)
        self.card_type: str = card_type
        self.smiles: int = smiles

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "other", "subtype": self.card_type})
        return base

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        return True, ""

    def play_card(self, game: "Game", current_player: "Player") -> None:
        super().play_card(game, current_player)

    def get_card_rule(self) -> str:
        return f"Carte {self.card_type} — {self.smiles} smiles."


class LegionCard(OtherCard):
    def __init__(self, smiles: int, image_path: str):
        super().__init__("legion", smiles, image_path)

    def get_card_rule(self) -> str:
        return (
            f"Légion d'Honneur — {self.smiles} smiles.\n"
            "- Jouable uniquement si le joueur n'a jamais été bandit.\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if current_player.has_been_bandit:
            return False, "Vous avez été bandit dans la partie"
        return True, ""


class PriceCard(OtherCard):
    def __init__(self, smiles: int, image_path: str):
        super().__init__("prix", smiles, image_path)
        self.job_link: str | None = None

    def get_card_rule(self) -> str:
        return (
            f"Grand Prix d'Excellence — {self.smiles} smiles.\n"
            "- Certains métiers seulement.\n"
            "- Permet des salaires de 1 à 4.\n"
            "- Le bonus smile reste même si le métier lié est perdu.\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if "prix_possible" not in current_player.get_power():
            return False, "Votre métier ne permet pas de recevoir un prix"
        for job in current_player.get_job():
            if "prix_possible" in job.get_power():
                self.job_link = job.id
                job.is_link = True
        return True, ""
