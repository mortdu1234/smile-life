from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.Game import Game

from src.cartes import (
    Card, JobCard, StudyCard, SalaryCard, MarriageCard, 
    ChildCard, AnimalCard, AdulteryCard, FlirtCard, FlirtWithChildCard,
    AquisitionCard, SpecialCard, OtherCard, HardshipCard,
    PermanentEffet, FemaleChild, MaleChild,
    LicorneAnimal, ArcEnCielCard, EtoileFilanteCard,
    GynocratieHardship, PhalocratieHardship
)


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
            "cartes spéciales": [],      # cartes spéciales, autres, et flirts avec adultère
            "effet permanent": []
        }
        self.skip_turns = 0
        self.has_been_bandit = False
        self.heritage = 0
        self.received_hardships: list[HardshipCard] = []
        self.connected = True
        self.session_id = None
    
    def get_marriage(self):
        for card in self.played["vie personnelle"]:
            if isinstance(card, MarriageCard):
                return card
        return None
    
    # EFFET PERMANENT
    def get_played_effet_permanent(self):
        return self.played["effet permanent"]
    def add_card_to_effet_permanent(self, card: Card):
        self.played["effet permanent"].append(card)
    def get_played_effet_permanent_by_id(self, card_id):
        for card in self.played["effet permanent"]:
            if card.id == card_id:
                return card
        return None
    
    # VIE PROFESSIONNELLE
    def get_played_vie_pro(self):
        return self.played["vie professionnelle"]
    def add_card_to_vie_pro(self, card: Card):
        self.played["vie professionnelle"].append(card)
    def get_played_vie_pro_by_id(self, card_id):
        for card in self.played["vie professionnelle"]:
            if card.id == card_id:
                return card
        return None
    
    # VIE PERSONNELLE
    def get_played_vie_perso(self):
        return self.played["vie personnelle"]
    def add_card_to_vie_perso(self, card: Card):
        self.played["vie personnelle"].append(card)
    def get_played_vie_perso_by_id(self, card_id):
        for card in self.played["vie personnelle"]:
            if card.id == card_id:
                return card
        return None
    
    # AQUISITIONS
    def get_played_acquisitions(self):
        return self.played["acquisitions"]
    def add_card_to_acquisitions(self, card: Card):
        self.played["acquisitions"].append(card)
    def get_played_acquisitions_by_id(self, card_id):
        for card in self.played["acquisitions"]:
            if card.id == card_id:
                return card
        return None
    
    # SALAIRE DEPENSE
    def get_played_salaire_depense(self):
        return self.played["salaire dépensé"]
    def add_card_to_salaire_depense(self, card: Card):
        self.played["salaire dépensé"].append(card)
    def get_played_salaire_depense_by_id(self, card_id):
        for card in self.played["salaire dépensé"]:
            if card.id == card_id:
                return card
        return None
    
    # CARTES SPECIALES
    def get_played_carte_speciale(self):
        return self.played["cartes spéciales"]
    def add_card_to_carte_speciale(self, card: Card):
        self.played["cartes spéciales"].append(card)
    def get_played_carte_speciale_by_id(self, card_id):
        for card in self.played["cartes spéciales"]:
            if card.id == card_id:
                return card
        return None

    # MAIN
    def get_card_from_hand(self):
        return self.hand
    def remove_card_from_hand(self, card: Card):
        """retire une carte a la main du joueur"""
        self.hand.remove(card)
    def add_card_to_hand(self, card: Card):
        """ajoute une carte a la main du joueur"""
        self.hand.append(card)

    # JOBS
    def has_job(self) -> bool:
        return any(isinstance(card, JobCard) for card in self.played["vie professionnelle"])
    def get_job(self) -> List[JobCard]:
        jobs = []
        for card in self.played["vie professionnelle"]:
            if isinstance(card, JobCard):
                jobs.append(card)
        return jobs

    def __str__(self):
        return self.name
    
    def get_last_flirt(self) -> FlirtCard:
        print("[START] : Player.get_last_flirt()")
        i = len(self.played["vie personnelle"])-1
        while i >= 0:
            card: Card = self.played["vie personnelle"][i]
            if isinstance(card, FlirtCard):
                i = -1
            if isinstance(card, FlirtWithChildCard):
                return card
            i -= 1
        return None
    
    def get_power(self) -> list[str]:
        powers = []
        if self.has_job():
            for job in self.get_job():
                powers += job.get_power()
        for card in self.get_all_played_cards():
            if isinstance(card, PermanentEffet):
                powers += card.get_power()
        print(f"[FONCTION] get power : {powers}")
        return powers

    
    def get_all_played_cards(self) -> List[Card]:
        """Retourne toutes les cartes jouées (toutes catégories)"""
        all_cards = []
        for category_cards in self.played.values():
            all_cards.extend(category_cards)
        return all_cards
    
    def add_card_to_played(self, card: Card):
        """Ajoute une carte à la bonne catégorie"""
        if isinstance(card, PermanentEffet):
            self.add_card_to_effet_permanent(card)
        elif isinstance(card, (StudyCard, JobCard, SalaryCard)):
            self.played["vie professionnelle"].append(card)
        elif isinstance(card, (MarriageCard, ChildCard, AnimalCard, AdulteryCard)):
            self.played["vie personnelle"].append(card)
        elif isinstance(card, FlirtCard):
            # ✅ Les flirts posés avec un adultère vont dans "cartes spéciales"
            if self.has_adultery():
                self.played["cartes spéciales"].append(card)
            else:
                self.played["vie personnelle"].append(card)
        elif isinstance(card, (AquisitionCard)):
            self.played["acquisitions"].append(card)
        elif isinstance(card, (SpecialCard, OtherCard)):
            self.played["cartes spéciales"].append(card)
        elif isinstance(card, (HardshipCard)):
            self.received_hardships.append(card)
        else:
            print("[ERROR] add_card_to_played CARTE INCONNUE", card)
        
    
    def remove_card_from_played(self, card: Card) -> bool:
        """Retire une carte des cartes jouées"""
        for category_cards in self.played.values():
            if card in category_cards:
                category_cards.remove(card)
                return True
        return False
    
    def get_played_card_by_id(self, card_id):
        cards = self.get_all_played_cards()
        for card in cards:
            if card.id == card_id:
                return card
        return None
    
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
    def has_any_flirt(self) -> bool:
        """Vérifie si le joueur a au moins un flirt"""
        # Chercher dans vie personnelle ET cartes spéciales (flirts avec adultère)
        all_flirts = [c for c in self.played["vie personnelle"] if isinstance(c, FlirtCard)]
        all_flirts.extend([c for c in self.played["cartes spéciales"] if isinstance(c, FlirtCard)])
        return len(all_flirts) > 0
    
    def has_adultery(self) -> bool:
        """Vérifie si le joueur a un adultère"""
        print(f"[DEBUG] : {self.played}, {self.name}\n\n")
        return any(isinstance(card, AdulteryCard) for card in self.played["vie personnelle"])
    
    
  
    

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
        
        # Gestion de la licorne
        has_licorne = any(isinstance(c, LicorneAnimal) for c in all_cards)
        has_arc = any(isinstance(c, ArcEnCielCard) for c in all_cards)
        has_etoile = any(isinstance(c, EtoileFilanteCard) for c in all_cards)
        if has_licorne and has_arc and has_etoile:
            total += 3
        
        # Gestion de gynocratie et phalocratie
        has_gynocratie = any(isinstance(c, GynocratieHardship) for c in all_cards)
        has_phalocratie = any(isinstance(c, PhalocratieHardship) for c in all_cards)
        
        if has_gynocratie:
            nb_female = sum(1 for card in all_cards if isinstance(card, FemaleChild))
            total -= nb_female
        if has_phalocratie:
            nb_male = sum(1 for card in all_cards if isinstance(card, MaleChild))
            total -= nb_male
        


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
            'received_hardships': [
                card.to_dict().get('subtype', 'malus') if hasattr(card, 'to_dict') else str(card)
                for card in self.received_hardships
            ],
            'connected': self.connected
        }