import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Card(ABC):
    """Classe de base pour toutes les cartes"""
    def __init__(self, image_path: str):
        self.id = str(uuid.uuid4())
        self.smiles = 0
        self.image: str = image_path
    
    def __str__(self):
        return f"YOUSK id : {self.id}"
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la carte en dictionnaire pour la sérialisation"""
        return {
            'id': self.id,
            'smiles': self.smiles,
            'type': self.__class__.__name__.lower(),
            'image': self.image
        }
    
    @abstractmethod
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        print("[WARNING] cette méthode ne devrait pas etre appellée")
        
        return True, ""

class JobCard(Card):
    """Carte métier"""
    def __init__(self, job_name: str, salary: int, studies: int, status: str, power: str, image_path: str):
        super().__init__(image_path)
        self.job_name = job_name
        self.salary = salary
        self.studies = studies
        self.status = status
        self.power = power
        self.smiles = 2
    
    def __str__(self):
        return f"{self.job_name} - smile : {self.smiles} - JobCard"
    
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
    def __init__(self, study_type: str, levels: int, image_path: str):
        super().__init__(image_path)
        self.study_type = study_type
        self.levels = levels
        self.smiles = 1
    
    def __str__(self):
        return f"{self.study_type} - smile : {self.smiles} - StudyCard"
    
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
        if player.has_job() and 'extra_study' not in player.get_job().power:
            return False, "Vous ne pouvez plus faire d'études après avoir trouvé un métier"
        return True, ""

class SalaryCard(Card):
    """Carte salaire"""
    def __init__(self, level: int, image_path: str):
        super().__init__(image_path)
        self.level = level
        self.smiles = 1
    
    def __str__(self):
        return f"{self.level} - smile : {self.smiles} - SalaryCard"
    
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

        max_salary = job.salary
        # ✅ Vérifier si le joueur a le Grand Prix d'excellence
        for c in player.get_all_played_cards():
            print(c.id)
            if isinstance(c, PriceCard):
                print("carte prix trouvée")
                if c.job_link == job.id:
                    print("le link est bon")
                    max_salary = 4
                    
        if self.level > max_salary:
            return False, f"Votre salaire maximum est de {max_salary}"
        
        return True, ""

class FlirtCard(Card):
    """Carte flirt"""
    def __init__(self, location: str, image_path: str):
        super().__init__(image_path)
        self.location = location
        self.smiles = 1
    
    def __str__(self):
        return f"{self.location} - smile : {self.smiles} - FlirtCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'flirt',
            'subtype': self.location
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        # Peut flirter si pas marié OU si on a un adultère
        if player.is_married() and not player.has_adultery():
            return False, "Vous êtes marié(e) sans adultère"
        return True, ""

class MarriageCard(Card):
    """Carte mariage"""
    def __init__(self, location: str, image_path:str):
        super().__init__(image_path)
        self.location = location
        self.smiles = 3
    
    def __str__(self):
        return f"{self.location} - smile : {self.smiles} - MarriageCard"
    
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
        
        if not player.has_any_flirt():
            return False, "Vous devez avoir un flirt pour vous marier"
        
        return True, ""

class AdulteryCard(Card):
    """Carte adultère"""
    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.smiles = 1
    
    def __str__(self):
        return f"adultaire - smile : {self.smiles} - AdulteryCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base['type'] = 'adultere'
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        if not player.is_married():
            return False, "Vous devez être marié(e) pour commettre un adultère"
        
        # Vérifier qu'on n'a pas déjà un adultère
        if player.has_adultery():
            return False, "Vous avez déjà un adultère"
        
        return True, ""

class ChildCard(Card):
    """Carte enfant"""
    def __init__(self, name: str, image_path: str):
        super().__init__(image_path)
        self.name = name
        self.smiles = 2
    
    def __str__(self):
        return f"{self.name} - smile : {self.smiles} - ChildCard"
    
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
    def __init__(self, animal_name: str, smiles: int, image_path: str):
        super().__init__(image_path)
        self.animal_name = animal_name
        self.smiles = smiles

    def __str__(self):
        return f"{self.animal_name} - smile : {self.smiles} - AnimalCard"
    
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
    def __init__(self, house_type: str, cost: int, smiles: int, image_path: str):
        super().__init__(image_path)
        self.house_type = house_type
        self.cost = cost
        self.smiles = smiles
    
    def __str__(self):
        return f"{self.house_type} - smile : {self.smiles} - HouseCard"
    
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
        
        # Calculer le coût requis (divisé par 2 si marié)
        required_cost = self.cost
        if player.is_married():
            required_cost = required_cost // 2
        
        # Vérifier la somme totale des salaires
        total_salary_value = player.get_available_salary_sum()
        if total_salary_value < required_cost:
            return False, f"Vous avez besoin d'une somme de salaires de {required_cost}"
        
        return True, ""

class TravelCard(Card):
    """Carte voyage"""
    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.cost = 3
        self.smiles = 1
    
    def __str__(self):
        return f"{self.cost} - smile : {self.smiles} - TravelCard"
    
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
        
        # Vérifier la somme totale des salaires
        total_salary_value = player.get_available_salary_sum()
        if total_salary_value < self.cost:
            return False, f"Vous avez besoin d'une somme de salaires de {self.cost}"
        
        return True, ""

class SpecialCard(Card):
    """Carte spéciale"""
    def __init__(self, special_type: str, image_path: str):
        super().__init__(image_path)
        self.special_type = special_type
        self.smiles = 0
    
    def __str__(self):
        return f"{self.special_type} - smile : {self.smiles} - SpecialCard"
    
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
    def __init__(self, hardship_type: str, image_path: str):
        super().__init__(image_path)
        self.hardship_type = hardship_type
        self.smiles = 0

    def __str__(self):
        return f"{self.hardship_type} - smile : {self.smiles} - HardshipCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'hardship',
            'subtype': self.hardship_type
        })
        return base
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        # Les coups durs sont joués sur d'autres joueurs
        print(f"le joueurs : {player.name}")
        if player.has_job() and f'immune_{self.hardship_type}' in player.get_job().power:
            return False, f"le joueur {player.name} est immunisé contre {self.hardship_type} grâce à son métier"

        return False, "Les coups durs doivent être joués sur un autre joueur"

class OtherCard(Card):
    """Autres cartes (légion d'honneur, prix)"""
    def __init__(self, card_type: str, smiles: int, image_path: str):
        super().__init__(image_path)
        self.card_type = card_type
        self.smiles = smiles
    
    def __str__(self):
        return f"{self.card_type} - smile : {self.smiles} - OtherCard"

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
    
class LegionCard(OtherCard):
    """Carte légion d'honneur"""
    def __init__(self, smiles: int, image_path: str):
        super().__init__("legion", smiles, image_path)

    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        if player.has_been_bandit:
            return False, "Vous avez été bandit dans la partie"
        return True, ""

class PriceCard(OtherCard):
    """Carte prix d'excellence"""
    def __init__(self, smiles: int, image_path: str):
        super().__init__('prix', smiles, image_path)
        self.job_link = None
    
    def can_be_played(self, player: 'Player') -> tuple[bool, str]:
        print("tentative de link de Prix", end=" ")
        job = player.get_job()
        if not job:
            return False, "Vous devez avoir un métier"
        if job.power not in ['prix_possible', 'see_hands_prix_possible']:
            return False, "Votre métier ne permet pas de recevoir un prix"
        self.job_link = job.id
        print("le link est : ", self.job_link)

        return True, ""

class Player:
    """Classe représentant un joueur"""
    def __init__(self, player_id: int, name: str):
        self.id = player_id
        self.name = name
        self.hand: List[Card] = []
        # Organisation des cartes jouées par catégories
        self.played = {
            "vie professionnelle": [],  # études, métier, salaires
            "vie personnelle": [],      # flirts, mariage, adultère, enfants, animaux
            "acquisitions": [],         # maisons, voyages
            "salaire dépensé": [],      # salaires utilisés pour acheter
            "cartes spéciales": []      # cartes spéciales, autres, et flirts avec adultère
        }
        self.skip_turns = 0
        self.has_been_bandit = False
        self.heritage = 0
        self.received_hardships = []
        self.connected = True
        self.session_id = None
    
    def __str__(self):
        return "Player YOUSK"
    
    def get_all_played_cards(self) -> List[Card]:
        """Retourne toutes les cartes jouées (toutes catégories)"""
        all_cards = []
        for category_cards in self.played.values():
            all_cards.extend(category_cards)
        return all_cards
    
    def add_card_to_played(self, card: Card):
        """Ajoute une carte à la bonne catégorie"""
        if isinstance(card, (StudyCard, JobCard, SalaryCard)):
            self.played["vie professionnelle"].append(card)
        elif isinstance(card, (MarriageCard, ChildCard, AnimalCard, AdulteryCard)):
            self.played["vie personnelle"].append(card)
        elif isinstance(card, FlirtCard):
            # ✅ Les flirts posés avec un adultère vont dans "cartes spéciales"
            if self.has_adultery():
                self.played["cartes spéciales"].append(card)
            else:
                self.played["vie personnelle"].append(card)
        elif isinstance(card, (HouseCard, TravelCard)):
            self.played["acquisitions"].append(card)
        elif isinstance(card, (SpecialCard, OtherCard)):
            self.played["cartes spéciales"].append(card)
    
    def remove_card_from_played(self, card: Card) -> bool:
        """Retire une carte des cartes jouées"""
        for category_cards in self.played.values():
            if card in category_cards:
                category_cards.remove(card)
                return True
        return False
    
    def spend_salaries(self, amount: int) -> List[SalaryCard]:
        """Dépense des salaires pour un achat et les déplace vers 'salaire dépensé'"""
        available_salaries = [c for c in self.played["vie professionnelle"] if isinstance(c, SalaryCard)]
        
        # Trier par niveau décroissant pour optimiser
        available_salaries.sort(key=lambda x: x.level, reverse=True)
        
        spent_salaries = []
        remaining = amount
        
        for salary in available_salaries:
            if remaining <= 0:
                break
            if salary.level <= remaining:
                spent_salaries.append(salary)
                remaining -= salary.level
        
        # Si on ne peut pas payer exactement, essayer d'autres combinaisons
        if remaining > 0:
            # Essayer avec les plus petites cartes
            available_salaries.sort(key=lambda x: x.level)
            spent_salaries = []
            total = 0
            for salary in available_salaries:
                if total >= amount:
                    break
                spent_salaries.append(salary)
                total += salary.level
        
        # Déplacer les salaires dépensés
        for salary in spent_salaries:
            self.played["vie professionnelle"].remove(salary)
            self.played["salaire dépensé"].append(salary)
        
        return spent_salaries
    
    def get_available_salary_sum(self) -> int:
        """Retourne la somme des salaires disponibles (non dépensés)"""
        return sum(c.level for c in self.played["vie professionnelle"] if isinstance(c, SalaryCard))
    
    def has_job(self) -> bool:
        return any(isinstance(card, JobCard) for card in self.played["vie professionnelle"])
    
    def has_any_flirt(self) -> bool:
        """Vérifie si le joueur a au moins un flirt"""
        # Chercher dans vie personnelle ET cartes spéciales (flirts avec adultère)
        all_flirts = [c for c in self.played["vie personnelle"] if isinstance(c, FlirtCard)]
        all_flirts.extend([c for c in self.played["cartes spéciales"] if isinstance(c, FlirtCard)])
        return len(all_flirts) > 0
    
    def has_adultery(self) -> bool:
        """Vérifie si le joueur a un adultère"""
        return any(isinstance(card, AdulteryCard) for card in self.played["vie personnelle"])
    
    def get_job(self) -> JobCard:
        for card in self.played["vie professionnelle"]:
            if isinstance(card, JobCard):
                return card
        return None
    
    def has_teacher_job(self) -> bool:
        job = self.get_job()
        return job and job.job_name.startswith('prof')
    
    def count_studies(self) -> int:
        total = 0
        for card in self.played["vie professionnelle"]:
            if isinstance(card, StudyCard):
                total += card.levels
        return total
    
    def count_salaries(self) -> int:
        return sum(1 for card in self.played["vie professionnelle"] if isinstance(card, SalaryCard))
    
    def is_married(self) -> bool:
        return any(isinstance(card, MarriageCard) for card in self.played["vie personnelle"])
    
    def has_flirt_at_location(self, location: str) -> bool:
        # Chercher dans vie personnelle ET cartes spéciales
        all_flirts = [c for c in self.played["vie personnelle"] if isinstance(c, FlirtCard)]
        all_flirts.extend([c for c in self.played["cartes spéciales"] if isinstance(c, FlirtCard)])
        return any(flirt.location == location for flirt in all_flirts)
    
    def calculate_smiles(self) -> int:
        total = sum(card.smiles for card in self.get_all_played_cards())
        
        # Bonus licorne + arc-en-ciel + étoile filante
        all_cards = self.get_all_played_cards()
        has_licorne = any(isinstance(c, AnimalCard) and c.animal_name == 'licorne' for c in all_cards)
        has_arc = any(isinstance(c, SpecialCard) and c.special_type == 'arc en ciel' for c in all_cards)
        has_etoile = any(isinstance(c, SpecialCard) and c.special_type == 'etoile filante' for c in all_cards)
        
        if has_licorne and has_arc and has_etoile:
            total += 3
        
        return total
    
    def to_dict(self, hide_hand: bool = False) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'hand': [] if hide_hand else [card.to_dict() for card in self.hand],
            'hand_count': len(self.hand),
            'played': {
                category: [card.to_dict() for card in cards]
                for category, cards in self.played.items()
            },
            'skip_turns': self.skip_turns,
            'has_been_bandit': self.has_been_bandit,
            'heritage': self.heritage,
            'received_hardships': self.received_hardships,
            'connected': self.connected
        }

class CardFactory:
    """Factory pour créer les cartes"""
    
    JOBS = [
        {'name': 'architecte', 'salary': 3, 'studies': 4, 'status': 'rien', 'power': 'house_free', 'image': 'personnal_life/professionnal_life/JobCards/architecte.png'},
        {'name': 'astronaute', 'salary': 4, 'studies': 6, 'status': 'rien', 'power': 'instant', 'image': 'personnal_life/professionnal_life/JobCards/astronaute.png'},
        {'name': 'avocat', 'salary': 3, 'studies': 4, 'status': 'rien', 'power': 'immune_divorce', 'image': 'personnal_life/professionnal_life/JobCards/avocat.png'},
        {'name': 'bandit', 'salary': 4, 'studies': 0, 'status': 'rien', 'power': 'immune_tax__immune_licenciement', 'image': 'personnal_life/professionnal_life/JobCards/bandit.png'},
        {'name': 'barman', 'salary': 1, 'studies': 0, 'status': 'intérimaire', 'power': 'unlimited_flirt', 'image': 'personnal_life/professionnal_life/JobCards/barman.png'},
        {'name': 'chef des ventes', 'salary': 3, 'studies': 3, 'status': 'rien', 'power': 'instant', 'image': 'personnal_life/professionnal_life/JobCards/chef_des_ventes.png'},
        {'name': 'chef des achats', 'salary': 3, 'studies': 3, 'status': 'rien', 'power': 'instant', 'image': 'personnal_life/professionnal_life/JobCards/chef_des_achats.png'},
        {'name': 'chercheur', 'salary': 2, 'studies': 6, 'status': 'rien', 'power': 'extra_card__prix_possible', 'image': 'personnal_life/professionnal_life/JobCards/chercheur.png'},
        {'name': 'chirurgien', 'salary': 4, 'studies': 6, 'status': 'rien', 'power': 'no_illness__extra_study', 'image': 'personnal_life/professionnal_life/JobCards/chirurgien.png'},
        {'name': 'designer', 'salary': 3, 'studies': 4, 'status': 'rien', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/designer.png'},
        {'name': 'ecrivain', 'salary': 1, 'studies': 0, 'status': 'rien', 'power': 'prix_possible', 'image': 'personnal_life/professionnal_life/JobCards/ecrivain.png'},
        {'name': 'garagiste', 'salary': 2, 'studies': 1, 'status': 'rien', 'power': 'immune_accident', 'image': 'personnal_life/professionnal_life/JobCards/garagiste.png'},
        {'name': 'gourou', 'salary': 3, 'studies': 0, 'status': 'rien', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/gourou.png'},
        {'name': 'jardinier', 'salary': 1, 'studies': 1, 'status': 'rien', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/jardinier.png'},
        {'name': 'journaliste', 'salary': 2, 'studies': 3, 'status': 'rien', 'power': 'instant__prix_possible', 'image': 'personnal_life/professionnal_life/JobCards/journaliste.png'},
        {'name': 'médecin', 'salary': 4, 'studies': 6, 'status': 'rien', 'power': 'immune_maladie__extra_study', 'image': 'personnal_life/professionnal_life/JobCards/medecin.png'},
        {'name': 'médium', 'salary': 1, 'studies': 0, 'status': 'rien', 'power': 'instant', 'image': 'personnal_life/professionnal_life/JobCards/medium.png'},
        {'name': 'militaire', 'salary': 1, 'studies': 0, 'status': 'fonctionnaire', 'power': 'no_attentat', 'image': 'personnal_life/professionnal_life/JobCards/militaire.png'},
        {'name': 'pharmacien', 'salary': 3, 'studies': 5, 'status': 'rien', 'power': 'immune_maladie', 'image': 'personnal_life/professionnal_life/JobCards/pharmacien.png'},
        {'name': 'pilote de ligne', 'salary': 4, 'studies': 5, 'status': 'rien', 'power': 'travel_free', 'image': 'personnal_life/professionnal_life/JobCards/pilote_de_ligne.png'},
        {'name': 'pizzaiolo', 'salary': 2, 'studies': 0, 'status': 'rien', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/pizzaiolo.png'},
        {'name': 'plombier', 'salary': 1, 'studies': 1, 'status': 'intérimaire', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/plombier.png'},
        {'name': 'policier', 'salary': 1, 'studies': 1, 'status': 'fonctionnaire', 'power': 'block_bandit_gourou', 'image': 'personnal_life/professionnal_life/JobCards/policier.png'},
        {'name': 'prof anglais', 'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/prof_anglais.png'},
        {'name': 'prof francais', 'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/prof_francais.png'},
        {'name': 'prof histoire', 'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/prof_histoire.png'},
        {'name': 'prof maths', 'salary': 2, 'studies': 2, 'status': 'fonctionnaire', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/prof_maths.png'},
        {'name': 'serveur', 'salary': 1, 'studies': 0, 'status': 'intérimaire', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/serveur.png'},
        {'name': 'stripteaser', 'salary': 1, 'studies': 0, 'status': 'intérimaire', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/stripteaser.png'},
        {'name': 'grand prof', 'salary': 3, 'studies': 'P', 'status': 'fonctionnaire', 'power': 'none', 'image': 'personnal_life/professionnal_life/JobCards/grand_prof.png'}
    ]
    
    FLIRT_LOCATIONS = ['bar', 'boite de nuit', 'camping', 'cinema', 'hotel', 
                       'internet', 'parc', 'restaurant', 'theatre', 'zoo']
    MARRIAGE_LOCATIONS = ['corps-nuds', 'montcuq', 'monteton', 'sainte-vierge', 
                          'fourqueux', 'fourqueux', 'fourqueux']
    CHILDREN_NAMES = ['diana', 'harry', 'hermione', 'lara', 'leia', 'luigi', 
                      'luke', 'mario', 'rocky', 'zelda']
    ANIMALS = [
        {'name': 'chat', 'smiles': 1},
        {'name': 'chien', 'smiles': 1},
        {'name': 'lapin', 'smiles': 1},
        {'name': 'licorne', 'smiles': 3},
        {'name': 'poussin', 'smiles': 1}
    ]

    TRIP_NAMES = ["le caire", "londres", "new york", "rio", "sydney"]

    SPECIAL_CARDS = ['anniversaire', 'arc en ciel', 'casino', 'chance', 
                       'etoile filante', 'heritage', 'piston', 'troc', 
                       'tsunami', 'vengeance']

    def test_create_deck(cls) -> List[Card]:
        """effectue un tests avec des cartes customs"""
        deck = []
        jobs_custom = [
            {'name': 'bandit', 'salary': 4, 'studies': 0, 'status': 'rien', 'power': 'immune_tax__immune_licenciement', 'image': 'personnal_life/professionnal_life/JobCards/bandit.png'},
            {'name': 'bandit', 'salary': 4, 'studies': 0, 'status': 'rien', 'power': 'immune_tax__immune_licenciement', 'image': 'personnal_life/professionnal_life/JobCards/bandit.png'},
            {'name': 'bandit', 'salary': 4, 'studies': 0, 'status': 'rien', 'power': 'immune_tax__immune_licenciement', 'image': 'personnal_life/professionnal_life/JobCards/bandit.png'},
            {'name': 'bandit', 'salary': 4, 'studies': 0, 'status': 'rien', 'power': 'immune_tax__immune_licenciement', 'image': 'personnal_life/professionnal_life/JobCards/bandit.png'}    
        ]
        for job in jobs_custom:
            deck.append(JobCard(job['name'], job['salary'], job['studies'], 
                               job['status'], job['power'], job['image']))

        for _ in range(5):
            deck.append(StudyCard('double', 2, "personnal_life/professionnal_life/StudyCards/study2.png"))


        for level in range(1, 5):
            for _ in range(5):
                deck.append(SalaryCard(level, f"personnal_life/professionnal_life/SalaryCards/salary{level}.png"))

        # Maisons

        # Voyages
        for _ in range(0):
            deck.append(TravelCard())

        # Flirts
        """
        for loc in cls.FLIRT_LOCATIONS:
            l = loc.replace(" ", "_")
            deck.append(FlirtCard(loc, f"personnal_life/flirts/{l}.png"))
            deck.append(FlirtCard(loc, f"personnal_life/flirts/{l}.png"))
        """

        # Mariages
        """
        for loc in cls.MARRIAGE_LOCATIONS:
            l = loc.replace(" ", "_").replace("-", "_")
            deck.append(MarriageCard(loc, f"personnal_life/mariages/mariage_{l}.png"))
        """
        # Enfants
        """
        for name in cls.CHILDREN_NAMES:
            deck.append(ChildCard(name, f"personnal_life/children/{name}.png"))
        """
         # Cartes spéciales
        for special in ['tsunami', 'arc en ciel', 'casino', 'chance',
                        "arc en ciel", "arc en ciel", "anniversaire", "anniversaire", "anniversaire"]:
            
            s = special.replace(' ', '_')
            deck.append(SpecialCard(special, f"special_cards/{s}.png"))
        
        

        return deck
    
    @classmethod
    def create_deck(cls) -> List[Card]:
        """Crée un deck complet de cartes"""
        #########################
        return cls.test_create_deck(cls)
        # TESTING
        #########################
        
        deck = []
        
        # Métiers
        for job in cls.JOBS:
            deck.append(JobCard(job['name'], job['salary'], job['studies'], 
                        job['status'], job['power'], job['image']))
        
        # Études
        for _ in range(22):
            deck.append(StudyCard('simple', 1, "personnal_life/professionnal_life/StudyCards/study1.png"))
        for _ in range(3):
            deck.append(StudyCard('double', 2, "personnal_life/professionnal_life/StudyCards/study2.png"))
        
        # Salaires
        for level in range(1, 5):
            for _ in range(10):
                deck.append(SalaryCard(level, f"personnal_life/professionnal_life/SalaryCards/salary{level}.png"))
        
        # Flirts
        for loc in cls.FLIRT_LOCATIONS:
            l = loc.replace(" ", "_")
            deck.append(FlirtCard(loc, f"personnal_life/flirts/{l}.png"))
            deck.append(FlirtCard(loc, f"personnal_life/flirts/{l}.png"))
        
        # Mariages
        for loc in cls.MARRIAGE_LOCATIONS:
            l = loc.replace(" ", "_").replace("-", "_")
            deck.append(MarriageCard(loc, f"personnal_life/mariages/mariage_{l}.png"))
        
        # Adultères
        for _ in range(3):
            deck.append(AdulteryCard("personnal_life/mariages/adultere.png"))
        
        # Enfants
        for name in cls.CHILDREN_NAMES:
            deck.append(ChildCard(name, f"personnal_life/children/{name}.png"))
        
        # Animaux
        for animal in cls.ANIMALS:
            deck.append(AnimalCard(animal['name'], animal['smiles'], f"aquisition_cards/animals/{animal['name']}.png"))
        
        # Maisons
        deck.append(HouseCard('petite', 6, 1, "aquisition_cards/houses/maison1.png"))
        deck.append(HouseCard('petite', 6, 1, "aquisition_cards/houses/maison1.png"))
        deck.append(HouseCard('moyenne', 8, 2, "aquisition_cards/houses/maison2.png"))
        deck.append(HouseCard('moyenne', 8, 2, "aquisition_cards/houses/maison2.png"))
        deck.append(HouseCard('grande', 10, 3, "aquisition_cards/houses/maison3.png"))
        
        # Voyages
        for trip_name in cls.TRIP_NAMES:
            t = trip_name.replace(" ", "_")
            deck.append(TravelCard(f"aquisition_cards/trip/{t}.png"))
        
        # Cartes spéciales
        for special in cls.SPECIAL_CARDS:
            s = special.replace(' ', '_')
            deck.append(SpecialCard(special, f"special_cards/{s}.png"))
        
        # Coups durs
        for _ in range(5):
            deck.append(HardshipCard('accident', "hardship_cards/accident.png"))
            deck.append(HardshipCard('burnout', "hardship_cards/burnout.png"))
            deck.append(HardshipCard('divorce', "hardship_cards/divorce.png"))
            deck.append(HardshipCard('tax', "hardship_cards/tax.png"))
            deck.append(HardshipCard('licenciement', "hardship_cards/licenciement.png"))
            deck.append(HardshipCard('maladie', "hardship_cards/maladie.png"))
            deck.append(HardshipCard('redoublement', "hardship_cards/redoublement.png"))
        
        deck.append(HardshipCard('prison', "hardship_cards/prison.png"))
        deck.append(HardshipCard('attentat', "hardship_cards/attentat.png"))
        
        # Autres
        deck.append(LegionCard(3, "personnal_life/professionnal_life/legion.png"))
        deck.append(PriceCard(4, "personnal_life/professionnal_life/price.png"))
        deck.append(PriceCard(4, "personnal_life/professionnal_life/price.png"))
        
        return deck
    