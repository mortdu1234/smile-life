"""
Hiérarchie des cartes métier.
"""
import random
from threading import Event
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.card import Card
from app.core.io_context import emit

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


class JobCard(Card):
    """Carte métier de base."""

    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(image_path)
        self.job_name: str = job_name
        self.salary: int = salary
        self.studies: int = studies
        self.status: str = ""
        self.power: list[str] = []
        self.smiles: int = 2

    def get_power(self) -> list[str]:
        power = list(self.power)
        if self.status == "fonctionnaire":
            power.append("no_fire")
        return power

    def get_salary(self) -> int:
        return self.salary

    def __str__(self) -> str:
        return f"{self.job_name} — JobCard"

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "type": "job",
            "subtype": self.job_name,
            "salary": self.salary,
            "studies": self.studies,
            "status": self.status,
            "power": self.power,
        })
        return base

    def get_card_rule(self) -> str:
        return (
            f"Carte Métier ({self.job_name}) — {self.smiles} smiles.\n"
            f"- Nécessite {self.studies} niveau(x) d'études.\n"
            f"- Salaire maximum : {self.salary}.\n"
        )

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        from app.cards.concrete.professional.study_salary import StudyCard
        study_count = current_player.count_studies()
        if study_count < self.studies:
            return False, f"Il vous faut {self.studies} niveau(x) d'études"
        if current_player.has_job() and "2_jobs" not in current_player.get_power():
            return False, "Vous avez déjà un métier"
        powers = current_player.get_power()
        if "no_job_with_study_5" in powers and self.studies >= 5:
            return False, "Plafond de verre — métier de niveau 5/6 interdit"
        if "no_job_with_study_6" in powers and self.studies >= 6:
            return False, "Plafond de verre — métier de niveau 6 interdit"
        return True, ""

    def play_card(self, game: "Game", current_player: "Player") -> None:
        super().play_card(game, current_player)
        self.apply_instant_power(game, current_player)

    def discard_play_card(self, game: "Game", effected_player: "Player") -> None:
        effected_player.remove_card_from_played(self)
        game.discard.append(self)
        self.loosing_continuous_power(game, effected_player)
        if effected_player.id == game.current_player and self.status != "intérimaire":
            game.next_player()

    def apply_instant_power(self, game: "Game", current_player: "Player") -> None:
        """Pouvoir déclenché à la pose — à surcharger."""
        pass

    def loosing_continuous_power(self, game: "Game", effected_player: "Player") -> None:
        """Nettoyage lors de la perte du métier — à surcharger."""
        pass


# ------------------------------------------------------------------ #
#  Métiers concrets                                                    #
# ------------------------------------------------------------------ #

class AstronauteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)

    def get_card_rule(self) -> str:
        base = super().get_card_rule()
        return base + "- Pouvoir instantané : récupérer une carte posable depuis la défausse.\n"

    def apply_instant_power(self, game, current_player):
        available = [c for c in game.discard if c.can_be_played(current_player, game)[0]]
        emit("select_astronaute_card", {
            "card_id": self.id,
            "cards": [c.to_dict() for c in available],
        }, room=current_player.session_id)
        game.pending_interaction = {
            "type": "astronaute_selection",
            "card_id": self.id,
            "player_id": current_player.id,
        }

    def resolve(self, game, current_player, data):
        selected_id = data.get("selected_card_id")
        if not selected_id:
            return
        for c in game.discard:
            if c.id == selected_id:
                game.discard.remove(c)
                current_player.hand.append(c)
                c.play_card(game, current_player)
                break


class BanditJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["no_tax", "no_fire"]

    def get_card_rule(self) -> str:
        base = super().get_card_rule()
        return base + "- Immunisé aux impôts et au licenciement.\n"

    def can_be_played(self, current_player: "Player", game: "Game") -> tuple[bool, str]:
        for player in game.players:
            if player.has_job() and "no_bandit" in player.get_power():
                return False, "Un métier empêche le bandit"
        return super().can_be_played(current_player, game)

    def apply_instant_power(self, game: "Game", current_player: "Player") -> None:
        current_player.has_been_bandit = True


class MediumJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)

    def get_card_rule(self) -> str:
        base = super().get_card_rule()
        return base + "- Pouvoir instantané : voir les 13 prochaines cartes de la pioche.\n"

    def apply_instant_power(self, game, current_player):
        next_cards = [game.deck[-i] for i in range(1, 1 + min(13, len(game.deck)))]
        emit("medium_show_cards", {
            "card_id": self.id,
            "cards": [c.to_dict() for c in next_cards],
            "total": len(game.deck),
        }, room=current_player.session_id)


class JournalisteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["prix_possible"]
        self.is_link: bool = False

    def get_salary(self) -> int:
        return 4 if self.is_link else self.salary

    def get_card_rule(self) -> str:
        base = super().get_card_rule()
        return base + "- Grand Prix d'Excellence possible.\n- Pouvoir : voir la main de tous les joueurs.\n"

    def apply_instant_power(self, game, current_player):
        hands_info = {
            p.name: [c.to_dict() for c in p.hand]
            for p in game.players
            if p.connected and p.id != current_player.id
        }
        emit("show_all_hands", {
            "card_id": self.id,
            "hands": hands_info,
        }, room=current_player.session_id)


class ChefDesAchatsJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)

    def get_card_rule(self) -> str:
        base = super().get_card_rule()
        return base + "- Pouvoir : récupérer une acquisition de la défausse.\n"

    def apply_instant_power(self, game, current_player):
        from app.cards.concrete.acquisitions.cards import AquisitionCard
        available = [c for c in game.discard
                    if isinstance(c, AquisitionCard) and c.can_be_played(current_player, game)[0]]
        emit("select_chef_achats_acquisition", {
            "card_id": self.id,
            "acquisitions": [a.to_dict() for a in available],
        }, room=current_player.session_id)
        game.pending_interaction = {
            "type": "chef_achats_selection",
            "card_id": self.id,
            "player_id": current_player.id,
        }

    def resolve(self, game, current_player, data):
        selected_id = data.get("acquisition_id")
        if not selected_id:
            return
        for c in game.discard:
            if c.id == selected_id:
                current_player.hand.append(c)
                game.discard.remove(c)
                c.play_card(game, current_player)
                break


class ArchitecteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["house_free"]
        self._power_used: bool = False

    def get_card_rule(self) -> str:
        base = super().get_card_rule()
        return base + "- Pouvoir : une maison gratuite (usage unique).\n"

    def use_power(self) -> None:
        self._power_used = True
        if "house_free" in self.power:
            self.power.remove("house_free")

    def get_power(self) -> list[str]:
        return super().get_power() + ([] if self._power_used else ["house_free"])


class InfirmierJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["no_maladie"]

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Immunisé à la Maladie.\n"


class ChirurgienJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["no_illness", "extra_study"]

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Immunisé à la Maladie. Études illimitées.\n"


class DesignerJob(JobCard):
    pass


class GaragisteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["no_accident"]

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Immunisé à l'Accident.\n"


class JardinierJob(JobCard):
    pass


class MedecinJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["no_maladie", "extra_study"]

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Immunisé à la Maladie. Études illimitées.\n"


class MilitaireJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "fonctionnaire"
        self.power = ["no_attentat"]

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Fonctionnaire (non licenciable). Bloque les attentats.\n"


class PharmacienJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["no_maladie"]

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Immunisé à la Maladie.\n"


class PiloteDeLigneJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["travel_free"]

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Tous les voyages sont gratuits.\n"


class PizzaioloJob(JobCard):
    pass


class PlombierJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Intérimaire : peut démissionner à tout moment.\n"


class ServeurJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Intérimaire : peut démissionner à tout moment.\n"


class StripTeaserJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"


class EcrivainJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["prix_possible"]
        self.is_link: bool = False

    def get_salary(self) -> int:
        return 4 if self.is_link else self.salary

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Grand Prix d'Excellence possible.\n"


class YoutuberJob(JobCard):
    pass


class CoiffeurJob(JobCard):
    pass


class DeejayJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"

    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Intérimaire. Mélange les mains à la pose.\n"

    def apply_instant_power(self, game: "Game", current_player: "Player") -> None:
        all_cards: list = []
        for player in game.players:
            all_cards.extend(player.hand)
        random.shuffle(all_cards)
        for player in game.players:
            nb = len(player.hand)
            player.hand = [all_cards.pop() for _ in range(nb)]

class AvocatJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.power = ["no_divorce"]
        
    def get_card_rule(self) -> str:
        return super().get_card_rule() + "- Intérimaire. Mélange les mains à la pose.\n"

class BarmanJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = ["infinite_flirt"]
    
class ChefDesVentesJob(JobCard):
    pass

class ChercheurJob(JobCard):
    pass

class GourouJob(JobCard):
    pass

class GrandProfJob(JobCard):
    pass

class PolicierJob(JobCard):
    pass

class ProfJob(JobCard):
    pass


    