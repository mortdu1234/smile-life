import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Card(ABC):
    """Classe de base pour toutes les cartes"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.smiles = 0
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la carte en dictionnaire pour la sérialisation"""
        return {
            'id': self.id,
            'smiles': self.smiles,
            'type': self.__class__.__name__.lower()
        }
    
    @abstractmethod
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        """Vérifie si la carte peut être jouée par le joueur"""
        return True, ""

class JobCard(Card):
    """Carte métier"""
    def __init__(self, job_name: str, salary: int, studies: int, status: str, power: str):
        super().__init__()
        self.job_name = job_name
        self.salary = salary
        self.studies = studies
        self.status = status
        self.power = power
        self.smiles = 2
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'job',
            'subtype': self.job_name,
            'salary': self.salary,
            'studies': self.studies,
            'status': self.status,
            'power': self.power
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        # Vérifier si le joueur a déjà un métier
        if player.has_job():
            return False, "Vous avez déjà un métier"
        
        # Vérifier si le joueur a les études nécessaires
        if self.studies == 'P':
            # Grand prof nécessite d'être prof
            if not player.has_teacher_job():
                return False, "Vous devez être professeur pour devenir grand prof"
        elif isinstance(self.studies, int) and self.studies > 0:
            if player.count_studies() < self.studies:
                return False, f"Vous avez besoin de {self.studies} études"
        
        return True, ""

class StudyCard(Card):
    """Carte étude"""
    def __init__(self, study_type: str, levels: int):
        super().__init__()
        self.study_type = study_type
        self.levels = levels
        self.smiles = 1
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'study',
            'subtype': self.study_type,
            'levels': self.levels
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        # Les études ne peuvent être jouées que si on n'a pas encore de métier
        if player.has_job():
            return False, "Vous ne pouvez plus faire d'études après avoir trouvé un métier"
        return True, ""

class SalaryCard(Card):
    """Carte salaire"""
    def __init__(self, level: int):
        super().__init__()
        self.level = level
        self.smiles = level
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'salary',
            'subtype': self.level
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        job = player.get_job()
        if not job:
            return False, "Vous devez avoir un métier pour recevoir un salaire"
        
        if self.level > job.salary:
            return False, f"Votre salaire maximum est de {job.salary}"
        
        return True, ""

class FlirtCard(Card):
    """Carte flirt"""
    def __init__(self, location: str):
        super().__init__()
        self.location = location
        self.smiles = 1
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'flirt',
            'subtype': self.location
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        if player.is_married():
            return False, "Vous êtes marié(e)"
        return True, ""

class MarriageCard(Card):
    """Carte mariage"""
    def __init__(self, location: str):
        super().__init__()
        self.location = location
        self.smiles = 3
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'marriage',
            'subtype': self.location
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        if player.is_married():
            return False, "Vous êtes déjà marié(e)"
        
        if not player.has_flirt_at_location(self.location):
            return False, f"Vous devez avoir un flirt à {self.location}"
        
        return True, ""

class AdulteryCard(Card):
    """Carte adultère"""
    def __init__(self):
        super().__init__()
        self.smiles = 1
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base['type'] = 'adultere'
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        if not player.is_married():
            return False, "Vous devez être marié(e) pour commettre un adultère"
        return True, ""

class ChildCard(Card):
    """Carte enfant"""
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.smiles = 2
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'child',
            'subtype': self.name
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        if not player.is_married():
            return False, "Vous devez être marié(e) pour avoir un enfant"
        return True, ""

class AnimalCard(Card):
    """Carte animal"""
    def __init__(self, animal_name: str, smiles: int):
        super().__init__()
        self.animal_name = animal_name
        self.smiles = smiles
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'animal',
            'subtype': self.animal_name
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        return True, ""

class HouseCard(Card):
    """Carte maison"""
    def __init__(self, house_type: str, cost: int, smiles: int):
        super().__init__()
        self.house_type = house_type
        self.cost = cost
        self.smiles = smiles
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'house',
            'subtype': self.house_type,
            'cost': self.cost
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        job = player.get_job()
        if job and job.power == 'house_free':
            return True, ""
        
        if player.count_salaries() < self.cost:
            return False, f"Vous avez besoin de {self.cost} salaires"
        
        return True, ""

class TravelCard(Card):
    """Carte voyage"""
    def __init__(self):
        super().__init__()
        self.cost = 3
        self.smiles = 1
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'travel',
            'cost': self.cost
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        job = player.get_job()
        if job and job.power == 'travel_free':
            return True, ""
        
        if player.count_salaries() < self.cost:
            return False, f"Vous avez besoin de {self.cost} salaires"
        
        return True, ""

class SpecialCard(Card):
    """Carte spéciale"""
    def __init__(self, special_type: str):
        super().__init__()
        self.special_type = special_type
        self.smiles = 0
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'special',
            'subtype': self.special_type
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        # Logique spécifique selon le type
        return True, ""

class HardshipCard(Card):
    """Carte coup dur"""
    def __init__(self, hardship_type: str):
        super().__init__()
        self.hardship_type = hardship_type
        self.smiles = 0
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'hardship',
            'subtype': self.hardship_type
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        # Les coups durs sont joués sur d'autres joueurs
        return False, "Les coups durs doivent être joués sur un autre joueur"

class OtherCard(Card):
    """Autres cartes (légion d'honneur, prix)"""
    def __init__(self, card_type: str, smiles: int):
        super().__init__()
        self.card_type = card_type
        self.smiles = smiles
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'other',
            'subtype': self.card_type
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        if self.card_type == 'prix':
            job = player.get_job()
            if not job:
                return False, "Vous devez avoir un métier"
            if job.power not in ['prix_possible', 'see_hands_prix_possible']:
                return False, "Votre métier ne permet pas de recevoir un prix"
        
        return True, ""

class Player:
    """Classe représentant un joueur"""
    def __init__(self, player_id: int, name: str):
        self.id = player_id
        self.name = name
        self.hand: List[Card] = []
        self.played: List[Card] = []
        self.skip_turns = 0
        self.has_been_bandit = False
        self.heritage = 0
        self.received_hardships = []
        self.connected = True
        self.session_id = None
    
    def has_job(self) -> bool:
        return any(isinstance(card, JobCard) for card in self.played)
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        if player.is_married():
            return False, "Vous êtes déjà marié(e)"
        
        if not player.has_any_flirt():
            return False, "Vous devez avoir un flirt pour vous marier"
        
        return True, ""

    def get_job(self) -> JobCard:
        for card in self.played:
            if isinstance(card, JobCard):
                return card
        return None
    
    def has_teacher_job(self) -> bool:
        job = self.get_job()
        return job and job.job_name.startswith('prof')
    
    def count_studies(self) -> int:
        total = 0
        for card in self.played:
            if isinstance(card, StudyCard):
                total += card.levels
        return total
    
    def count_salaries(self) -> int:
        return sum(1 for card in self.played if isinstance(card, SalaryCard))
    
    def is_married(self) -> bool:
        return any(isinstance(card, MarriageCard) for card in self.played)
    
    def has_flirt_at_location(self, location: str) -> bool:
        return any(isinstance(card, FlirtCard) and card.location == location 
                   for card in self.played)
    
    def calculate_smiles(self) -> int:
        total = sum(card.smiles for card in self.played)
        
        # Bonus licorne + arc-en-ciel + étoile filante
        has_licorne = any(isinstance(c, AnimalCard) and c.animal_name == 'licorne' 
                         for c in self.played)
        has_arc = any(isinstance(c, SpecialCard) and c.special_type == 'arc en ciel' 
                     for c in self.played)
        has_etoile = any(isinstance(c, SpecialCard) and c.special_type == 'etoile filante' 
                        for c in self.played)
        
        if has_licorne and has_arc and has_etoile:
            total += 3
        
        return total
    
    def to_dict(self, hide_hand: bool = False) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'hand': [] if hide_hand else [card.to_dict() for card in self.hand],
            'hand_count': len(self.hand),
            'played': [card.to_dict() for card in self.played],
            'skip_turns': self.skip_turns,
            'has_been_bandit': self.has_been_bandit,
            'heritage': self.heritage,
            'received_hardships': self.received_hardships,
            'connected': self.connected
        }

class CardFactory:
    """Factory pour créer les cartes"""
    
    JOBS = {
        'architecte': {'salary': 3, 'studies': 4, 'status': 'rien', 'power': 'house_free'},
        'astronaute': {'salary': 4, 'studies': 6, 'status': 'rien', 'power': 'discard_pick'},
        'avocat': {'salary': 3, 'studies': 4, 'status': 'rien', 'power': 'no_divorce'},
        'bandit': {'salary': 4, 'studies': 0, 'status': 'rien', 'power': 'no_fire_tax'},
        'barman': {'salary': 1, 'studies': 0, 'status': 'intérimaire', 'power': 'unlimited_flirt'},
        'chef des ventes': {'salary': 3, 'studies': 3, 'status': 'rien', 'power': 'salary_discard'},
        'chef des achats': {'salary': 3, 'studies': 3, 'status': 'rien', 'power': 'acquisition_discard'},
        'chercheur': {'salary': 2, 'studies': 6, 'status': 'rien', 'power': 'extra_card'},
        'chirurgien': {'salary': 4, 'studies': 6, 'status': 'rien', 'power': 'no_illness_extra_study'},
        'designer': {'salary': 3, 'studies': 4, 'status': 'rien', 'power': 'none'},
        'ecrivain': {'salary': 1, 'studies': 0, 'status': 'rien', 'power': 'prix_possible'},
        'garagiste': {'salary': 2, 'studies': 1, 'status': 'rien', 'power': 'no_accident'},
        'gourou': {'salary': 3, 'studies': 0, 'status': 'rien', 'power': 'none'},
        'jardinier': {'salary': 1, 'studies': 1, 'status': 'rien', 'power': 'none'},
        'journaliste': {'salary': 2, 'studies': 3, 'status': 'rien', 'power': 'see_hands_prix_possible'},
        'médecin': {'salary': 4, 'studies': 6, 'status': 'rien', 'power': 'no_illness_extra_study'},
        'médium': {'salary': 1, 'studies': 0, 'status': 'rien', 'power': 'see_deck'},
        'militaire': {'salary': 1, 'studies': 0, 'status': 'fonctionnaire', 'power': 'no_attentat'},
        'pharmacien': {'salary': 3, 'studies': 5, 'status': 'rien', 'power': 'no_illness'},
        'pilote de ligne': {'salary': 4, 'studies': 5, 'status': 'rien', 'power': 'travel_free'},
        'pizzaiolo': {'salary': 2, 'studies': 0, 'status': 'rien', 'power': 'none'},
        'plombier': {'salary': 1, 'studies': 1, 'status': 'intérimaire', 'power': 'none'},
        'policier': {'salary': 1, 'studies': 1, 'status': 'fonctionnaire', 'power': 'block_bandit_gourou'},
        'prof anglais': {'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none'},
        'prof francais': {'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none'},
        'prof histoire': {'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none'},
        'prof maths': {'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none'},
        'serveur': {'salary': 1, 'studies': 0, 'status': 'intérimaire', 'power': 'none'},
        'stripteaser': {'salary': 1, 'studies': 0, 'status': 'intérimaire', 'power': 'none'},
        'grand prof': {'salary': 3, 'studies': 'P', 'status': 'fonctionnaire', 'power': 'none'}
    }
    
    FLIRT_LOCATIONS = ['bar', 'boite de nuit', 'camping', 'cinema', 'hotel', 
                       'internet', 'parc', 'restaurant', 'theatre', 'zoo']
    MARRIAGE_LOCATIONS = ['corps-nuds', 'montcuq', 'monteton', 'Sainte-Vierge', 
                          'Fourqueux', 'Fourqueux', 'Fourqueux']
    CHILDREN_NAMES = ['diana', 'harry', 'hermionne', 'lara', 'leia', 'luigi', 
                      'luke', 'mario', 'rocky', 'zelda']
    ANIMALS = [
        {'name': 'chat', 'smiles': 1},
        {'name': 'chien', 'smiles': 1},
        {'name': 'lapin', 'smiles': 1},
        {'name': 'licorne', 'smiles': 3},
        {'name': 'poussin', 'smiles': 1}
    ]
    
    @classmethod
    def create_deck(cls) -> List[Card]:
        """Crée un deck complet de cartes"""
        deck = []
        
        # Métiers
        for job_name, job_data in cls.JOBS.items():
            deck.append(JobCard(job_name, job_data['salary'], job_data['studies'], 
                               job_data['status'], job_data['power']))
        
        # Études
        for _ in range(22):
            deck.append(StudyCard('simple', 1))
        for _ in range(3):
            deck.append(StudyCard('double', 2))
        
        # Salaires
        for level in range(1, 5):
            for _ in range(10):
                deck.append(SalaryCard(level))
        
        # Flirts
        for loc in cls.FLIRT_LOCATIONS:
            deck.append(FlirtCard(loc))
            deck.append(FlirtCard(loc))
        
        # Mariages
        for loc in cls.MARRIAGE_LOCATIONS:
            deck.append(MarriageCard(loc))
        
        # Adultères
        for _ in range(3):
            deck.append(AdulteryCard())
        
        # Enfants
        for name in cls.CHILDREN_NAMES:
            deck.append(ChildCard(name))
        
        # Animaux
        for animal in cls.ANIMALS:
            deck.append(AnimalCard(animal['name'], animal['smiles']))
        
        # Maisons
        deck.append(HouseCard('petite', 6, 1))
        deck.append(HouseCard('petite', 6, 1))
        deck.append(HouseCard('moyenne', 8, 2))
        deck.append(HouseCard('moyenne', 8, 2))
        deck.append(HouseCard('grande', 10, 3))
        
        # Voyages
        for _ in range(5):
            deck.append(TravelCard())
        
        # Cartes spéciales
        for special in ['anniversaire', 'arc en ciel', 'casino', 'chance', 
                       'etoile filante', 'heritage', 'piston', 'troc', 
                       'tsunami', 'vengeance']:
            deck.append(SpecialCard(special))
        
        # Coups durs
        for _ in range(5):
            deck.append(HardshipCard('accident'))
            deck.append(HardshipCard('burnout'))
            deck.append(HardshipCard('divorce'))
            deck.append(HardshipCard('impot'))
            deck.append(HardshipCard('licenciement'))
            deck.append(HardshipCard('maladie'))
            deck.append(HardshipCard('redoublement'))
        
        deck.append(HardshipCard('prison'))
        deck.append(HardshipCard('attentat'))
        
        # Autres
        deck.append(OtherCard('legion', 3))
        deck.append(OtherCard('prix', 4))
        deck.append(OtherCard('prix', 4))
        
        return deck