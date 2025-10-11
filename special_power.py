"""
Extension pour gérer les pouvoirs spéciaux des métiers et cartes spéciales
"""

from card_classes import Card, Player, JobCard, FlirtCard, HardshipCard
from typing import List

class PowerManager:
    """Gestionnaire des pouvoirs spéciaux"""
    
    @staticmethod
    def can_play_card_with_powers(card: Card, player: Player) -> tuple[bool, str]:
        """Vérifie si une carte peut être jouée en tenant compte des pouvoirs"""
        # Vérification de base
        can_play, message = card.can_be_played(player)
        if not can_play:
            return False, message
        
        job = player.get_job()
        if not job:
            return True, ""
        
        # Pouvoirs spéciaux qui modifient les règles
        
        # Barman: flirts illimités
        if isinstance(card, FlirtCard) and job.power == 'unlimited_flirt':
            if player.is_married():
                return True, ""  # Override la règle normale
        
        return True, ""
    
    @staticmethod
    def apply_hardship_immunities(hardship: HardshipCard, target_player: Player) -> tuple[bool, str]:
        """Vérifie si un joueur est immunisé contre un coup dur"""
        job = target_player.get_job()
        if not job:
            return True, ""  # Pas de protection
        
        immunities = {
            'accident': 'no_accident',  # Garagiste
            'maladie': 'no_illness',    # Pharmacien, Médecin, Chirurgien
            'attentat': 'no_attentat',  # Militaire
            'divorce': 'no_divorce',    # Avocat
            'licenciement': 'no_fire_tax',  # Bandit (partiellement)
            'impot': 'no_fire_tax'      # Bandit (partiellement)
        }
        
        hardship_type = hardship.hardship_type
        required_power = immunities.get(hardship_type)
        
        if required_power:
            if job.power == required_power:
                return False, f"Protection: {job.job_name}"
            
            # Cas spéciaux
            if hardship_type == 'maladie' and job.power == 'no_illness_extra_study':
                return False, f"Protection: {job.job_name}"
        
        # Policier bloque bandit et gourou
        if job.job_name == 'policier':
            # Vérifier si l'attaquant est bandit ou gourou
            # (cette logique devrait être dans le contexte du jeu)
            pass
        
        return True, ""
    
    @staticmethod
    def calculate_house_cost(player: Player, house_cost: int) -> int:
        """Calcule le coût réel d'une maison selon les pouvoirs"""
        job = player.get_job()
        if job and job.power == 'house_free':
            return 0  # Architecte: maison gratuite
        return house_cost
    
    @staticmethod
    def calculate_travel_cost(player: Player, travel_cost: int) -> int:
        """Calcule le coût réel d'un voyage selon les pouvoirs"""
        job = player.get_job()
        if job and job.power == 'travel_free':
            return 0  # Pilote de ligne: voyage gratuit
        return travel_cost
    
    @staticmethod
    def can_pick_from_discard(player: Player) -> bool:
        """Vérifie si le joueur peut choisir dans la défausse"""
        job = player.get_job()
        if job and job.power in ['discard_pick', 'acquisition_discard', 'salary_discard']:
            return True
        return False
    
    @staticmethod
    def get_extra_cards_count(player: Player) -> int:
        """Retourne le nombre de cartes supplémentaires à piocher"""
        job = player.get_job()
        if job and job.power == 'extra_card':
            return 1  # Chercheur pioche 2 cartes au lieu d'1
        return 0
    
    @staticmethod
    def can_see_other_hands(player: Player) -> bool:
        """Vérifie si le joueur peut voir les mains des autres"""
        job = player.get_job()
        if job and 'see_hands' in job.power:
            return True
        return False
    
    @staticmethod
    def can_see_deck_top(player: Player) -> bool:
        """Vérifie si le joueur peut voir le dessus du deck"""
        job = player.get_job()
        if job and job.power == 'see_deck':
            return True  # Médium
        return False
    
    @staticmethod
    def can_win_prize(player: Player) -> bool:
        """Vérifie si le joueur peut recevoir un prix"""
        job = player.get_job()
        if not job:
            return False
        
        if 'prix_possible' in job.power:
            return True
        return False

class GameRules:
    """Gestionnaire des règles du jeu"""
    
    @staticmethod
    def validate_flirt_locations(player: Player, flirt_location: str, marriage_location: str) -> bool:
        """Vérifie si le mariage correspond à un flirt"""
        # Mapping des lieux de flirt vers les lieux de mariage
        location_mapping = {
            'bar': ['Fourqueux'],
            'boite de nuit': ['Fourqueux'],
            'camping': ['monteton'],
            'cinema': ['corps-nuds'],
            'hotel': ['Fourqueux'],
            'internet': ['Sainte-Vierge'],
            'parc': ['montcuq'],
            'restaurant': ['Fourqueux'],
            'theatre': ['montcuq'],
            'zoo': ['monteton']
        }
        
        valid_marriages = location_mapping.get(flirt_location, [])
        return marriage_location in valid_marriages
    
    @staticmethod
    def can_become_grand_prof(player: Player) -> bool:
        """Vérifie si un joueur peut devenir grand prof"""
        job = player.get_job()
        if not job:
            return False
        
        # Doit être un professeur
        teacher_jobs = ['prof anglais', 'prof francais', 'prof histoire', 'prof maths']
        return job.job_name in teacher_jobs
    
    @staticmethod
    def calculate_unemployment_benefit(player: Player) -> int:
        """Calcule les allocations chômage"""
        job = player.get_job()
        if not job:
            return 0
        
        # Intérimaires: pas d'allocations
        if job.status == 'intérimaire':
            return 0
        
        # Fonctionnaires: protection renforcée
        if job.status == 'fonctionnaire':
            return job.salary
        
        # Autres: allocations réduites
        return max(1, job.salary - 1)
    
    @staticmethod
    def is_protected_from_firing(player: Player) -> bool:
        """Vérifie si un joueur est protégé du licenciement"""
        job = player.get_job()
        if not job:
            return False
        
        # Fonctionnaires sont protégés
        if job.status == 'fonctionnaire':
            return True
        
        # Bandit est partiellement protégé
        if job.power == 'no_fire_tax':
            return True
        
        return False
    
    @staticmethod
    def calculate_studies_bonus(player: Player) -> int:
        """Calcule les bonus d'études"""
        job = player.get_job()
        if not job:
            return 0
        
        # Médecin et Chirurgien: bonus d'étude en cas de maladie évitée
        if job.power == 'no_illness_extra_study':
            # Cette logique dépend du contexte
            pass
        
        return 0

class SpecialCardHandler:
    """Gestionnaire des cartes spéciales"""
    
    @staticmethod
    def handle_troc(player: Player, other_player: Player, card_id: str) -> bool:
        """Gère l'échange de cartes (Troc)"""
        # Logique d'échange
        pass
    
    @staticmethod
    def handle_vengeance(player: Player, target_player: Player) -> bool:
        """Gère la vengeance"""
        # Renvoyer un coup dur reçu
        pass
    
    @staticmethod
    def handle_piston(player: Player) -> bool:
        """Gère le piston (obtenir un métier sans études)"""
        pass
    
    @staticmethod
    def handle_heritage(player: Player, amount: int):
        """Gère l'héritage"""
        player.heritage += amount
    
    @staticmethod
    def handle_casino(player: Player, deck: List[Card]) -> tuple[bool, int]:
        """Gère le casino (parier des smiles)"""
        # Retourne (gagné, montant)
        import random
        won = random.choice([True, False])
        return won, 2
    
    @staticmethod
    def handle_tsunami(players: List[Player]):
        """Gère le tsunami (tout le monde défausse)"""
        for player in players:
            if player.is_married():
                # Retirer le mariage
                player.played = [c for c in player.played 
                               if not isinstance(c, MarriageCard)]
    
    @staticmethod
    def handle_chance(player: Player, deck: List[Card]) -> Card:
        """Gère la chance (piocher 3 cartes et en choisir 1)"""
        if len(deck) < 3:
            return None
        
        choices = [deck.pop() for _ in range(3)]
        # Le joueur doit choisir, les autres retournent dans le deck
        return choices  # Retourne les choix
    
    @staticmethod
    def handle_rainbow_bonus(player: Player) -> int:
        """Vérifie le bonus licorne + arc-en-ciel + étoile"""
        from card_classes import AnimalCard, SpecialCard
        
        has_unicorn = any(isinstance(c, AnimalCard) and c.animal_name == 'licorne' 
                         for c in player.played)
        has_rainbow = any(isinstance(c, SpecialCard) and c.special_type == 'arc en ciel' 
                         for c in player.played)
        has_star = any(isinstance(c, SpecialCard) and c.special_type == 'etoile filante' 
                      for c in player.played)
        
        if has_unicorn and has_rainbow and has_star:
            return 3
        return 0

# Exemple d'utilisation
if __name__ == '__main__':
    from card_classes import Player, CardFactory, JobCard, HardshipCard
    
    # Créer un joueur avec un métier
    player = Player(0, "Test")
    
    # Ajouter le métier de garagiste
    garagiste = JobCard('garagiste', 2, 1, 'rien', 'no_accident')
    player.played.append(garagiste)
    
    # Tester l'immunité
    accident = HardshipCard('accident')
    is_vulnerable, msg = PowerManager.apply_hardship_immunities(accident, player)
    print(f"Le garagiste peut-il recevoir un accident ? {is_vulnerable} - {msg}")
    
    # Tester le coût d'une maison pour un architecte
    player2 = Player(1, "Architecte")
    architecte = JobCard('architecte', 3, 4, 'rien', 'house_free')
    player2.played.append(architecte)
    
    house_cost = PowerManager.calculate_house_cost(player2, 10)
    print(f"Coût de la maison pour l'architecte: {house_cost}")