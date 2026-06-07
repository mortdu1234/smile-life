"""représente un joueur dans la partie"""
from .cards.personnals.Wedding import Adultery, Wedding
from .cards.professionnals.JobCard import JobCard
from .cards.professionnals.SalaryCard import SalaryCard
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
    
    def __init__(self, name: str, id: int):
        self.name = name
        self.id = id
        self.hand = []
        self.power = []
        self.job = None
        self.skip_turn = 0
        self.groupe = {
            PlayedCardGroup.VIE_PROFESSIONNELLE: [],
            PlayedCardGroup.VIE_PERSONNELLE: [],
            PlayedCardGroup.ACQUISITIONS: [],
            PlayedCardGroup.SALAIRES_DEPENSES: [],
            PlayedCardGroup.CARTES_SPECIALES: [],
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
            }
        }
        if reveal_hand:
            base["hand"] = [c.to_dict() for c in self.hand]
        return base

    
    @property
    def groupe_str(self) -> dict:
        return PlayedCardGroup.groupe_to_dict(self.groupe)

    def add_card_to_played(self, card: Card):
        """joue la carte du joueur et l'ajoute dans le groupe correspondant"""
        self.cards[card.get_id()] = card
        self.groupe[PlayedCardGroup.get_card_on_play_group(card)].append(card)

    def find_card_by_id(self, card_id: int) -> Card | None:
        """recherche une carte jouée par son id"""
        return self.cards.get(card_id)

    def remove_card(self, card: Card) -> None:
        """retire une carte des cartes jouées"""
        card_id = card.get_id()
        success = self.cards.pop(card_id, None)
        if not success:
            raise ValueError(f"Card {card.get_id()} not found in player's played cards")
        groups: list[PlayedCardGroup] = PlayedCardGroup.get_card_groups(card)
        for group in groups:
            self.groupe[group].remove(card)

    def remove_card_from_hand(self, card: Card) -> None:
        """retire une carte de la main du joueur"""
        if card in self.hand:
            self.hand.remove(card)
        else:
            raise ValueError(f"Card {card.get_id()} not in player's hand")

    def get_study_level(self) -> int:
        """Retourne le niveau d'étude de joueur"""
        total = 0
        for card in self.groupe.get(PlayedCardGroup.VIE_PROFESSIONNELLE, []):
            if isinstance(card, SalaryCard):
                total += card.get_value()  # pyright: ignore[reportAttributeAccessIssue]
        return total

    def get_id(self) ->int:
        return self.id

    def get_power(self) -> list[Power]:
        return self.power + self.job.get_power() if self.job else []

    def get_job(self) -> JobCard | None:
        return self.job

    def get_available_salary(self) -> list[SalaryCard | Heritage]:
        """renvois la lsite des salaire disponible pour un achat"""
        result = []
        cards = self.get_card_from_group(PlayedCardGroup.VIE_PROFESSIONNELLE)
        for card in cards:
            if isinstance(card, SalaryCard):
                result.append(cards)
        cards = self.get_card_from_group(PlayedCardGroup.CARTES_SPECIALES)
        for card in cards:
            if isinstance(card, Heritage):
                result.append(cards)
        return result

    def is_wedding(self) -> bool:
        """renvois si le joueur est mariée ou non"""
        cards = self.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE)
        for card in cards:
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
        