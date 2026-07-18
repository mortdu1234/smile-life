"""représente un joueur dans la partie"""
from typing import TYPE_CHECKING



if TYPE_CHECKING:
    from backend.core.roles.PlayerRole import PlayerRole
    from ..userIo.interface import UserIO
    from .cards.professionnals.SalaryCard import SalaryCard
    from .cards.professionnals.StudyCard import StudyCard
    from .Game import Game
    from .cards.CardAttributes import CanBeUseOnAcquisition

from .cards.personnals.Wedding import Adultery, Wedding
from .cards.professionnals.JobCard import JobCard
from .cards.personnals.Flirts import Flirt

from .cards.Card import Card, InstantPlayedCard

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
        self.power = []
        self.job = None
        self.skip_turn = 0
        self.interface = interface
        self.groupe = {
            PlayedCardGroup.VIE_PERSONNELLE : [], # flirts, marriage, adultères
            PlayedCardGroup.CHILDREN : [], # enfants
            PlayedCardGroup.ANIMALS : [], # animaux
        
            PlayedCardGroup.VIE_PROFESSIONNELLE : [], # etudes, job
            PlayedCardGroup.SALARIES : [], # salaires non dépensés
            PlayedCardGroup.SALARIES_USED : [], # salaires dépensés
            PlayedCardGroup.ACQUISITIONS : [], # acquisitions
        
            PlayedCardGroup.SPECIAL : [], # cartes spéciales
            PlayedCardGroup.OTHER : [], # autres cartes
            PlayedCardGroup.HARDSHIP : [], # hardship, malefices
        }
        self.cards = {}
        self.role: "PlayerRole|None" = None

    def set_role(self, role: "PlayerRole"):
        self.role = role

    def get_role(self) -> "PlayerRole|None":
        return self.role

    def get_available_salaries(self) -> "list[CanBeUseOnAcquisition]":
        """renvois l'ensemble des cartes utilisables pour acheter une acquisition"""
        from .cards.CardAttributes import CanBeUseOnAcquisition
        # récupération des salaires
        available_salaries: "list[CanBeUseOnAcquisition]" = []
        salaries = self.get_card_from_group(PlayedCardGroup.SALARIES)
        for card in salaries:
            if isinstance(card, CanBeUseOnAcquisition) and not card.is_used:
                available_salaries.append(card)

        # récupération des héritages
        available_speciales: "list[CanBeUseOnAcquisition]" = []
        speciales = self.get_card_from_group(PlayedCardGroup.SPECIAL)
        for card in speciales:
            if isinstance(card, CanBeUseOnAcquisition) and not card.is_used:
                available_speciales.append(card)

        # récupération des Amulettes
        available_acquisitions: "list[CanBeUseOnAcquisition]" = []
        acquisitions = self.get_card_from_group(PlayedCardGroup.ACQUISITIONS)
        for card in acquisitions:
            if isinstance(card, CanBeUseOnAcquisition) and not card.is_used:
                available_acquisitions.append(card)

        return available_salaries + available_speciales + available_acquisitions
                 



    def to_dict(self, reveal_hand: bool = False) -> dict:
        base ={
            'name': self.name,
            'hand_count': len(self.hand),
            'cards': {str(k): v.to_dict() for k, v in self.cards.items()},
            'groupe': {
                group.value: [c.to_dict() for c in cards]
                for group, cards in self.groupe.items()
            }, 
            "skip_turn": self.skip_turn, 
            "smiles": self.get_smiles(),
        }
        role = self.get_role()
        if role:
            base["role"] = role.to_dict()
        if reveal_hand:
            base["hand"] = [c.to_dict() for c in self.hand]
        return base

    def get_group(self, card: "Card") -> "PlayedCardGroup|None":
        for groupe in self.groupe:
            if card in self.groupe[groupe]:
                return groupe
        return None

    def get_smiles(self) -> int:
        """retourne le nombre de smiles"""
        score = 0
        for id, card in self.cards.items():
            score += card.get_smiles(self)
        return score
    
    def get_max_hand_card(self):
        maxCard = 5 # valeur par défaut
        for power in self.get_power():
            if power == Power.ADD_1_HAND_CARD:
                maxCard += 1
            if power == Power.SUB_1_HAND_CARD:
                maxCard -= 1
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

        from .cards.personnals.Flirts import Flirt
        if isinstance(card, Flirt) and self.get_adultery():
            card.count = False

        from .cards.professionnals.StudyCard import StudyCard
        if isinstance(card, StudyCard) and Power.INFINITE_STUDY in self.get_power():
            card.count = False
                    
        self.groupe[PlayedCardGroup.get_card_on_play_group(card)].append(card)


    def find_card_by_id(self, card_id: int) -> Card | None:
        """recherche une carte jouée par son id"""
        return self.cards.get(card_id)

    def remove_card(self, card: Card, game: "Game") -> None:
        """retire une carte des cartes jouées"""
        card_id = card.get_id()
        success = self.cards.pop(card_id, None)
        if not success:
            raise ValueError(f"Card {card.get_id()} not found in player ({self.name}) played cards")
        groups: list[PlayedCardGroup] = PlayedCardGroup.get_card_groups(card)
        for group in groups:
            try:
                card.discard_card(game, self)
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
            print(f"[INFO] déplacement de la carte {card.get_name()} du groupe {groupFrom} vers {groupTo}")
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
        double_study: bool = Power.DOUBLE_STUDY in self.get_power()
        from .cards.professionnals.StudyCard import StudyCard
        for card in self.get_card_from_group(PlayedCardGroup.VIE_PROFESSIONNELLE):
            if isinstance(card, StudyCard):
                total += card.get_value() * (1+double_study)
        return total


    def get_id(self) ->int:
        return self.id

    def get_power(self) -> list[Power]:
        powers = self.power.copy()
        if self.get_adultery() is not None:
            powers += [Power.CAN_FLIRT_WITH_WEDDING]
        if self.job:
            powers += self.job.get_power(self).copy()
        if self.role is not None:
            powers += self.role.get_power().copy()
        return powers
    
    def add_power(self, power: Power):
        """ajoute un pouvoir dans la liste"""
        if power not in self.power:
            self.power.append(power)

    def get_job(self) -> JobCard | None:
        return self.job
    
    def is_wedding(self) -> bool:
        """renvois si le joueur est mariée ou non"""
        cards = self.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE)
        for card in cards:
            from .cards.personnals.Wedding import Wedding
            if isinstance(card, Wedding):
                return True
        return False
    
    def remove_player_power(self, power: Power):
        """retire un pouvoir dans la liste du joueur (sans le métier)"""
        try:
            self.power.remove(power)
        except ValueError:        
            print("[ERROR] Le pouvoir demander est nul part")

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
        return self.groupe.get(group1, []).copy()

    def add_card_to_hand(self, card: Card) -> bool:
        """ajoute une nouvelle carte a la main et vérifie si c'est une carte qui dois etre jouée directement"""
        self.hand.append(card)
        if isinstance(card, InstantPlayedCard):
            return False
        return True

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
        for card in self.get_card_from_group(PlayedCardGroup.SALARIES):
            from .cards.professionnals.SalaryCard import SalaryCard 
            if isinstance(card, SalaryCard) and not card.is_protected:
                last_salary = card
        return last_salary

    def get_last_study_placed(self) -> "StudyCard | None":
        """retourne la dernière carte étude posé"""
        last_study = None
        for card in self.get_card_from_group(PlayedCardGroup.VIE_PROFESSIONNELLE):
            from .cards.professionnals.StudyCard import StudyCard
            if isinstance(card, StudyCard) and not card.is_protected:
                last_study = card
        return last_study

    def get_hand(self) -> list["Card"]:
        return self.hand.copy()

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