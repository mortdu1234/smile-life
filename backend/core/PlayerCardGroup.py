from enum import Enum

from .cards.Card import Card


class PlayedCardGroup(Enum):
    """Enum pour les différents groupes de cartes jouées devant un joueur"""
    VIE_PERSONNELLE = "vie_personnelle" # flirts, marriage, adultères
    CHILDREN = "children" # enfants
    ANIMALS = "animals" # animaux

    VIE_PROFESSIONNELLE = "vie_professionnelle" # etudes, job
    SALARIES = "salaries" # salaires non dépensés
    SALARIES_USED = "salaries_used" # salaires dépensés
    ACQUISITIONS = "acquisitions" # acquisitions

    SPECIAL = "special" # cartes spéciales
    OTHER = "other" # autres cartes
    HARDSHIP = "hardship" # hardship, malefices

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

        if isinstance(card, (Flirt, Wedding, Adultery)):
            return PlayedCardGroup.VIE_PERSONNELLE
        if isinstance(card, ChildCard):
            return PlayedCardGroup.CHILDREN
        if isinstance(card, AnimalCard):
            return PlayedCardGroup.ANIMALS
        if isinstance(card, (StudyCard, JobCard)):
            return PlayedCardGroup.VIE_PROFESSIONNELLE
        if isinstance(card, SalaryCard):
            return PlayedCardGroup.SALARIES
        if isinstance(card, Acquisition):
            return PlayedCardGroup.ACQUISITIONS
        if isinstance(card,  (SpecialCard)):
            return PlayedCardGroup.SPECIAL
        if isinstance(card, OtherCard):
            return PlayedCardGroup.OTHER
        if isinstance(card, Hardship):
            return PlayedCardGroup.HARDSHIP
        print(f"[WARNING] la carte {card.__class__.__name__} n'est pas bien rangée")
        return PlayedCardGroup.OTHER
        
    
    @staticmethod
    def get_card_groups(card: Card) -> list['PlayedCardGroup']:
        """Retourne la liste des groupes de cartes auxquels appartient la carte donnée"""
        from .cards.professionnals.SalaryCard import SalaryCard
        if isinstance(card, SalaryCard):
            return [PlayedCardGroup.get_card_on_play_group(card), PlayedCardGroup.SALARIES_USED]
        return [PlayedCardGroup.get_card_on_play_group(card)]
    
    @staticmethod
    def groupe_to_dict(groupe: dict) -> dict:
        """Convertit un dict {PlayedCardGroup: [Card]} en {str: [Card]} pour Jinja2."""
        return {group.value: cards for group, cards in groupe.items()}