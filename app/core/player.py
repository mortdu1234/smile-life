"""
Classe Player — logique pure, aucun import Flask.
"""
from typing import TYPE_CHECKING, Dict, Any, List

if TYPE_CHECKING:
    from app.cards.base.card import Card
    from app.cards.base.hardship_card import HardshipCard


class Player:
    """Représente un joueur dans la partie."""

    def __init__(self, player_id: int, name: str):
        self.id: int = player_id
        self.name: str = name
        self.hand: List["Card"] = []
        self.played: Dict[str, List["Card"]] = {
            "vie professionnelle": [],  # études, métier, salaires
            "vie personnelle": [],      # flirts, mariage, adultère, enfants, animaux
            "acquisitions": [],         # maisons, voyages
            "salaire dépensé": [],      # salaires utilisés pour investir
            "cartes spéciales": [],     # cartes spéciales, légion, prix…
            "effet permanent": [],      # effets permanents (coups durs, clichés…)
        }
        self.skip_turns: int = 0
        self.has_been_bandit: bool = False
        self.heritage: int = 0
        self.received_hardships: List["HardshipCard"] = []
        self.connected: bool = True
        self.session_id: str | None = None

    # ------------------------------------------------------------------ #
    #  Ajout/retrait de cartes                                             #
    # ------------------------------------------------------------------ #

    def add_card_to_played(self, card: "Card") -> None:
        """Ajoute la carte dans la bonne catégorie."""
        from app.cards.concrete.professional.study_salary import StudyCard, SalaryCard
        from app.cards.concrete.professional.job import JobCard
        from app.cards.concrete.personal.flirt import FlirtCard, MarriageCard, AdulteryCard
        from app.cards.concrete.personal.children import ChildCard
        from app.cards.concrete.animals.cards import AnimalCard
        from app.cards.concrete.acquisitions.cards import AquisitionCard
        from app.cards.base.special_card import SpecialCard
        from app.cards.base.permanent_effect import PermanentEffet
        from app.cards.concrete.other.cards import OtherCard

        if isinstance(card, (StudyCard, SalaryCard, JobCard)):
            self.played["vie professionnelle"].append(card)
        elif isinstance(card, (FlirtCard, MarriageCard, AdulteryCard, ChildCard, AnimalCard)):
            self.played["vie personnelle"].append(card)
        elif isinstance(card, AquisitionCard):
            self.played["acquisitions"].append(card)
        elif isinstance(card, PermanentEffet):
            self.played["effet permanent"].append(card)
        elif isinstance(card, (SpecialCard, OtherCard)):
            self.played["cartes spéciales"].append(card)
        else:
            self.played["cartes spéciales"].append(card)

    def remove_card_from_played(self, card: "Card") -> None:
        for category in self.played.values():
            if card in category:
                category.remove(card)
                return

    def add_card_to_hand(self, card: "Card") -> None:
        self.hand.append(card)

    def remove_card_from_hand(self, card: "Card") -> None:
        if card in self.hand:
            self.hand.remove(card)

    def add_card_to_vie_perso(self, card: "Card") -> None:
        self.played["vie personnelle"].append(card)

    def add_card_to_salaire_depense(self, card: "Card") -> None:
        self.played["salaire dépensé"].append(card)

    def add_card_to_effet_permanent(self, card: "Card") -> None:
        self.played["effet permanent"].append(card)

    # ------------------------------------------------------------------ #
    #  Accesseurs par catégorie                                            #
    # ------------------------------------------------------------------ #

    def get_all_played_cards(self) -> List["Card"]:
        cards = []
        for cat in self.played.values():
            cards.extend(cat)
        return cards

    def get_played_vie_pro(self) -> List["Card"]:
        return self.played["vie professionnelle"]

    def get_played_vie_perso(self) -> List["Card"]:
        return self.played["vie personnelle"]

    def get_played_acquisitions(self) -> List["Card"]:
        return self.played["acquisitions"]

    def get_played_carte_speciale(self) -> List["Card"]:
        return self.played["cartes spéciales"]

    def get_played_effet_permanent(self) -> List["Card"]:
        return self.played["effet permanent"]

    def get_played_carte_speciale_by_id(self, card_id: str) -> "Card | None":
        return next((c for c in self.played["cartes spéciales"] if c.id == card_id), None)

    def get_played_effet_permanent_by_id(self, card_id: str) -> "Card | None":
        return next((c for c in self.played["effet permanent"] if c.id == card_id), None)

    def get_played_card_by_id(self, card_id: str) -> "Card | None":
        return next((c for c in self.get_all_played_cards() if c.id == card_id), None)

    # ------------------------------------------------------------------ #
    #  Requêtes sur l'état du joueur                                      #
    # ------------------------------------------------------------------ #

    def has_job(self) -> bool:
        from app.cards.concrete.professional.job import JobCard
        return any(isinstance(c, JobCard) for c in self.played["vie professionnelle"])

    def get_job(self) -> List["Card"]:
        from app.cards.concrete.professional.job import JobCard
        return [c for c in self.played["vie professionnelle"] if isinstance(c, JobCard)]

    def is_married(self) -> bool:
        from app.cards.concrete.personal.flirt import MarriageCard
        return any(isinstance(c, MarriageCard) for c in self.played["vie personnelle"])

    def has_adultery(self) -> bool:
        from app.cards.concrete.personal.flirt import AdulteryCard
        return any(isinstance(c, AdulteryCard) for c in self.played["vie personnelle"])

    def has_any_flirt(self) -> bool:
        from app.cards.concrete.personal.flirt import FlirtCard
        all_flirts = [c for c in self.played["vie personnelle"] if isinstance(c, FlirtCard)]
        all_flirts += [c for c in self.played["cartes spéciales"] if isinstance(c, FlirtCard)]
        return len(all_flirts) > 0

    def has_flirt_at_location(self, location: str) -> bool:
        from app.cards.concrete.personal.flirt import FlirtCard
        all_flirts = [c for c in self.played["vie personnelle"] if isinstance(c, FlirtCard)]
        all_flirts += [c for c in self.played["cartes spéciales"] if isinstance(c, FlirtCard)]
        return any(f.location == location for f in all_flirts)

    def get_last_flirt(self) -> "Card | None":
        from app.cards.concrete.personal.flirt import FlirtCard, MarriageCard
        cards = self.played["vie personnelle"]
        for card in reversed(cards):
            if isinstance(card, MarriageCard):
                return None
            if isinstance(card, FlirtCard):
                return card
        return None

    def get_marriage(self) -> "Card | None":
        from app.cards.concrete.personal.flirt import MarriageCard
        return next(
            (c for c in self.played["vie personnelle"] if isinstance(c, MarriageCard)),
            None,
        )

    def count_studies(self) -> int:
        from app.cards.concrete.professional.study_salary import StudyCard
        return sum(
            c.levels for c in self.played["vie professionnelle"]
            if isinstance(c, StudyCard)
        )

    def count_salaries(self) -> int:
        from app.cards.concrete.professional.study_salary import SalaryCard
        return sum(
            1 for c in self.played["vie professionnelle"]
            if isinstance(c, SalaryCard)
        )

    def get_available_salary_sum(self) -> int:
        from app.cards.concrete.professional.study_salary import SalaryCard
        return sum(
            c.level for c in self.played["vie professionnelle"]
            if isinstance(c, SalaryCard)
        )

    # ------------------------------------------------------------------ #
    #  Pouvoirs agrégés                                                   #
    # ------------------------------------------------------------------ #

    def get_power(self) -> List[str]:
        """Retourne tous les tokens de pouvoir actifs (cartes posées + métiers)."""
        powers: List[str] = []
        from app.cards.base.permanent_effect import PermanentEffet
        from app.cards.concrete.professional.job import JobCard
        for card in self.get_all_played_cards():
            if isinstance(card, (PermanentEffet, JobCard)):
                if hasattr(card, "get_power"):
                    powers.extend(card.get_power())
        return powers

    # ------------------------------------------------------------------ #
    #  Calcul des smiles                                                   #
    # ------------------------------------------------------------------ #

    def calculate_smiles(self) -> int:
        total = sum(c.smiles for c in self.get_all_played_cards())

        all_cards = self.get_all_played_cards()

        from app.cards.concrete.animals.cards import LicorneAnimal
        from app.cards.concrete.special.cards import ArcEnCielCard, EtoileFilanteCard
        has_licorne = any(isinstance(c, LicorneAnimal) for c in all_cards)
        has_arc = any(isinstance(c, ArcEnCielCard) for c in all_cards)
        has_etoile = any(isinstance(c, EtoileFilanteCard) for c in all_cards)
        if has_licorne and has_arc and has_etoile:
            total += 3

        from app.cards.concrete.hardship.cards import GynocratieHardship, PhalocratieHardship
        from app.cards.concrete.personal.children import FemaleChild, MaleChild
        if any(isinstance(c, GynocratieHardship) for c in all_cards):
            total -= sum(1 for c in all_cards if isinstance(c, FemaleChild))
        if any(isinstance(c, PhalocratieHardship) for c in all_cards):
            total -= sum(1 for c in all_cards if isinstance(c, MaleChild))

        return total

    # ------------------------------------------------------------------ #
    #  Sérialisation                                                       #
    # ------------------------------------------------------------------ #

    def to_dict(self, hide_hand: bool = False) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "hand": [] if hide_hand else [c.to_dict() for c in self.hand],
            "hand_count": len(self.hand),
            "played": {
                category: [c.to_dict() for c in cards]
                for category, cards in self.played.items()
            },
            "skip_turns": self.skip_turns,
            "has_been_bandit": self.has_been_bandit,
            "heritage": self.heritage,
            "received_hardships": [
                c.to_dict().get("subtype", "malus") if hasattr(c, "to_dict") else str(c)
                for c in self.received_hardships
            ],
            "connected": self.connected,
        }
