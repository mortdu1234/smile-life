from enum import Enum

from numpy import isin
from .cards.Card import Card


class PlayedCardGroup(Enum):
    """Enum pour les différents groupes de cartes jouées devant un joueur"""
    VIE_PROFESSIONNELLE = 'vie_professionnelle'
    VIE_PERSONNELLE = 'vie_personnelle'
    ACQUISITIONS = 'acquisitions'
    CARTES_PROTEGEES = 'cartes_protegees'
    CARTES_SPECIALES = 'cartes_speciales'
    HARDSHIP ="hardship"

    @staticmethod
    def get_card_on_play_group(card: Card) -> 'PlayedCardGroup':
        """Retourne le groupe de cartes auquel appartient la carte donnée"""
        from .cards.animals.AnimalCard import AnimalCard
        from .cards.acquisitions.Acquisition import Acquisition
        from .cards.other.OtherCard import OtherCard
        from .cards.specials.SpecialCard import SpecialCard
        from .cards.personnals.Children import ChildCard
        from .cards.personnals.Flirts import Flirt
        from .cards.personnals.Wedding import Wedding, Adultery
        from .cards.professionnals.JobCard import JobCard
        from .cards.professionnals.SalaryCard import SalaryCard
        from .cards.professionnals.StudyCard import StudyCard
        from .cards.hardships.HardshipCard import Hardship

        if isinstance(card, (Flirt, Wedding, Adultery, ChildCard, AnimalCard)):
            return PlayedCardGroup.VIE_PERSONNELLE
        if isinstance(card, (StudyCard, SalaryCard, JobCard)):
            return PlayedCardGroup.VIE_PROFESSIONNELLE
        if isinstance(card, Acquisition):
            return PlayedCardGroup.ACQUISITIONS
        if isinstance(card,  (SpecialCard, OtherCard)):
            return PlayedCardGroup.CARTES_SPECIALES
        if isinstance(card, Hardship):
            return PlayedCardGroup.HARDSHIP
        print(f"[WARNING] la carte {card.__class__.__name__} n'est pas bien rangée")
        return PlayedCardGroup.CARTES_SPECIALES
        
    
    @staticmethod
    def get_card_groups(card: Card) -> list['PlayedCardGroup']:
        """Retourne la liste des groupes de cartes auxquels appartient la carte donnée"""
        from .cards.animals.AnimalCard import AnimalCard
        from .cards.acquisitions.Acquisition import Acquisition
        from .cards.other.OtherCard import OtherCard
        from .cards.specials.SpecialCard import SpecialCard
        from .cards.personnals.Children import ChildCard
        from .cards.personnals.Flirts import Flirt
        from .cards.personnals.Wedding import Wedding, Adultery
        from .cards.professionnals.JobCard import JobCard
        from .cards.professionnals.SalaryCard import SalaryCard
        from .cards.professionnals.StudyCard import StudyCard
        from .cards.hardships.HardshipCard import Hardship
        result = []
        if isinstance(card, (Flirt, Wedding, Adultery, ChildCard, AnimalCard)):
            result.append(PlayedCardGroup.VIE_PERSONNELLE)
        if isinstance(card, (StudyCard, SalaryCard, JobCard)):
            result.append(PlayedCardGroup.VIE_PROFESSIONNELLE)
        if isinstance(card, Acquisition):
            result.append(PlayedCardGroup.ACQUISITIONS)
        if isinstance(card,  (SpecialCard, OtherCard)):
            result.append(PlayedCardGroup.CARTES_SPECIALES)
        if isinstance(card, Hardship):
            result.append(PlayedCardGroup.HARDSHIP)
        return result
    @staticmethod
    def groupe_to_dict(groupe: dict) -> dict:
        """Convertit un dict {PlayedCardGroup: [Card]} en {str: [Card]} pour Jinja2."""
        return {group.value: cards for group, cards in groupe.items()}