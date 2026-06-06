"""
Cartes de vie professionnelle : études et salaires.
"""
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.card import Card

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class StudyCard(Card):
    """Carte étude — accorde des niveaux d'étude."""

    def __init__(self, study_type: str, levels: int, image_path: str):
        super().__init__(image_path)
        self.study_type: str = study_type
        self.levels: int = levels
        self.smiles: int = 1

    def __str__(self) -> str:
        return f"{self.study_type} — StudyCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "study", "subtype": self.study_type, "levels": self.levels})
        return base

    def get_card_rule(self) -> str:
        return (
            f"Carte Étude ({self.study_type}) — {self.smiles} smile(s), {self.levels} niveau(x).\n"
            "RÈGLES\n"
            "- Jouable uniquement sans métier (sauf pouvoir extra_study).\n"
            "- Permet d'accéder à de meilleurs métiers.\n"
            "- Max 6 cartes études au total (sauf cas spécial).\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if current_player.has_job() and "extra_study" not in current_player.get_power():
            return False, "Vous ne pouvez plus faire d'études après avoir trouvé un métier"
        return True, ""

    def play_card(self, game: "Game", current_player: "Player") -> None:
        super().play_card(game, current_player)


class SalaryCard(Card):
    """Carte salaire — représente un revenu."""

    def __init__(self, level: int, image_path: str):
        super().__init__(image_path)
        self.level: int = level
        self.smiles: int = 1

    def __str__(self) -> str:
        return f"Salaire {self.level} — SalaryCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "salary", "subtype": self.level})
        return base

    def get_card_rule(self) -> str:
        return (
            f"Carte Salaire (niveau {self.level}) — {self.smiles} smile(s).\n"
            "RÈGLES\n"
            "- Nécessite d'avoir un métier.\n"
            "- Peut être jouée au casino si ouvert.\n"
            "- Permet d'acheter des acquisitions.\n"
        )
    def can_bet_card(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if game.casino_card and game.casino_card.first_player_id != current_player.id:
            return True, ""
        return False, "Vous etes l'ouvreur du casino ou le casino n'est pas ouvert"
    
    def can_place_card(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        jobs = current_player.get_job()
        if not jobs:
            return False, "Vous devez avoir un métier pour recevoir un salaire"
        max_salary = max(job.get_salary() for job in jobs)

        if "egalite_salaire" in current_player.get_power():
            for player in game.players:
                if player.has_job():
                    for job in player.get_job():
                        max_salary = max(max_salary, job.get_salary())

        if self.level > max_salary:
            return False, f"Votre salaire maximum est de {max_salary}"

        return True, ""
        
    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        can_place, reason = self.can_place_card(current_player, game)
        can_bet, bet_reason = self.can_bet_card(current_player, game)
        if can_place or can_bet:
            return True, ""
        return False, reason+" et "+bet_reason
    
    def play_card(self, game: "Game", current_player: "Player") -> None:
        can_place, _ = self.can_place_card(current_player, game)
        can_bet, _   = self.can_bet_card(current_player, game)

        if can_place and can_bet:
            # Les deux options → afficher le choix au joueur
            from app.core.io_context import emit
            emit("select_salary_placement", {
                "card_id": self.id,
                "casino_card_id": game.casino_card.id,
                "first_bet": game.casino_card.first_bet.to_dict() if game.casino_card.first_bet else None,
            }, room=current_player.session_id)
            game.pending_interaction = {
                "type": "salary_placement",
                "card_id": self.id,
                "player_id": current_player.id,
            }
            return

        if can_bet and not can_place:
            # Seulement casino
            game.casino_card.resolve_second(game, current_player, {"bet_card_id": self.id})
            return

        if can_place and not can_bet:
            # Seulement poser normalement
            super().play_card(game, current_player)
            return

        # Rien de possible
        from app.core.io_context import emit
        emit("error", {"message": "Vous ne pouvez pas jouer cette carte"}, room=current_player.session_id)

    def resolve_placement(self, game: "Game", player: "Player", choice: str) -> None:
        """Appelé depuis events.py après le choix du joueur."""
        if choice == "casino":
            game.casino_card.resolve_second(game, player, {"bet_card_id": self.id})
        elif choice == "normal":
            super().play_card(game, player)
            game.next_player()
            game.broadcast_update(f"{player.name} pose un salaire.")