"""
Cartes coup dur — toutes les sous-classes de HardshipCard.
"""
import random
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.hardship_card import HardshipCard
from app.cards.base.permanent_effect import PermanentEffet
from app.core.io_context import emit

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class AccidentCard(HardshipCard):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "Accident"
        return base

    def get_card_rule(self) -> str:
        return "Accident — fait passer un tour au joueur visé."

    def other_rules(self, game, current_player, player) -> bool:
        return "no_accident" in player.get_power()

    def apply_effect(self, game, target_player, current_player) -> None:
        target_player.skip_turns += 1


class MaladieCard(HardshipCard):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "Maladie"
        return base

    def get_card_rule(self) -> str:
        return "Maladie — fait passer un tour."

    def other_rules(self, game, current_player, player) -> bool:
        return player.has_job() and "no_maladie" in player.get_power()

    def apply_effect(self, game, target_player, current_player) -> None:
        target_player.skip_turns += 1


class TaxCard(HardshipCard):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "TAX"
        return base

    def get_card_rule(self) -> str:
        return "Impôt sur le Revenu — retire le dernier salaire posé."

    def other_rules(self, game, current_player, player) -> bool:
        if not player.has_job():
            return True
        if "no_tax" in player.get_power():
            return True
        if player.get_available_salary_sum() == 0:
            return True
        return False

    def apply_effect(self, game, target_player, current_player) -> None:
        from app.cards.concrete.professional.study_salary import SalaryCard
        salaries = [c for c in target_player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
        if salaries:
            card = salaries[-1]
            target_player.remove_card_from_played(card)
            game.discard.append(card)


class BurnOutCard(HardshipCard):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "BurnOut"
        return base

    def get_card_rule(self) -> str:
        return "Burn-Out — fait passer un tour (nécessite un métier)."

    def other_rules(self, game, current_player, player) -> bool:
        return not player.has_job()

    def apply_effect(self, game, target_player, current_player) -> None:
        target_player.skip_turns += 1


class DivorceCard(HardshipCard):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "Divorce"
        return base

    def get_card_rule(self) -> str:
        return "Divorce — retire le mariage (et enfants si adultère)."

    def other_rules(self, game, current_player, player) -> bool:
        if not player.is_married():
            return True
        if player.has_job() and "no_divorce" in player.get_power():
            return True
        return False

    def apply_effect(self, game, target_player, current_player) -> None:
        from app.cards.concrete.personal.flirt import AdulteryCard, MarriageCard
        from app.cards.concrete.personal.children import ChildCard
        cards_played = tuple(target_player.played["vie personnelle"])
        if target_player.has_adultery():
            for card in cards_played:
                if isinstance(card, (AdulteryCard, MarriageCard, ChildCard)):
                    target_player.remove_card_from_played(card)
                    game.discard.append(card)
        else:
            for card in cards_played:
                if isinstance(card, MarriageCard):
                    target_player.remove_card_from_played(card)
                    game.discard.append(card)


class LicenciementCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.targeted_job_id: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "Licenciement"
        return base

    def get_card_rule(self) -> str:
        return "Licenciement — retire le métier (sauf fonctionnaire)."

    def other_rules(self, game, current_player, player) -> bool:
        if not player.has_job():
            return True
        if "no_fire" in player.get_power():
            return True
        return False

    def apply_effect(self, game, target_player, current_player):
        target_jobs = target_player.get_job()
        if len(target_jobs) == 1:
            target_jobs[0].discard_play_card(game, target_player)
            return
        emit("select_job_licenciement", {
            "card_id": self.id,
            "jobs": [j.to_dict() for j in target_jobs],
        }, room=current_player.session_id)
        game.pending_interaction = {
            "type": "licenciement_job_selection",
            "card_id": self.id,
            "player_id": current_player.id,   # c'est le joueur qui a joué le coup dur
            "target_player_id": target_player.id,
        }

    def resolve(self, game, current_player, data):
        target_player_id = game.pending_interaction["target_player_id"]  # récupéré avant clear
        target_player = game.players[target_player_id]
        target_jobs = target_player.get_job()
        job_id = data.get("target_job_id")
        job = next((j for j in target_jobs if j.id == job_id), None) or random.choice(target_jobs)
        job.discard_play_card(game, target_player)


class RedoublementCard(HardshipCard):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "Redoublement"
        return base

    def get_card_rule(self) -> str:
        return "Redoublement — retire la dernière carte étude (sans métier seulement)."

    def other_rules(self, game, current_player, player) -> bool:
        from app.cards.concrete.professional.study_salary import StudyCard
        if player.has_job():
            return True
        if not any(isinstance(c, StudyCard) for c in player.played["vie professionnelle"]):
            return True
        return False

    def apply_effect(self, game, target_player, current_player) -> None:
        from app.cards.concrete.professional.study_salary import StudyCard
        studies = [c for c in target_player.played["vie professionnelle"] if isinstance(c, StudyCard)]
        if studies:
            card = studies[-1]
            target_player.remove_card_from_played(card)
            game.discard.append(card)


class PrisonCard(HardshipCard):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "Prison"
        return base

    def get_card_rule(self) -> str:
        return "Prison — passe 3 tours, perd 2 cartes, perd son métier Bandit."

    def other_rules(self, game, current_player, player) -> bool:
        from app.cards.concrete.professional.job import BanditJob
        if player.has_job():
            return not any(isinstance(j, BanditJob) for j in player.get_job())
        return True

    def apply_effect(self, game, target_player, current_player) -> None:
        target_player.skip_turns += 3
        for _ in range(2):
            if target_player.hand:
                card = random.choice(target_player.hand)
                target_player.hand.remove(card)
                game.discard.append(card)
        for _ in range(2):
            if game.deck:
                target_player.hand.append(game.deck.pop())
        LicenciementCard("").apply_effect(game, target_player, current_player)


class AttentatCard(HardshipCard):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "Attentat"
        return base

    def get_card_rule(self) -> str:
        return "Attentat — défausse tous les enfants posés de tous les joueurs."

    def can_be_played(self, current_player, game) -> tuple[bool, str]:
        for player in game.players:
            if player.has_job() and "no_attentat" in player.get_power():
                return False, "Un métier bloque les attentats"
        return True, ""

    def get_available_targets(self, game, current_player) -> list[dict]:
        return [
            {**player.to_dict(), "immune": False}
            for player in game.players
        ]

    def apply_effect(self, game, target_player, current_player) -> None:
        from app.cards.concrete.personal.children import ChildCard
        for player in game.players:
            for card in list(player.played["vie personnelle"]):
                if isinstance(card, ChildCard):
                    player.remove_card_from_played(card)
                    game.discard.append(card)


class ChargeMentalHardhip(HardshipCard):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "ChargeMental"
        return base

    def get_card_rule(self) -> str:
        return "Charge Mentale — jette un enfant (nécessite un enfant et un métier)."

    def other_rules(self, game, current_player, player) -> bool:
        from app.cards.concrete.personal.children import ChildCard
        if not player.has_job():
            return True
        children = [c for c in player.get_played_vie_perso() if isinstance(c, ChildCard)]
        return len(children) == 0

    def apply_effect(self, game, target_player, current_player) -> None:
        from app.cards.concrete.personal.children import ChildCard
        children = [c for c in target_player.get_played_vie_perso() if isinstance(c, ChildCard)]
        if children:
            card = random.choice(children)
            target_player.remove_card_from_played(card)
            game.discard.append(card)


class GynocratieHardship(HardshipCard, PermanentEffet):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "GynocratieHardship"
        return base

    def get_card_rule(self) -> str:
        return "Gynocratie — chaque fille vaut 1 smile de moins. Ne se cumule pas avec Phalocratie."

    def other_rules(self, game, current_player, player) -> bool:
        from app.cards.concrete.hardship.cards import PhalocratieHardship
        for card in player.get_played_effet_permanent():
            if isinstance(card, (PhalocratieHardship, GynocratieHardship)):
                return True
        return False

    def get_power(self) -> list[str]:
        return []


class PhalocratieHardship(HardshipCard, PermanentEffet):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "PhalocratieHardship"
        return base

    def get_card_rule(self) -> str:
        return "Phalocratie — chaque garçon vaut 1 smile de moins. Ne se cumule pas avec Gynocratie."

    def other_rules(self, game, current_player, player) -> bool:
        for card in player.get_played_effet_permanent():
            if isinstance(card, (PhalocratieHardship, GynocratieHardship)):
                return True
        return False

    def get_power(self) -> list[str]:
        return []


class PlafondDeVerreHardship(HardshipCard, PermanentEffet):
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["subtype"] = "PlafondDeVerreHardship"
        return base

    def get_card_rule(self) -> str:
        return "Plafond de Verre — interdit les métiers de niveau 5 ou 6."

    def get_power(self) -> list[str]:
        return ["no_job_with_study_5", "no_job_with_study_6"]


class PorcHardship(HardshipCard):
    def get_card_rule(self) -> str:
        return "Balance Ton Porc — défausse le mariage et le métier du joueur."

    def other_rules(self, game, current_player, player) -> bool:
        return not player.is_married() or not player.has_job()

    def apply_effect(self, game, target_player, current_player) -> None:
        DivorceCard("").apply_effect(game, target_player, current_player)
        LicenciementCard("").apply_effect(game, target_player, current_player)