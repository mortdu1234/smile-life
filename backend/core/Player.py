"""représente un joueur dans la partie"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..userIo.interface import UserIO
    from .cards.professionnals.SalaryCard import SalaryCard
    from .cards.professionnals.StudyCard import StudyCard
from ..userIo.web import WebIO
from .cards.personnals.Wedding import Adultery, Wedding
from .cards.professionnals.JobCard import JobCard
from .cards.personnals.Flirts import Flirt
from .cards.specials.Heritage import Heritage

from .cards.Card import Card

from .Power import Power
from .PlayerCardGroup import PlayedCardGroup


class Player:
    name: str # Pseudo du joueur
    id: int
    hand: list[Card] # Cartes en main du joueur
    power: list[Power]
    job: JobCard | None
    skip_turn: int
    # cartes jouées devant lui
    groupe: dict[PlayedCardGroup, list[Card]] # Toutes les cartes posés du joueurs rangées par groupe
    cards: dict[int, Card] # Toutes les cartes posées du joueurs
    interface: "UserIO"
    
    def __init__(self, name: str, id: int, interface: "UserIO"):
        self.name = name
        self.id = id
        self.hand = []
        self.power = [Power.MAX_HAND_CARD_5]
        self.job = None
        self.skip_turn = 0
        self.interface = interface
        self.groupe = {
            PlayedCardGroup.VIE_PROFESSIONNELLE: [],
            PlayedCardGroup.VIE_PERSONNELLE: [],
            PlayedCardGroup.ACQUISITIONS: [],
            PlayedCardGroup.CARTES_PROTEGEES: [],
            PlayedCardGroup.CARTES_SPECIALES: [],
            PlayedCardGroup.HARDSHIP: []
        }
        self.cards = {}

    def to_dict(self, reveal_hand: bool = False) -> dict:
        base ={
            'name': self.name,
            'hand_count': len(self.hand),
            'cards': {str(k): v.to_dict() for k, v in self.cards.items()},
            'groupe': {
                group.value: [c.to_dict() for c in cards]
                for group, cards in self.groupe.items()
            }, 
            "skip_turn": self.skip_turn
        }
        if reveal_hand:
            base["hand"] = [c.to_dict() for c in self.hand]
        return base

    def get_max_hand_card(self):
        maxCard = 0
        for power in self.get_power():
            if power.value.startswith("max_hand_card_"): 
                value = int(power.value.split("_")[-1])  
                maxCard = max(maxCard, value)
        return maxCard
    
    @property
    def groupe_str(self) -> dict:
        return PlayedCardGroup.groupe_to_dict(self.groupe)

    def get_interface(self) -> "UserIO":
        return self.interface

    def add_card_to_played(self, card: Card):
        """joue la carte du joueur et l'ajoute dans le groupe correspondant"""
        self.cards[card.get_id()] = card

        # ====================
        # Selection du groupe
        # ====================
        from .cards.professionnals.JobCard import JobCard
        if isinstance(card, JobCard):
            self.job = card
            self.groupe[PlayedCardGroup.get_card_on_play_group(card)].append(card)
            return

        from .cards.personnals.Flirts import Flirt
        if isinstance(card, Flirt):
            is_adultery = self.get_adultery()
            if is_adultery:
                self.groupe[PlayedCardGroup.CARTES_PROTEGEES].append(card)
            else:
                self.groupe[PlayedCardGroup.VIE_PERSONNELLE].append(card)
            return
    
        self.groupe[PlayedCardGroup.get_card_on_play_group(card)].append(card)

    def find_card_by_id(self, card_id: int) -> Card | None:
        """recherche une carte jouée par son id"""
        return self.cards.get(card_id)

    def remove_card(self, card: Card) -> None:
        """retire une carte des cartes jouées"""
        card_id = card.get_id()
        success = self.cards.pop(card_id, None)
        if not success:
            raise ValueError(f"Card {card.get_id()} not found in player ({self.name}) played cards")
        groups: list[PlayedCardGroup] = PlayedCardGroup.get_card_groups(card)
        for group in groups:
            try:
                self.groupe[group].remove(card)
            except ValueError:
                print(f"Erreur, player:{self.name} \nretirer carte:{card.id} de type {card.__class__}\ngroupe:{group} contient : {[carte.__class__ for carte in self.groupe[group]]}")
        if isinstance(card, JobCard):
            self.job = None

    def move_placed_cards(self,card: Card, groupFrom: PlayedCardGroup, groupTo: PlayedCardGroup) -> bool:
        """déplace une carte et la change de groupe"""
        try:
            self.groupe[groupFrom].remove(card)
            self.groupe[groupTo].append(card)
            return True
        except ValueError:
            return False
        
    def remove_card_from_hand(self, card: Card) -> None:
        """retire une carte de la main du joueur"""
        if card in self.hand:
            self.hand.remove(card)
        else:
            raise ValueError(f"Card {card.get_id()} not in player's hand")

    def get_study_level(self) -> int:
        """Retourne le niveau d'étude de joueur"""
        total = 0

        from .cards.professionnals.StudyCard import StudyCard
        for card in self.groupe.get(PlayedCardGroup.VIE_PROFESSIONNELLE, []):

            if isinstance(card, StudyCard):
                total += card.get_value()  # pyright: ignore[reportAttributeAccessIssue]
        return total

    def get_id(self) ->int:
        return self.id

    def get_power(self) -> list[Power]:
        if self.job:
            print(f"[DEBUG] get_power() : perso + job : {self.power + self.job.get_power()}")
            return self.power + self.job.get_power()
        print(f"[DEBUG] get_power() : perso : {self.power}")
        return self.power

    def get_job(self) -> JobCard | None:
        return self.job

    def get_available_salary(self) -> "list[SalaryCard | Heritage]":
        """renvois la lsite des salaire disponible pour un achat"""
        result = []
        cards = self.get_card_from_group(PlayedCardGroup.VIE_PROFESSIONNELLE)
        for card in cards:
            from .cards.professionnals.SalaryCard import SalaryCard
            if isinstance(card, SalaryCard):
                result.append(card)
        cards = self.get_card_from_group(PlayedCardGroup.CARTES_SPECIALES)
        for card in cards:
            if isinstance(card, Heritage):
                result.append(card)
        return result

    def is_wedding(self) -> bool:
        """renvois si le joueur est mariée ou non"""
        cards = self.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE)
        for card in cards:
            from .cards.personnals.Wedding import Wedding
            if isinstance(card, Wedding):
                return True
        return False

    def remove_power(self, power: Power):
        """retire un pouvoir dans la liste"""
        try:
            self.power.remove(power)
        except ValueError:
            if self.job:
                try:
                    self.job.jobPower.remove(power)
                except ValueError:
                    print("[ERROR] Le pouvoir demander est nul part")

    def get_last_flirt(self) -> Flirt | None:
        """retourne le dernier flirt posé"""
        cards = self.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE)
        for card in cards[::-1]:
            if isinstance(card, Flirt):
                return card
        return None

    def is_adultery(self) -> bool:
        """revois si le joueur est en adultaire ou non"""
        cards = self.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE)
        for card in cards:
            if isinstance(card, Adultery):
                return True
        return False

    def get_card_from_group(self, group1: PlayedCardGroup) -> list[Card]:
        return self.groupe.get(group1, [])

    def add_card_to_hand(self, card: Card):
        """ajoute une nouvelle carte a la main"""
        self.hand.append(card)

    def get_card_by_id_from_hand(self, card_id: int) -> Card | None:
        """retourne une carte de la main a partir de son ID"""
        for card in self.hand:
            if card.get_id() == card_id:
                return card
        return None

    def add_skip_turn(self, number: int):
        self.skip_turn += number


    # -------------------------------------
    # GETTERS
    # -------------------------------------
    def get_last_salary_placed(self) -> "SalaryCard | None":
        """Retourne le dernier salaire posé et non utilisé par un joueur"""
        last_salary = None
        for card in self.get_card_from_group(PlayedCardGroup.VIE_PROFESSIONNELLE):
            from .cards.professionnals.SalaryCard import SalaryCard 
            if isinstance(card, SalaryCard):
                last_salary = card
        return last_salary

    def get_last_study_placed(self) -> "StudyCard | None":
        """retourne la dernière carte étude posé"""
        last_study = None
        for card in self.get_card_from_group(PlayedCardGroup.VIE_PROFESSIONNELLE):
            from .cards.professionnals.StudyCard import StudyCard
            if isinstance(card, StudyCard):
                last_study = card
        return last_study

    def get_hand(self) -> list["Card"]:
        return self.hand

    def get_wedding(self) -> "Wedding | None":
        """retourne le marriage posé"""
        wedding_card = None
        for card in self.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE):
            if isinstance(card, Wedding):
                wedding_card = card
        return wedding_card
    
    def get_adultery(self) -> "Adultery | None":
        """retourne le marriage posé"""
        adultery_card = None
        for card in self.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE):
            if isinstance(card, Adultery):
                adultery_card = card
        return adultery_card