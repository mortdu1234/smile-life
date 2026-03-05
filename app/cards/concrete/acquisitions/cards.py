"""
Cartes acquisitions — achetables avec des salaires.
"""
from typing import TYPE_CHECKING, Dict, Any

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
        return (
            f"Carte Acquisition — {self.smiles} smiles, coût : {self.cost} liasses.\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if current_player.get_available_salary_sum() < self.cost:
            return False, f"Il vous faut une somme de salaires de {self.cost}"
        return True, ""

    def play_card(self, game, current_player):
        emit("select_salaries_for_acquisition", {
            "card": self.to_dict(),
            "required_cost": self.cost,
            "available_salaries": [...],
            "heritage_available": current_player.heritage,
        }, room=current_player.session_id)  # ← ajouter room=
        game.pending_interaction = {
            "type": "salary_selection",
            "card_id": self.id,
            "player_id": current_player.id,
        }

    def resolve(self, game, current_player, data):
        from app.cards.concrete.professional.study_salary import SalaryCard as SC
        salary_ids = data.get("salary_ids", [])
        use_heritage = data.get("use_heritage", 0)
        for salary_id in salary_ids:
            for salary in current_player.played["vie professionnelle"]:
                if isinstance(salary, SC) and salary.id == salary_id:
                    current_player.played["vie professionnelle"].remove(salary)
                    current_player.played["salaire dépensé"].append(salary)
                    break
        if use_heritage > 0:
            current_player.heritage -= use_heritage
        super().play_card(game, current_player)


class HouseCard(AquisitionCard):
    """Carte maison."""

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
            "- Les salaires investis sont protégés.\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if "house_free" in current_player.get_power():
            return True, ""
        required = self.cost // 2 if current_player.is_married() else self.cost
        if current_player.get_available_salary_sum() < required:
            return False, f"Il vous faut {required} liasses"
        return True, ""

    def play_card(self, game, current_player):
        if "house_free" in current_player.get_power():
            self.cost = 0
            for job in current_player.get_job():
                if isinstance(job, ArchitecteJob):
                    job.use_power()
        elif current_player.is_married():
            self.cost = self.cost // 2
        super().play_card(game, current_player)

    def resolve(self, game, current_player, data):
        super().resolve(game, current_player, data)
        self.cost = self._original_cost


class TravelCard(AquisitionCard):
    """Carte voyage."""

    def __init__(self, image_path: str):
        super().__init__(3, 1, image_path)

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({"type": "travel", "cost": self.cost})
        return base

    def get_card_rule(self) -> str:
        return f"Carte Voyage — {self.smiles} smiles, coût {self.cost} (gratuit avec Pilote).\n"

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        if "travel_free" in current_player.get_power():
            return True, ""
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        if "travel_free" in current_player.get_power():
            self.cost = 0
        super().play_card(game, current_player)

    def resolve(self, game, current_player, data):
        super().resolve(game, current_player, data)
        self.cost = self._original_cost


class ConcertTicket(AquisitionCard):
    pass


class SabreCard(AquisitionCard):
    """Sabre — renvoie des coups durs reçus grâce à Béatrix."""

    def __init__(self, cost: int, smiles: int, image_path: str):
        super().__init__(cost, smiles, image_path)

    def apply_card_effect(self, game, current_player):
        from app.cards.concrete.personal.children import BeatrixChild
        if not any(isinstance(c, BeatrixChild) for c in current_player.get_played_vie_perso()):
            return True
        receivable = [h for h in current_player.received_hardships
                    if h.can_be_played(current_player, game)[0]]
        if not receivable:
            return True
        emit("select_sabre", {
            "card_id": self.id,
            "opponents": [p.to_dict() for p in game.players if p != current_player],
            "received_hardships": [h.to_dict() for h in receivable],
        }, room=current_player.session_id)
        game.pending_interaction = {
            "type": "sabre_selection",
            "card_id": self.id,
            "player_id": current_player.id,
        }
        return False
    
    def resolve(self, game, current_player, data):
        target_id = data.get("target_id")
        hardship_id = data.get("hardship_id")
        if target_id is None or hardship_id is None:
            return
        target = game.players[target_id]
        for card in current_player.received_hardships:
            if card.id == hardship_id:
                current_player.received_hardships.remove(card)
                card.apply_effect(game, target, current_player)
                target.received_hardships.append(card)
                break


class NounouCard(AquisitionCard):
    """Nounou — place tous les enfants en salaires dépensés."""

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.personal.children import ChildCard
        for child in list(current_player.get_played_vie_perso()):
            if isinstance(child, ChildCard):
                current_player.remove_card_from_played(child)
                current_player.add_card_to_salaire_depense(child)
        return True
