"""
Cartes acquisitions — achetables avec des salaires.
"""
from typing import TYPE_CHECKING, Dict, Any, List

from app.cards.base.card import Card
from app.core.io_context import emit

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game
    from app.cards.concrete.professional.study_salary import SalaryCard


class AquisitionCard(Card):
    """Carte acquisition de base — nécessite un paiement en salaires."""

    def __init__(self, cost: int, smiles: int, image_path: str):
        super().__init__(image_path)
        self.cost: int = cost
        self._original_cost = cost
        self.smiles: int = smiles

    def __str__(self) -> str:
        return f"Acquisition (coût {self.cost}) — {self.smiles} smiles"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "aquisition", "cost": self.cost})
        return base

    def get_card_rule(self) -> str:
        return f"Carte Acquisition — {self.smiles} smiles, coût : {self.cost} liasses.\n"

    def _effective_cost(self, current_player: "Player") -> int:
        """Coût réel après réductions éventuelles (surcharge dans les sous-classes)."""
        return self.cost

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        required = self._effective_cost(current_player)
        total_power = current_player.get_available_salary_sum() + current_player.heritage
        if total_power < required:
            return False, f"Il vous faut {required} liasses (vous avez {total_power})"
        return True, ""

    def _get_available_salaries(self, current_player: "Player") -> list:
        """Retourne les SalaryCard posées du joueur (non encore dépensées)."""
        from app.cards.concrete.professional.study_salary import SalaryCard as SC
        return [
            c for c in current_player.played["vie professionnelle"]
            if isinstance(c, SC)
        ]

    def play_card(self, game: "Game", current_player: "Player") -> None:
        """Ouvre l'overlay de sélection des salaires, ne pose pas encore la carte."""
        effective = self._effective_cost(current_player)
        available_salaries = self._get_available_salaries(current_player)

        emit("select_salaries_for_acquisition", {
            "card":               self.to_dict(),
            "required_cost":      effective,
            "available_salaries": [s.to_dict() for s in available_salaries],
            "heritage_available": current_player.heritage,
        }, room=current_player.session_id)

        game.pending_interaction = {
            "type":      "salary_selection",
            "card_id":   self.id,
            "player_id": current_player.id,
        }
        # La carte reste en main jusqu'à resolve()

    def resolve(self, game: "Game", current_player: "Player", data: dict) -> None:
        """
        Appelé par events.py après confirm_salary_selection.
        Déplace les salaires sélectionnés vers 'salaire dépensé', pose la carte.
        """
        from app.cards.concrete.professional.study_salary import SalaryCard as SC

        salary_ids   = data.get("salary_ids", [])
        use_heritage = int(data.get("use_heritage", 0))

        # Déplacer les salaires sélectionnés → salaire dépensé
        for sid in salary_ids:
            for salary in list(current_player.played["vie professionnelle"]):
                if isinstance(salary, SC) and salary.id == sid:
                    current_player.played["vie professionnelle"].remove(salary)
                    current_player.add_card_to_salaire_depense(salary)
                    break

        # Déduire l'héritage utilisé
        if use_heritage > 0:
            current_player.heritage = max(0, current_player.heritage - use_heritage)

        # Retirer de la main et poser
        if self.apply_card_effect(game, current_player):
            current_player.hand.remove(self)
            current_player.add_card_to_played(self)


# ------------------------------------------------------------------ #
#  Maison                                                              #
# ------------------------------------------------------------------ #

class HouseCard(AquisitionCard):
    """Carte maison — 50 % de réduction si marié(e), gratuite avec Architecte."""

    def __init__(self, house_type: str, cost: int, smiles: int, image_path: str):
        super().__init__(cost, smiles, image_path)
        self.house_type: str = house_type

    def __str__(self) -> str:
        return f"{self.house_type} — HouseCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "house", "subtype": self.house_type, "cost": self.cost})
        return base

    def get_card_rule(self) -> str:
        return (
            f"Carte Maison ({self.house_type}) — {self.smiles} smiles, coût {self.cost}.\n"
            "- 50% moins chère si marié(e).\n"
            "- Gratuite une fois avec Architecte.\n"
            "- Les salaires investis sont protégés.\n"
        )

    def _effective_cost(self, current_player: "Player") -> int:
        if "house_free" in current_player.get_power():
            return 0
        return self._original_cost // 2 if current_player.is_married() else self._original_cost

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if "house_free" in current_player.get_power():
            return True, ""
        return super().can_be_played(current_player, game)

    def play_card(self, game: "Game", current_player: "Player") -> None:
        self.cost = self._effective_cost(current_player)
        if self.cost == 0:
            # Gratuit (Architecte) : poser directement sans overlay
            self._use_architect_power(current_player)
            if self.apply_card_effect(game, current_player):
                current_player.hand.remove(self)
                current_player.add_card_to_played(self)
        else:
            super().play_card(game, current_player)

    def resolve(self, game: "Game", current_player: "Player", data: dict) -> None:
        super().resolve(game, current_player, data)
        self.cost = self._original_cost  # réinitialiser pour la prochaine lecture

    def _use_architect_power(self, current_player: "Player") -> None:
        from app.cards.concrete.professional.job import ArchitecteJob
        for job in current_player.get_job():
            if isinstance(job, ArchitecteJob):
                job.use_power()
                break


# ------------------------------------------------------------------ #
#  Voyage                                                              #
# ------------------------------------------------------------------ #

class TravelCard(AquisitionCard):
    """Carte voyage — gratuite avec le Pilote de ligne."""

    def __init__(self, image_path: str):
        super().__init__(3, 1, image_path)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "travel", "cost": self.cost})
        return base

    def get_card_rule(self) -> str:
        return f"Carte Voyage — {self.smiles} smiles, coût {self._original_cost} (gratuit avec Pilote).\n"

    def _effective_cost(self, current_player: "Player") -> int:
        return 0 if "travel_free" in current_player.get_power() else self._original_cost

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if "travel_free" in current_player.get_power():
            return True, ""
        return super().can_be_played(current_player, game)

    def play_card(self, game: "Game", current_player: "Player") -> None:
        self.cost = self._effective_cost(current_player)
        if self.cost == 0:
            if self.apply_card_effect(game, current_player):
                current_player.hand.remove(self)
                current_player.add_card_to_played(self)
        else:
            super().play_card(game, current_player)

    def resolve(self, game: "Game", current_player: "Player", data: dict) -> None:
        super().resolve(game, current_player, data)
        self.cost = self._original_cost


# ------------------------------------------------------------------ #
#  Concert                                                             #
# ------------------------------------------------------------------ #

class ConcertTicket(AquisitionCard):
    """Concert — acquisition générique avec coût et smiles variables."""
    pass


# ------------------------------------------------------------------ #
#  Sabre                                                               #
# ------------------------------------------------------------------ #

class SabreCard(AquisitionCard):
    """Sabre — renvoie un coup dur reçu si Béatrix est posée."""

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.personal.children import BeatrixChild
        has_beatrix = any(
            isinstance(c, BeatrixChild)
            for c in current_player.get_played_vie_perso()
        )
        if not has_beatrix:
            return True  # Pose normalement, sans pouvoir

        receivable = [
            h for h in current_player.received_hardships
            if h.can_be_played(current_player, game)[0]
        ]
        if not receivable:
            return True  # Béatrix présente mais aucun coup dur à renvoyer

        emit("select_sabre", {
            "card_id":            self.id,
            "opponents":          [p.to_dict() for p in game.players if p.id != current_player.id],
            "received_hardships": [h.to_dict() for h in receivable],
        }, room=current_player.session_id)

        game.pending_interaction = {
            "type":      "sabre_selection",
            "card_id":   self.id,
            "player_id": current_player.id,
        }
        return False  # La carte sera posée après resolve() via events.py

    def resolve(self, game: "Game", current_player: "Player", data: dict) -> None:
        target_id   = data.get("target_id")
        hardship_id = data.get("hardship_id")
        if target_id is None or hardship_id is None:
            return
        target = game.players[target_id]
        for card in list(current_player.received_hardships):
            if card.id == hardship_id:
                current_player.received_hardships.remove(card)
                card.apply_effect(game, target, current_player)
                target.received_hardships.append(card)
                break


# ------------------------------------------------------------------ #
#  Nounou                                                              #
# ------------------------------------------------------------------ #

class NounouCard(AquisitionCard):
    """Nounou — place tous les enfants en salaires dépensés."""

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.personal.children import ChildCard
        for child in list(current_player.get_played_vie_perso()):
            if isinstance(child, ChildCard):
                current_player.remove_card_from_played(child)
                current_player.add_card_to_salaire_depense(child)
        return True