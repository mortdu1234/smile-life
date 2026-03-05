"""
Cartes spéciales — toutes les sous-classes de SpecialCard.
"""
import random
from threading import Event
from typing import TYPE_CHECKING, Dict, Any

from app.cards.base.special_card import SpecialCard
from app.cards.base.permanent_effect import PermanentEffet
from app.core.io_context import emit

if TYPE_CHECKING:
    from app.core.player import Player
    from app.core.game import Game


# ------------------------------------------------------------------ #
#  Cartes à effet permanent (Clichés, GirlPower, EgalitéSalaires)    #
# ------------------------------------------------------------------ #

class EgaliteDesSalaireCard(SpecialCard, PermanentEffet):
    def __init__(self, image_path: str):
        super().__init__("egalite des salaire", image_path)

    def get_card_rule(self) -> str:
        return "Égalité des Salaires — votre plafond salarial = le meilleur joueur. Permanent."

    def get_power(self) -> list[str]:
        return ["egalite_salaire"]


class ClicheCard(SpecialCard, PermanentEffet):
    def __init__(self, image_path: str):
        super().__init__("cliché", image_path)


class ClicheAccident(ClicheCard):
    def get_card_rule(self) -> str:
        return "Cliché Accident — immunisé aux accidents. Permanent."

    def get_power(self) -> list[str]:
        return ["no_accident"]


class ClicheFlirt(ClicheCard):
    def get_card_rule(self) -> str:
        return "Cliché Flirt — flirt illimité avant le mariage. Permanent."

    def get_power(self) -> list[str]:
        return ["unlimited_flirt"]


class ClicheMetier(ClicheCard):
    def get_card_rule(self) -> str:
        return "Cliché Métier — vous pouvez cumuler 2 métiers. Permanent."

    def get_power(self) -> list[str]:
        return ["2_jobs"]


class GirlPowerCard(SpecialCard, PermanentEffet):
    """Chaque fille posée permet de rejouer une carte spéciale."""

    def __init__(self, image_path: str):
        super().__init__("girl power", image_path)
        self.special_cards_uses: list = []
        self.selection_event: Event = Event()
        self.special_card_id: str | None = None

    def get_card_rule(self) -> str:
        return "Girl Power — chaque fille posée permet de rejouer une carte spéciale. Permanent."

    def confirm_selection(self, data: dict) -> None:
        self.special_card_id = data.get("selected_card_id")
        self.selection_event.set()

    def discard_selection(self, data: dict) -> None:
        self.selection_event.set()

    def effect(self, game: "Game", current_player: "Player") -> None:
        specials = [
            c for c in current_player.get_played_carte_speciale()
            if isinstance(c, SpecialCard)
            and c not in self.special_cards_uses
            and c.can_be_played(current_player, game)[0]
        ]
        emit("select_girl_power_card", {
            "card_id": self.id,
            "special_cards": [c.to_dict() for c in specials],
        })
        self.selection_event.wait()
        self.selection_event.clear()

        if self.special_card_id is not None:
            selected = current_player.get_played_carte_speciale_by_id(self.special_card_id)
            if selected:
                self.special_cards_uses.append(selected)
                current_player.remove_card_from_played(selected)
                current_player.add_card_to_hand(selected)
                selected.play_card(game, current_player)

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.personal.children import FemaleChild
        nb_filles = sum(
            1 for c in current_player.get_played_vie_perso()
            if isinstance(c, FemaleChild)
        )
        for _ in range(nb_filles):
            self.effect(game, current_player)
        return True

    def get_power(self) -> list[str]:
        return ["double_special_card"]


# ------------------------------------------------------------------ #
#  Cartes à effet unique                                               #
# ------------------------------------------------------------------ #

class RedistributionDesTachesCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("redistribution des taches", image_path)
        self.selection_event: Event = Event()
        self.choices: dict | None = None

    def get_card_rule(self) -> str:
        return "Redistribution des Tâches — redistribue tous les métiers à ta guise."

    def confirm_selection(self, data: dict) -> None:
        self.choices = data.get("distribution")
        self.selection_event.set()

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        initial_data: dict = {}
        job_map: dict = {}
        for player in game.players:
            jobs = player.get_job()
            initial_data[player.id] = [[j.id for j in jobs], len(jobs)]
            for job in jobs:
                job_map[job.id] = (job, player)

        emit("redistribution_des_taches", {
            "card_id": self.id,
            "data_initial": initial_data,
        })
        self.selection_event.wait()
        self.selection_event.clear()

        if self.choices:
            for job_id, (job_card, orig_player) in job_map.items():
                orig_player.remove_card_from_played(job_card)
            for player_id, job_ids in self.choices.items():
                player = game.players[int(player_id)]
                for job_id in job_ids:
                    if job_id in job_map:
                        player.add_card_to_played(job_map[job_id][0])
        return True


class SoireeEntreFilleCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("soirée entre fille", image_path)

    def get_card_rule(self) -> str:
        return "Soirée Entre Filles — récupère tous les enfants en main et les pose sans conditions."

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.personal.children import ChildCard
        for player in game.players:
            nb = 0
            for card in list(player.hand):
                if isinstance(card, ChildCard):
                    current_player.add_card_to_played(card)
                    player.remove_card_from_hand(card)
                    nb += 1
            for _ in range(nb):
                if game.deck:
                    player.add_card_to_hand(game.get_card_from_deck())
        return True


class CoupDeFoudreCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("coup de foudre", image_path)
        self.selection_event: Event = Event()
        self.target_player_id: int | None = None

    def get_card_rule(self) -> str:
        return "Coup de Foudre — vole le mariage d'un joueur."

    def can_be_played(self, current_player, game) -> tuple[bool, str]:
        if current_player.is_married():
            return False, "Vous êtes déjà marié(e)"
        if any(p.is_married() for p in game.players if p != current_player):
            return True, ""
        return False, "Aucun joueur n'est marié"

    def confirm_selection(self, data: dict) -> None:
        self.target_player_id = data.get("target_player_id")
        self.selection_event.set()

    def discard_selection(self, data: dict) -> None:
        self.target_player_id = None
        self.selection_event.set()

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        targets = [
            {**p.to_dict(), "immune": p == current_player or not p.is_married()}
            for p in game.players
        ]
        emit("select_coup_de_foudre_target", {
            "card_id": self.id,
            "available_targets": targets,
        })
        self.selection_event.wait()
        self.selection_event.clear()

        if self.target_player_id is not None:
            target = game.players[self.target_player_id]
            marriage = target.get_marriage()
            if marriage:
                target.remove_card_from_played(marriage)
                current_player.add_card_to_vie_perso(marriage)
        return True


class ErreurDetiquetageCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("erreur etiquetage", image_path)
        self.selection_event: Event = Event()
        self.target_player_id: int | None = None
        self.current_child_id: str | None = None
        self.target_child_id: str | None = None

    def get_card_rule(self) -> str:
        return "Erreur d'Étiquetage — échange un de vos enfants avec un autre joueur."

    def can_be_played(self, current_player, game) -> tuple[bool, str]:
        from app.cards.concrete.personal.children import ChildCard
        for player in game.players:
            if player != current_player:
                if any(isinstance(c, ChildCard) for c in player.get_played_vie_perso()):
                    return True, ""
        return False, "Pas de cible disponible"

    def confirm_children_selection(self, data: dict) -> None:
        self.current_child_id = data.get("current_child_id")
        self.target_child_id = data.get("target_child_id")
        self.selection_event.set()

    def confirm_target_selection(self, data: dict) -> None:
        self.target_player_id = int(data.get("target_id"))
        self.selection_event.set()

    def discard_selection(self, data: dict) -> None:
        self.selection_event.set()

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.personal.children import ChildCard
        targets = [
            {
                **p.to_dict(),
                "immune": p == current_player or not any(isinstance(c, ChildCard) for c in p.get_played_vie_perso()),
            }
            for p in game.players
        ]
        emit("select_erreur_etiquetage_target", {
            "card_id": self.id,
            "available_targets": targets,
        })
        self.selection_event.wait()
        self.selection_event.clear()

        if self.target_player_id is None:
            return True

        target_player = game.players[self.target_player_id]
        children_current = [c for c in current_player.get_played_vie_perso() if isinstance(c, ChildCard)]
        children_target = [c for c in target_player.get_played_vie_perso() if isinstance(c, ChildCard)]

        emit("select_erreur_etiquetage_children", {
            "card_id": self.id,
            "current_children": [c.to_dict() for c in children_current],
            "target_children": [c.to_dict() for c in children_target],
        })
        self.selection_event.wait()
        self.selection_event.clear()

        if self.current_child_id and self.target_child_id:
            c1 = current_player.get_played_card_by_id(self.current_child_id)
            c2 = target_player.get_played_card_by_id(self.target_child_id)
            if c1 and c2:
                current_player.remove_card_from_played(c1)
                target_player.remove_card_from_played(c2)
                current_player.add_card_to_played(c2)
                target_player.add_card_to_played(c1)
        return True


class TsunamiCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("tsunami", image_path)

    def get_card_rule(self) -> str:
        return "Tsunami — mélange toutes les mains et les redistribue."

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        current_player.hand.remove(self)
        counts = [len(p.hand) for p in game.players]
        all_cards = []
        for p in game.players:
            all_cards.extend(p.hand)
        random.shuffle(all_cards)
        for idx, player in enumerate(game.players):
            player.hand = [all_cards.pop() for _ in range(counts[idx])]
        current_player.hand.append(self)
        return True


class HeritageCard(SpecialCard):
    def __init__(self, image_path: str, heritage_value: int):
        super().__init__("heritage", image_path)
        self.value: int = heritage_value

    def get_card_rule(self) -> str:
        return f"Héritage — ajoute {self.value} liasse(s) disponibles pour investir."

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        current_player.heritage += self.value
        return True


class PistonCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("piston", image_path)
        self.selection_event: Event = Event()
        self.job_id: str | None = None

    def get_card_rule(self) -> str:
        return "Piston — pose un métier sans les études requises."

    def can_be_played(self, current_player, game) -> tuple[bool, str]:
        return not current_player.has_job(), ""

    def confirm_job_selection(self, data: dict) -> None:
        self.job_id = data.get("job_id")
        self.selection_event.set()

    def discard_job_selection(self, data: dict) -> None:
        self.selection_event.set()

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.professional.job import JobCard
        jobs_in_hand = [c for c in current_player.hand if isinstance(c, JobCard)]
        emit("select_piston_job", {
            "card_id": self.id,
            "available_jobs": [j.to_dict() for j in jobs_in_hand],
        })
        self.selection_event.wait()
        self.selection_event.clear()

        job_card = next((c for c in current_player.hand if c.id == self.job_id), None)
        if job_card:
            job_card.play_card(game, current_player)
            if game.deck:
                current_player.hand.append(game.deck.pop())
        return True


class VengeanceCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("vengeance", image_path)
        self.selection_event: Event = Event()
        self.target_player_id: int | None = None
        self.hardship_id: str | None = None

    def get_card_rule(self) -> str:
        return "Vengeance — attaque quelqu'un avec un coup dur reçu."

    def can_be_played(self, current_player, game) -> tuple[bool, str]:
        for card in current_player.received_hardships:
            if card.can_be_played(current_player, game)[0]:
                return True, ""
        return False, "Aucun coup dur disponible"

    def confirm_vengeance_selection(self, data: dict) -> None:
        self.target_player_id = int(data.get("target_id"))
        self.hardship_id = data.get("hardship_id")
        self.selection_event.set()

    def discard_vengeance_selection(self, data: dict) -> None:
        self.selection_event.set()

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        receivable = [h.to_dict() for h in current_player.received_hardships if h.can_be_played(current_player, game)[0]]
        others = [p.to_dict() for p in game.players if p != current_player]
        emit("select_vengeance", {
            "card_id": self.id,
            "received_hardships": receivable,
            "available_targets": others,
        })
        self.selection_event.wait()
        self.selection_event.clear()

        if self.target_player_id is not None and self.hardship_id:
            target = game.players[self.target_player_id]
            for card in current_player.received_hardships:
                if card.id == self.hardship_id:
                    current_player.received_hardships.remove(card)
                    card.apply_effect(game, target, current_player)
                    target.received_hardships.append(card)
                    break
        return True


class ChanceCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("chance", image_path)
        self.next_cards: list = []
        self.selection_event: Event = Event()
        self.selected_card_id: str | None = None

    def get_card_rule(self) -> str:
        return "Chance — pioche 3 cartes, en sélectionne 1, joue normalement."

    def confirm_card_selection(self, data: dict) -> None:
        self.selected_card_id = data.get("selected_card_id")
        self.selection_event.set()

    def discard_card_selection(self, data: dict) -> None:
        self.selection_event.set()

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        for _ in range(min(3, len(game.deck))):
            self.next_cards.append(game.deck.pop())
        emit("select_chance_card", {
            "card_id": self.id,
            "cards": [c.to_dict() for c in self.next_cards],
        }, room=current_player.session_id)
        self.selection_event.wait()
        self.selection_event.clear()

        for card in self.next_cards:
            if card.id == self.selected_card_id:
                current_player.hand.append(card)
            else:
                game.discard.append(card)
        self.next_cards = []
        return True


class EtoileFilanteCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("etoile filante", image_path)
        self.selection_event: Event = Event()
        self.selected_card_id: str | None = None

    def get_card_rule(self) -> str:
        return "Étoile Filante — choisit une carte de la défausse et la pose directement."

    def confirm_card_selection(self, data: dict) -> None:
        self.selected_card_id = data.get("selected_card_id")
        self.selection_event.set()

    def discard_card_selection(self, data: dict) -> None:
        self.selection_event.set()

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        playable = [c for c in game.discard if c.can_be_played(current_player, game)[0]]
        emit("select_star_card", {
            "card_id": self.id,
            "discard_cards": [c.to_dict() for c in playable],
        })
        self.selection_event.wait()
        self.selection_event.clear()

        card = next((c for c in game.discard if c.id == self.selected_card_id), None)
        if card:
            game.discard.remove(card)
            current_player.hand.append(card)
            card.play_card(game, current_player)
        return True


class CasinoCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("casino", image_path)
        self.selection_event: Event = Event()
        self.bet_card_id: str | None = None
        self.is_open: bool = False
        self.first_player_bet = None
        self.first_bet = None

    def get_card_rule(self) -> str:
        return (
            "Casino — ouvre le casino. Deux joueurs misent un salaire :\n"
            "- Valeurs identiques → le second gagne les deux.\n"
            "- Valeurs différentes → le premier gagne les deux.\n"
        )

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            "open": self.is_open,
            "first_bet": self.first_player_bet.to_dict() if self.first_bet else None,
            "second_bet": None,
        })
        return base

    def confirm_bet_selection(self, data: dict) -> None:
        self.bet_card_id = data.get("bet_card_id")
        self.selection_event.set()

    def discard_bet_selection(self, data: dict) -> None:
        self.selection_event.set()

    def bet_on_casino(self, game: "Game", current_player: "Player", is_opener: bool = False) -> None:
        from app.cards.concrete.professional.study_salary import SalaryCard
        salary_cards = [s.to_dict() for s in current_player.hand if isinstance(s, SalaryCard)]
        emit("select_casino_bet", {
            "card_id": self.id,
            "available_salaries": salary_cards,
        })
        self.selection_event.wait()
        self.selection_event.clear()

        if self.bet_card_id:
            from app.cards.concrete.professional.study_salary import SalaryCard as SC
            card = next((c for c in current_player.hand if c.id == self.bet_card_id), None)
            if card:
                if self.first_bet:
                    current_player.hand.remove(card)
                    if card.level == self.first_bet.level:
                        current_player.add_card_to_played(card)
                        current_player.add_card_to_played(self.first_bet)
                    else:
                        self.first_player_bet.add_card_to_played(card)
                        self.first_player_bet.add_card_to_played(self.first_bet)
                    self.first_bet = None
                    self.first_player_bet = None
                else:
                    current_player.hand.remove(card)
                    self.first_bet = card
                    self.first_player_bet = current_player
                    if is_opener and game.deck:
                        current_player.hand.append(game.deck.pop())
                game.broadcast_update()

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        self.bet_on_casino(game, current_player, True)
        return True

    def play_card(self, game: "Game", current_player: "Player") -> None:
        self.is_open = True
        game.casino_card = self
        self.apply_card_effect(game, current_player)
        current_player.hand.remove(self)


class AnniversaireCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("anniversaire", image_path)
        self.nb_player_to_give: int = 0
        self.selection_event: Event = Event()
        self.player_giver_id: int | None = None
        self.salary_id: str | None = None

    def get_card_rule(self) -> str:
        return "Anniversaire — tous les autres joueurs offrent un salaire posé."

    def give_salary_to_player(self, data: dict) -> None:
        self.salary_id = data.get("salary_id")
        self.player_giver_id = int(data.get("player_id"))
        self.selection_event.set()

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        from app.cards.concrete.professional.study_salary import SalaryCard
        emit("show_birthday_waiting", {"card_id": self.id})
        self.nb_player_to_give = 0

        for player in game.players:
            if player.id != current_player.id and player.connected:
                salaries = [c.to_dict() for c in player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
                if salaries:
                    self.nb_player_to_give += 1
                    emit("select_birthday_gift", {
                        "card_id": self.id,
                        "birthday_player_name": current_player.name,
                        "available_salaries": salaries,
                        "player_id": player.id,
                    }, room=player.session_id)

        while self.nb_player_to_give > 0:
            self.selection_event.wait()
            self.selection_event.clear()
            self.nb_player_to_give -= 1
            giver = game.players[self.player_giver_id]
            from app.cards.concrete.professional.study_salary import SalaryCard as SC
            for card in giver.played["vie professionnelle"]:
                if card.id == self.salary_id:
                    giver.played["vie professionnelle"].remove(card)
                    current_player.add_card_to_played(card)
                    break

        emit("close_birthday_waiting", {"card_id": self.id})
        return True


class ArcEnCielCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("arc en ciel", image_path)
        self.nb_cards_played: int = 0

    def get_card_rule(self) -> str:
        return "Arc-en-Ciel — jouez jusqu'à 3 cartes supplémentaires, puis repiochez."

    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base["count"] = 4 - self.nb_cards_played
        return base

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        game.arcEnCielMode = True
        game.arcEnCielCard = self
        return True

    def add_card_played(self, game: "Game", current_player: "Player") -> None:
        self.nb_cards_played += 1
        if self.nb_cards_played >= 4:
            self.end_arc_en_ciel(game, current_player)

    def end_arc_en_ciel(self, game: "Game", current_player: "Player") -> None:
        game.arcEnCielMode = False
        for _ in range(1, self.nb_cards_played):
            if game.deck:
                current_player.hand.append(game.deck.pop())


class MuguetCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("muguet", image_path)
        self.smiles: int = 1

    def get_card_rule(self) -> str:
        return "Muguet — permet de rejouer ce tour."

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        game.phase = "draw"
        return True
