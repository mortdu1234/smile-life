import random
import uuid
from flask_socketio import emit
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from threading import Event



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
    def can_be_played(self, player: 'Player', game: 'Game') -> tuple[bool, str]:
        print("[WARNING] cette méthode ne devrait pas etre appellée")
        
        return True, ""
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        """pose la carte"""
        print("pose la carte")
        current_player.hand.remove(self)
        current_player.add_card_to_played(self)

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
    
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        # Les études ne peuvent être jouées que si on n'a pas encore de métier
        if current_player.has_job() and 'extra_study' not in current_player.get_job().power:
            return False, "Vous ne pouvez plus faire d'études après avoir trouvé un métier"
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

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
    
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        job = current_player.get_job()
        if not job:
            return False, "Vous devez avoir un métier pour recevoir un salaire"

        max_salary = job.salary
        # ✅ Vérifier si le joueur a le Grand Prix d'excellence
        for c in current_player.get_all_played_cards():
            print(c.id)
            if isinstance(c, PriceCard):
                print("carte prix trouvée")
                if c.job_link == job.id:
                    print("le link est bon")
                    max_salary = 4
                    
        if self.level > max_salary:
            return False, f"Votre salaire maximum est de {max_salary}"
        
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

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
    
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        # Peut flirter si pas marié OU si on a un adultère
        if current_player.is_married() and not current_player.has_adultery():
            return False, "Vous êtes marié(e) sans adultère"
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

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
    
    def discard_play_card(self, game: 'Game', effected_player: 'Player'):
        effected_player.remove_card_from_played(self)
        game.discard.append(self)
        if effected_player.id == game.current_player:
            game.next_player()
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        if current_player.is_married():
            return False, "Vous êtes déjà marié(e)"
        
        if not current_player.has_any_flirt():
            return False, "Vous devez avoir un flirt pour vous marier"
        
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

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
    
    def discard_play_card(self, game: 'Game', effected_player: 'Player'):
        effected_player.remove_card_from_played(self)
        game.discard.append(self)
        if effected_player.id == game.current_player:
            game.next_player()

    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        if not current_player.is_married():
            return False, "Vous devez être marié(e) pour commettre un adultère"
        
        # Vérifier qu'on n'a pas déjà un adultère
        if current_player.has_adultery():
            return False, "Vous avez déjà un adultère"
        
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

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
    
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        if not current_player.is_married():
            return False, "Vous devez être marié(e) pour avoir un enfant"
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

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
    
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

class AquisitionCard(Card):
    """carte a acheter avec de l'argent"""
    def __init__(self, cost: int, smiles: int, image_path: str):
        super().__init__(image_path)
        self.cost: int = cost
        self.smiles: int = smiles
        self.selection_event: Event = Event()
        self.salaries_use: list = []
        self.selection_confirmed: bool = False
        self.use_heritage: int = 0
    
    
    def __str__(self):
        return f" - smile : {self.smiles} - AquisitionCard"
    
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'aquisition',
            'cost': self.cost
        })
        return base
    
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        # Vérifier la somme totale des salaires
        total_salary_value = current_player.get_available_salary_sum()
        if total_salary_value < self.cost:
            return False, f"Vous avez besoin d'une somme de salaires de {self.cost}"
        
        return True, ""
    
    def confirm_salary_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.salaries_use = data.get('salary_ids', [])
        self.use_heritage = data.get('use_heritage', 0)
        self.selection_confirmed = True
        self.selection_event.set()  # Déclencher l'événement

    def discard_salary_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_confirmed = False
        self.selection_event.set()  # Déclencher l'événement

    
    def play_card(self, game: 'Game', current_player: 'Player'):
        # envois une demande d'afficher la sélection des salaires
        available_salaries = [c for c in current_player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
        print("[appel] : select_salaries_for_acquisition")
        emit('select_salaries_for_acquisition', {
            'card': self.to_dict(),
            'required_cost': self.cost,
            'available_salaries': [s.to_dict() for s in available_salaries],
            'heritage_available': current_player.heritage
        })
        # Attendre la réponse via l'événement
        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")

        # Vérifier si la sélection a été confirmée
        if self.selection_confirmed:
            # déplacer les cartes salaires séélectionnées
            selected_salaries = []
            for salary_id in self.salaries_use:
                for salary in current_player.played["vie professionnelle"]:
                    if isinstance(salary, SalaryCard) and salary.id == salary_id:
                        selected_salaries.append(salary)
                    
            for salary in selected_salaries:
                current_player.played["vie professionnelle"].remove(salary)
                current_player.played["salaire dépensé"].append(salary)

            # supprimer l'héritage si sélectionné
            if self.use_heritage > 0:
                current_player.heritage -= self.use_heritage

            super().play_card(game, current_player)

class HouseCard(AquisitionCard):
    """Carte maison"""
    def __init__(self, house_type: str, cost: int, smiles: int, image_path: str):
        super().__init__(cost, smiles, image_path)
        self.house_type: str = house_type

    
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
    
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        job = current_player.get_job()
        if job and job.power == 'house_free':
            return True, ""
        
        # Calculer le coût requis (divisé par 2 si marié)
        required_cost = self.cost
        if current_player.is_married():
            required_cost = required_cost // 2
        
        # Vérifier la somme totale des salaires
        total_salary_value = current_player.get_available_salary_sum()
        if total_salary_value < required_cost:
            return False, f"Vous avez besoin d'une somme de salaires de {required_cost}"
        
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        old_cost = self.cost
        if current_player.has_job() and "house_free" in current_player.get_job().power:
            self.cost = 0
            job = current_player.get_job()
            if isinstance(job, ArchitecteJob):
                job.use_power()
        if current_player.is_married():
            self.cost = self.cost // 2
        print(f"new price before placing: {self.cost}-{old_cost}")
        super().play_card(game, current_player)
        self.cost = old_cost
        print(f"new price after placing: {self.cost}-{old_cost}")
        

class TravelCard(AquisitionCard):
    """Carte voyage"""
    def __init__(self, image_path: str):
        super().__init__(3, 1, image_path)
    
    def __str__(self):
        return f"{self.cost} - smile : {self.smiles} - TravelCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'travel',
            'cost': self.cost
        })
        return base
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        job = current_player.get_job()
        if job and job.power == 'travel_free':
            return True, ""
        return super().can_be_played(current_player, game)
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        old_cost = self.cost
        if current_player.has_job() and "travel_free" in current_player.get_job().power:
            self.cost = 0
        super().play_card(game, current_player)
        self.cost = old_cost

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
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        # Logique spécifique selon le type
        return True, ""
    
    def apply_card_effect(self, game: 'Game', current_player: 'Player'):
        pass

    def play_card(self, game: 'Game', current_player: 'Player'):
        self.apply_card_effect(game, current_player)
        super().play_card(game, current_player)
        
class TrocCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("troc", image_path)
        self.smiles = 0
        self.selection_event: Event = Event()
        self.target_player_id: int = None
        self.target_player: Player = None
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    def confirm_player_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.target_player_id = data.get('target_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_player_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement

    def apply_card_effect(self, game, current_player):
        # Selection des cibles possibles
        players = [p.to_dict() for p in game.players if p != current_player]
        
        # affichage de la page
        emit('select_troc_target', {
            "card_id": self.id,
            'available_targets': players
        })

        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")
        
        self.target_player = game.players[self.target_player_id]

        # inversion de 2 cartes
        current_player.hand.remove(self)
        card_player1 = random.choice(current_player.hand)
        current_player.hand.append(self)
        card_player2 = random.choice(self.target_player.hand)

        current_player.hand.remove(card_player1)
        current_player.hand.append(card_player2)
        self.target_player.hand.remove(card_player2)
        self.target_player.hand.append(card_player1)
        print(f"Inversion des cartes {str(card_player1)} et {str(card_player2)}")
        
class TsunamiCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("tsunami", image_path)
        self.smiles = 0
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    def apply_card_effect(self, game, current_player):
        current_player.hand.remove(self)

        # récupération de toutes les cartes dans les mains des gens
        nb_cards_peer_player = []
        cards = []
        for player in game.players:
            nb_cards_peer_player.append(len(player.hand))
            cards.extend(player.hand)
        
        random.shuffle(cards)
        for idx, player in enumerate(game.players):
            new_hand = []
            for _ in range(nb_cards_peer_player[idx]):
                new_hand.append(cards.pop())
            player.hand = new_hand
        
        current_player.hand.append(self)

class HeritageCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("heritage", image_path)
        self.smiles = 0
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    def apply_card_effect(self, game, current_player):
        current_player.heritage += 3

class PistonCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("piston", image_path)
        self.smiles = 0
        self.selection_event: Event = Event()
        self.job_id: int = None
        self.job_card: Player = None
        
    
    def confirm_job_selection(self, data):
        """confirmation de la sélection du métier"""
        self.job_id = data.get('job_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_job_selection(self, data):
        """annulation de la sélection du métier"""
        self.selection_event.set()  # Déclencher l'événement
    
    def can_be_played(self, current_player, game):
        return not current_player.has_job(), ""
            
    def apply_card_effect(self, game, current_player):
        jobs_cards = [c for c in current_player.hand if isinstance(c, JobCard)]
        
        emit('select_piston_job', {
            "card_id" : self.id,
            'available_jobs': [j.to_dict() for j in jobs_cards]
        })

        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")

        for card in current_player.hand:
            if card.id == self.job_id:
                self.job_card: JobCard = card
                break

        self.job_card.play_card(game, current_player)
        
        pick_card = game.deck.pop()
        current_player.hand.append(pick_card)

class VengeanceCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("vengeance", image_path)
        self.smiles = 0
        self.selection_event: Event = Event()
        self.target_player_id: int = None
        self.target_player: Player = None
        self.hardship_id: int = None

    def confirm_vengeance_selection(self, data):
        """confirmation de la sélection de la cible"""
        self.target_player_id = int(data.get('target_id', None))
        self.hardship_id = data.get('hardship_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_vengeance_selection(self, data):
        """annulation de la sélection de la cible"""
        self.selection_event.set()  # Déclencher l'événement

    def can_be_played(self, current_player, game):
        for card in current_player.received_hardships:
            if card.can_be_played(current_player, game):
                return True, ""
        return False, "pas de cible disponibles ou pas de cartes recus"
    
    def apply_card_effect(self, game, current_player):
        received_hardships = [h.to_dict() for h in current_player.received_hardships if h.can_be_played(current_player, game)]
        other_players = [p.to_dict() for p in game.players if p != current_player]
        
        print("[APPEL] : select_vengeance")
        emit('select_vengeance', {
            'card_id' : self.id,
            'received_hardships': received_hardships,
            'available_targets': other_players
        })

        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")

        self.target_player = game.players[self.target_player_id]
        print(f"player target : {self.target_player.name} hardship_id = {self.hardship_id} \n {self.target_player.received_hardships}")
        self.hardship_card = None
        for card in current_player.received_hardships:
            if card.id == self.hardship_id:                
                current_player.received_hardships.remove(card)
                card.apply_effect(game, self.target_player, current_player)
                self.target_player.received_hardships.append(card)
                break
            
class ChanceCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("chance", image_path)
        self.smiles = 0
        self.next_cards: list[Card] = []
        self.selection_event: Event = Event()
        self.selected_card_id = None
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    
    def confirm_card_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.selected_card_id = data.get('selected_card_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_card_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement


    def apply_card_effect(self, game, current_player):
        for _ in range(min(3, len(game.deck))):
            self.next_cards.append(game.deck.pop())
        
        emit('select_chance_card', {
            'card_id': self.id,
            'cards': [c.to_dict() for c in self.next_cards]
        })
        
        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")

        print(self.selected_card_id, "in\n", self.next_cards)
        for card in self.next_cards:
            if card.id == self.selected_card_id:
                current_player.hand.append(card)
            else:
                game.discard.append(card)
        self.next_cards = []

class EtoileFilanteCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("etoile filante", image_path)
        self.smiles = 0
        self.selection_event: Event = Event()
        self.selected_card_id = None
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    def confirm_card_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.selected_card_id = data.get('selected_card_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_card_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement

    def apply_card_effect(self, game, current_player):
        
        emit('select_star_card', {
            "card_id": self.id,
            'discard_cards': [c.to_dict() for c in game.discard if c.can_be_played(current_player, game)[0]]
        })
        
        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")
        
        card = None
        for c in game.discard:
            if c.id == self.selected_card_id:
                card = c
                break

        game.discard.remove(card)
        current_player.hand.append(card)
        card.play_card(game, current_player)     
                
class CasinoCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("casino", image_path)
        self.smiles = 0
        self.selection_event: Event = Event()
        self.bet_card_id = None
        self.is_open = False
        self.first_player_bet: Player = None
        self.first_bet: SalaryCard = None

    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            "open": self.is_open,
            "first_bet": self.first_player_bet.to_dict() if self.first_bet else None,
            "second_bet": None
        })
        return base

    def confirm_bet_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.bet_card_id = data.get('bet_card_id', None)
        print(self.bet_card_id)
        self.selection_event.set()  # Déclencher l'événement

    def discard_bet_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement

    def bet_on_casino(self, game: 'Game', current_player: 'Player', is_opener=False):
        print("[start] : bet_on_casino")
        salary_cards = [s.to_dict() for s in current_player.hand if isinstance(s, SalaryCard)]
        
        emit('select_casino_bet', {
                'card_id': self.id,
                'available_salaries': salary_cards
            })
        
        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")

        if self.bet_card_id:
            print("il y a un choix de carte")
            card: SalaryCard = None
            for c in current_player.hand:
                if c.id == self.bet_card_id:
                    card = c
                    break
            print(f"la carte salaire a été retrouvée : {card}")

            if self.first_bet:
                print("c'est le deuxieme")
                current_player.hand.remove(card)
                if card.level == self.first_bet.level:
                    print("c'est le deuxieme qui gagne")
                    current_player.add_card_to_played(card)
                    current_player.add_card_to_played(self.first_bet)
                else:
                    print("c'est le premier qui gagne")
                    self.first_player_bet.add_card_to_played(card)
                    self.first_player_bet.add_card_to_played(self.first_bet)
                self.first_bet = None
                self.first_player_bet = None
            else:
                print("c'est le premier")
                current_player.hand.remove(card)
                self.first_bet = card
                self.first_player_bet = current_player
                if is_opener:
                    current_player.hand.append(game.deck.pop())
            game.broadcast_update()

    def apply_card_effect(self, game, current_player):
        self.bet_on_casino(game, current_player, True)

    def play_card(self, game: 'Game', current_player: 'Player'):
        self.is_open = True
        game.casino_card = self
        self.apply_card_effect(game, current_player)
        current_player.hand.remove(self) 
        
class AnniversaireCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("anniversaire", image_path)
        self.smiles = 0
        self.nb_player_to_give: int = 0
        self.selection_event: Event = Event()
        self.player_giver_id = None
        self.salary_id = None
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    

    def apply_card_effect(self, game, current_player):
        # Afficher la page d'attente au joueur qui joue la carte
        emit('show_birthday_waiting', {
            'card_id': self.id
        })
        
        # Initialiser le tracking des joueurs qui doivent donner
        self.waiting_for_players = {}
            
        for player in game.players:
            if player.id != current_player.id and player.connected:
                available_salaries = [c.to_dict() for c in player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
                if len(available_salaries) > 0:
                    self.nb_player_to_give += 1
                    print(f"card id : {self.id} apply_card_effect")
                    emit('select_birthday_gift', {
                        'card_id': self.id,
                        'birthday_player_name': current_player.name,
                        'available_salaries': available_salaries,
                        "player_id": player.id
                    }, room=player.session_id)
        
        # attendre que tous les joueurs ont donner
        while self.nb_player_to_give > 0:
            print("[EVENT] : Wait for selection")
            self.selection_event.wait()
            self.selection_event.clear()
            print("[EVENT] : trigger selection")
            self.nb_player_to_give -= 1
            player_giver: Player = game.players[self.player_giver_id]
            print(player_giver.name)
            for card in player_giver.played["vie professionnelle"]:
                if card.id == self.salary_id:
                    salary_card = card
                    game.players[self.player_giver_id].played["vie professionnelle"].remove(card)
                    break
            current_player.add_card_to_played(salary_card)

        emit('close_birthday_waiting', {
            'card_id': self.id
        })


    def give_salary_to_player(self, data):
        print("[START] : give_salary_to_player")
        self.salary_id = data.get('salary_id')
        self.player_giver_id = int(data.get('player_id'))
        self.selection_event.set()

class ArcEnCielCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("arc en ciel", image_path)
        self.smiles = 0
        self.nb_cards_played = 0
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            'count': 4 - self.nb_cards_played
        })
        return base
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    def apply_card_effect(self, game, current_player):
        game.arcEnCielMode = True
        game.arcEnCielCard = self

    def end_arc_en_ciel(self, game: 'Game', current_player: 'Player'):
        game.arcEnCielMode = False
        for _ in range(1, self.nb_cards_played):
            current_player.hand.append(game.deck.pop())

    def add_card_played(self, game: 'Game', current_player: 'Player'):
        self.nb_cards_played += 1
        if self.nb_cards_played >= 4:
            self.end_arc_en_ciel(game, current_player)    




class HardshipCard(Card):
    """Carte coup dur"""
    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.smiles = 0
        self.selection_event: Event = Event()
        self.target_player: Player = None
        self.target_player_id: int = None

    def __str__(self):
        return f"smile : {self.smiles} - HardshipCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'type': 'hardship'
        })
        return base

    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        # Les coups durs sont joués sur d'autres joueurs
        targets = self.get_available_targets(game, current_player)
        for t in targets:
            if not t["immune"]:
                return True, ""            
        return False, "Pas de cible possible"
    
    def confirm_target_selection(self, data):
        """confirmation de la sélection des salaires"""
        print("[appel] : confirm_target_selection")
        self.target_player_id = data.get('target_player_id')
        self.selection_event.set()  # Déclencher l'événement

    def discard_target_selection(self, data):
        """annulation de la sélection des salaires"""
        print("[appel] : discard_target_selection")
        self.target_player = None
        self.target_player_id = None
        self.selection_event.set()  # Déclencher l'événement
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        return False
    
    def get_available_targets(self, game: 'Game', current_player: 'Player') -> list[dict]:
        targets = []
        for player in game.players:
            values = player.to_dict()
            values["immune"] = False
            if player == current_player:
                values["immune"] = True
            if self.other_rules(game, current_player, player):
                values["immune"] = True
            targets.append(values)
        return targets

    def play_card(self, game: 'Game', current_player: 'Player'):
        # selection de la cible
        targets = self.get_available_targets(game, current_player)
        
        print("[appel] : select_hardship_target")
        emit('select_hardship_target', {
            'card': self.to_dict(),
            'available_targets': targets
        })
        
        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()
        print("[EVENT] : trigger selection")
        self.target_player = game.players[self.target_player_id]
        print(self.target_player.name)

        if self.target_player:
            self.apply_effect(game, self.target_player, current_player)            
            current_player.hand.remove(self)
            self.target_player.add_card_to_played(self)
            print("targetplayer pass")

    def apply_effect(self, game: 'Game', target_player: 'Player', current_player: 'Player'):
        print("apply_effect_hardhipCard")

class TaxCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"TaxCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'TAX'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        # si il possède pas de métier
        if not player.has_job():
            print(f"[DEBUG] : {player.name} pas de métier")
            return True
        # si le métier n'est pas imunisé au tax
        if "no_tax" in player.get_job().power:
            print(f"[DEBUG] : {player.name} un pouvoir no_tax")
            return True
        # si il a pas de salaires
        if player.get_available_salary_sum() == 0:
            print(f"[DEBUG] : {player.name} pas de salaire")
            return True
        print(f"[DEBUG] : {player.name} ne peux pas recevoir de taxe")
        return False

    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        print("apply_effect_Tax")
        salary_cards = [c for c in target_player.played["vie professionnelle"] if isinstance(c, SalaryCard)]
        card_to_remove = salary_cards[-1]
        target_player.remove_card_from_played(card_to_remove)
        game.discard.append(card_to_remove)

class MaladieCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"MaladieCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'Maladie'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        return player.has_job() and "no_maladie" in player.get_job().power
             
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        print("apply_effect_maladie")
        target_player.skip_turns += 1

class AccidentCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"AccidentCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'Accident'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        return player.has_job() and "no_accident" in player.get_job().power

    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        print("apply_effect accident")
        target_player.skip_turns += 1

class AttentatCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"AttentatCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'Attentat'
        })
        return base
    
    def can_be_played(self, current_player, game):
        for player in game.players:
            if player.has_job() and "no_attentat" in player.get_job().power:
                return False, ""
        return True, ""
    
    def get_available_targets(self, game: 'Game', current_player: 'Player') -> list[dict]:
        targets = []
        for player in game.players:
            values = player.to_dict()
            values["immune"] = False
            targets.append(values)
        return targets

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        for player in game.players:
            for card in player.played["vie personnelle"]:
                if isinstance(card, ChildCard):
                    player.remove_card_from_played(card)
                    game.discard.append(card)      

class DivorceCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"DivorceCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'Divorce'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        if not player.is_married():
            return True
        if player.has_job() and "no_divorce" in player.get_job().power:
            return True
        return False

    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        # si le joueur a un adultaire
        cards_played = tuple(target_player.played["vie personnelle"])
        if target_player.has_adultery():
            # jette tous les enfants
            for card in cards_played:
                print(f"[DEBUG] : card {card}")
                if isinstance(card, (AdulteryCard, MarriageCard, ChildCard)):
                    target_player.remove_card_from_played(card)
                    game.discard.append(card)
        else:
            for card in cards_played:
                if isinstance(card, MarriageCard):
                    target_player.remove_card_from_played(card)
                    game.discard.append(card)

class BurnOutCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"BurnOutCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'BurnOut'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        return not player.has_job()
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        target_player.skip_turns += 1

class RedoublementCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"RedoublementCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'Redoublement'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        if player.has_job():
            return True
        nb_study = len([c for c in player.played["vie professionnelle"] if isinstance(c, StudyCard)])
        if nb_study == 0:
            return True
        return False
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        print("apply effect redoublement")
        study_cards = [c for c in target_player.played["vie professionnelle"] if isinstance(c, StudyCard)]
        card_to_remove = study_cards[-1]
        target_player.remove_card_from_played(card_to_remove)
        game.discard.append(card_to_remove)
        
class PrisonCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"PrisonCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'Prison'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        return not (player.has_job() and player.get_job().job_name == "bandit")

    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        nb_card_removes = 2 # parametre, nombre de carte supprimée
        target_player.skip_turns += 3
        # perdre X cartes
        for _ in range(nb_card_removes):
            discard_card = random.choice(target_player.hand)
            target_player.hand.remove(discard_card)
            game.discard.append(discard_card)
        for _ in range(nb_card_removes):
            pick_card = game.deck.pop()
            target_player.hand.append(pick_card)
        # perte du métier
        job = target_player.get_job()
        target_player.remove_card_from_played(job)
        game.discard.append(job)

class LicenciementCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"LicenciementCard"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'Licenciement'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        if not player.has_job():
            return True
        if "no_fire" in player.get_job().power:
            return True
        if player.get_job().status == "fonctionnaire":
            return True
        return False

    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        job_card = target_player.get_job() 
        job_card.discard_play_card(game, target_player)



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
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        if self.card_type == 'prix':
            job = current_player.get_job()
            if not job:
                return False, "Vous devez avoir un métier"
            if job.power not in ['prix_possible', 'see_hands_prix_possible']:
                return False, "Votre métier ne permet pas de recevoir un prix"
        
        return True, ""
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)
    
class LegionCard(OtherCard):
    """Carte légion d'honneur"""
    def __init__(self, smiles: int, image_path: str):
        super().__init__("legion", smiles, image_path)

    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        if current_player.has_been_bandit:
            return False, "Vous avez été bandit dans la partie"
        return True, ""
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

class PriceCard(OtherCard):
    """Carte prix d'excellence"""
    def __init__(self, smiles: int, image_path: str):
        super().__init__('prix', smiles, image_path)
        self.job_link = None
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        print("tentative de link de Prix", end=" ")
        job = current_player.get_job()
        if not job:
            return False, "Vous devez avoir un métier"
        if "prix_possible" not in job.power:
            return False, "Votre métier ne permet pas de recevoir un prix"
        self.job_link = job.id
        print("le link est : ", self.job_link)

        return True, ""
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)







class JobCard(Card):
    """Carte métier"""
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(image_path)
        self.job_name = job_name
        self.salary = salary
        self.studies = studies
        self.status = ""
        self.power = ""
        self.smiles = 2
    
    
    def __str__(self):
        return f"{self.job_name} - smile : {self.smiles} - JobCard"
    
    def discard_play_card(self, game: 'Game', effected_player: 'Player'):
        effected_player.remove_card_from_played(self)
        game.discard.append(self)
        self.loosing_continuous_power(game, effected_player)
        if effected_player.id == game.current_player and self.status != "intérimaire":
            game.next_player()
    
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
    
    
    def can_be_played(self, player: 'Player', game: 'Game') -> tuple[bool, str]:
        # Vérifier si le joueur a déjà un métier
        if player.has_job():
            print(f"debug : {game.to_dict()}")
            return False, "Vous avez déjà un métier"
        
        # Vérifier si le joueur a les études nécessaires
        if isinstance(self.studies, int) and self.studies > 0:
            if player.count_studies() < self.studies:
                return False, f"Vous avez besoin de {self.studies} études"
        
        return True, ""
    
    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        pass

    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        pass

    def play_card(self, game: 'Game', current_player: 'Player'):
        self.apply_instant_power(game, current_player)
        super().play_card(game, current_player)


class ChercheurJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "prix_possible"

    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        current_player.hand.append(game.deck.pop())

    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        card = random.choice(effected_player.hand)
        print(f"carte perdu : {card}")
        effected_player.hand.remove(card)
        game.discard.append(card)

class AstronauteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
        self.selection_event: Event = Event()
        self.selected_card_id = None

    
    def confirm_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.selected_card_id = data.get('selected_card_id')
        self.selection_event.set()  # Déclencher l'événement

    def discard_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement



    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        current_player.add_card_to_played(self)
        available_cards = [c for c in game.discard if c.can_be_played(current_player, game)[0]]
        current_player.remove_card_from_played(self)

        emit('select_astronaute_card', {
        'card_id' : self.id,
        'cards': [c.to_dict() for c in available_cards]
        })

        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")
        
        if not self.selected_card_id:
            return

        card = None
        for c in game.discard:
            if c.id == self.selected_card_id:
                card = c
                break

        game.discard.remove(card)
        current_player.hand.append(card)
        card.play_card(game, current_player)    



    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        pass
   
class BanditJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_tax__no_fire"

    def can_be_played(self, current_player: 'Player', game: 'Game'):
        for player in game.players:
            if player.has_job() and "no_bandit" in player.get_job().power:
                return False, "il y a un job qui empeche le bandit"
        return super().can_be_played(current_player, game)

    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        current_player.has_been_bandit = True

    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        pass
   
class MediumJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
        self.selection_event: Event = Event()
    
    def confirm_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement


    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        next_cards = []
        for i in range(1, 1+min(13, len(game.deck))):
            next_cards.append(game.deck[-i])
        
        emit('medium_show_cards', {
            'card_id': self.id,
            'cards': [c.to_dict() for c in next_cards],
            'total': len(game.deck)
        })

        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  
        print("[EVENT] : trigger selection")

    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        pass
   
class JournalisteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "prix_possible"
        self.selection_event: Event = Event()
    
    def confirm_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement


    def apply_instant_power(self, game: 'Game', current_player: 'Player'):    
        hands_info = {}
        for p in game.players:
            if p.connected and p.id != current_player.id:
                hands_info[p.name] = [c.to_dict() for c in p.hand]
        
        emit('show_all_hands', {
            "card_id": self.id,
            'hands': hands_info
        })

        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  
        print("[EVENT] : trigger selection")

    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        pass
   
class ChefDesAchatsJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
        self.selection_event: Event = Event()
        self.selected_card_id = None

    
    def confirm_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.selected_card_id = data.get('acquisition_id')
        self.selection_event.set()  # Déclencher l'événement

    def discard_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement

    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        available_acquisitions = [c for c in game.discard if isinstance(c, AquisitionCard) and c.can_be_played(current_player, game)[0]]

        emit('select_chef_achats_acquisition', {
            "card_id": self.id,
            'acquisitions': [a.to_dict() for a in available_acquisitions]
        })

        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")
        if not self.selected_card_id:
            return
        
        for card in game.discard:
            if card.id == self.selected_card_id:
                current_player.hand.append(card)
                game.discard.remove(card)
                card.play_card(game, current_player)

    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        pass
   
class ChefDesVentesJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
        self.selection_event: Event = Event()
        self.selected_card_id = None

    
    def confirm_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.selected_card_id = data.get('selected_card_id')
        self.selection_event.set()  # Déclencher l'événement

    def discard_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement

    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        available_salaries = [c for c in game.discard if isinstance(c, SalaryCard) and c.level <= 3]
        
        emit('select_chef_ventes_salary', {
            "card_id": self.id,
            'salaries': [s.to_dict() for s in available_salaries]
        })

        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")
        if not self.selected_card_id:
            return
        
        for card in game.discard:
            if card.id == self.selected_card_id:
                current_player.add_card_to_played(card)
                game.discard.remove(card)
                break


    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        pass

class ProfJob(JobCard):   
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "fonctionnaire"
        self.power = ""

class GrandProfJob(JobCard):
    def __init__(self, job_name: str, salary: int, image_path: str):
        super().__init__(job_name, salary, 0, image_path)
        self.status = "fonctionnaire"
        self.power = ""

    def can_be_played(self, player, game):
        if player.has_job() and isinstance(player.get_job(), ProfJob):
            return True, ""
        return False, "Vous devez être professeur pour devenir grand prof"

    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        job = current_player.get_job()
        current_player.remove_card_from_played(job)
        game.discard.append(job)

class GourouJob(JobCard):
    def __init__(self, job_name, salary, studies, image_path):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
    
    def can_be_played(self, player, game):
        for player in game.players:
            if player.has_job() and "no_gourou" in player.get_job().power:
                return False, "il y a un job qui empeche le bandit"
        return super().can_be_played(player, game)

class PolicierJob(JobCard):
    def __init__(self, job_name, salary, studies, image_path):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "fonctionnaire"
        self.power = "no_bandit__no_gourou"
    
    def apply_instant_power(self, game, current_player):
        for player in game.players:
            if player.has_job() and isinstance(player.get_job(), (GourouJob, BanditJob)):
                player.get_job().discard_play_card(game, player)

class ArchitecteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "house_free"
    
    def use_power(self):
        self.power = ""

    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        self.power = "house_free"

class AvocatJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_divorce"

class BarmanJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = "unlimited_flirt"

class ChirurgienJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_illness__extra_study"

class DesignerJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "fonctionnaire"
        self.power = "no_bandit__no_gourou"

class GaragisteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""

class JardinierJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""

class MedecinJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_maladie__extra_study"

class MilitaireJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "fonctionnaire"
        self.power = "no_bandit__no_gourou"

class PharmacienJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_maladie"

class PiloteDeLigneJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "travel_free"

class PizzaioloJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""

class PlombierJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = ""

class ServeurJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = ""

class StripTeaserJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = ""

class EcrivainJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "prix_possible"


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
        self.received_hardships: list[HardshipCard] = []
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
        elif isinstance(card, (HardshipCard)):
            self.received_hardships.append(card)
        
    
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
        print(f"[DEBUG] : {self.played}, {self.name}\n\n")
        return any(isinstance(card, AdulteryCard) for card in self.played["vie personnelle"])
    
    def get_job(self) -> JobCard:
        for card in self.played["vie professionnelle"]:
            if isinstance(card, JobCard):
                return card
        return None
    
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
            'received_hardships': [
                card.to_dict().get('subtype', 'malus') if hasattr(card, 'to_dict') else str(card)
                for card in self.received_hardships
            ],
            'connected': self.connected
        }

class Game:
    """classe qui gere une partie"""
    def __init__(self, game_id: str, deck: list[Card], num_players: int):
        self.id: str = game_id
        
        self.players: list[Player] = []
        for i in range(num_players):
            player = Player(i, 'En attente...')
            player.connected = False
            self.players.append(player)
        
        self.num_players: int = num_players
        self.deck: list[Card] = deck
        self.discard: list[Card] = []
        self.last_discard = None
        self.current_player: int = 0
        self.phase: str = "waiting"
        self.players_joined: int = 0
        self.host_id: int = 0
        self.casino_card: CasinoCard = None
        self.pending_hardship = None
        self.arcEnCielMode = False
        self.arcEnCielCard: ArcEnCielCard = None


    def add_player(self, player: Player):
        """Ajoute un joueur à la partie"""
        if isinstance(player, Player):
            self.players[self.players_joined] = player
            if player.connected:
                self.players_joined += 1

    def next_player(self):
        self.change_current_player()
        self.phase = "draw"

    def change_current_player(self):
        """Change le joueur qui joue en passant automatiquement les joueurs déconnectés"""
        self.current_player = (self.current_player + 1) % self.num_players
        
        attempts = 0
        while not self.players[self.current_player].connected and attempts < self.num_players:
            self.current_player = (self.current_player + 1) % self.num_players
            attempts += 1

    def to_dict(self):
        """Retourne une représentation dict complète du jeu"""
        return {
            "id": self.id,
            "players": [p.to_dict() for p in self.players],
            "deck": [c.to_dict() for c in self.deck],
            "discard": [c.to_dict() for c in self.discard],
            "current_player": self.current_player,
            "phase": self.phase,
            "last_discard": self.last_discard,
            "num_players": self.num_players,
            "players_joined": self.players_joined,
            "host_id": self.host_id,
            "casino": self.casino_card.to_dict() if self.casino_card else {"open": False},
            "pending_hardship": self.pending_hardship,
            "arc_en_ciel": self.arcEnCielMode,
            "arc_en_ciel_card": self.arcEnCielCard.to_dict() if self.arcEnCielCard else {}    
        }

    def broadcast_update(self, message: str = ""):
        """
        Envoie une mise à jour à tous les joueurs connectés
        
        Args:
            message: Message optionnel à afficher aux joueurs
            socketio: Instance de SocketIO pour l'émission (doit être passée depuis l'extérieur)
        """            
        from constants import get_game_state_for_player, socketio
        
        print(f"[start]: Game.broadcast_update - message: '{message}'")
        
        for player in self.players:
            if player.connected:
                print(f"[broadcast] Sending update to player {player.id} ({player.name})")
                socketio.emit('game_updated', {
                    'game': get_game_state_for_player(self, player.id),
                    'message': message
                }, room=player.session_id)

class CardFactory:
    """Factory pour créer les cartes"""

    
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
        
        
        
        # Etudes
        for _ in range(0):
            deck.append(StudyCard('double', 2, "personnal_life/professionnal_life/StudyCards/study2.png"))
        
        # Salaires
        
        for level in range(3, 5):
            for _ in range(0):
                deck.append(SalaryCard(level, f"personnal_life/professionnal_life/SalaryCards/salary{level}.png"))
        
        # Maisons
        
        deck.append(HouseCard('petite', 6, 1, "aquisition_cards/houses/maison1.png"))
        deck.append(HouseCard('petite', 6, 1, "aquisition_cards/houses/maison1.png"))
        deck.append(HouseCard('moyenne', 8, 2, "aquisition_cards/houses/maison2.png"))
        deck.append(HouseCard('moyenne', 8, 2, "aquisition_cards/houses/maison2.png"))
        deck.append(HouseCard('grande', 10, 3, "aquisition_cards/houses/maison3.png"))
        
        # Voyages
        
        for trip_name in range(0):
            t = cls.TRIP_NAMES[0].replace(" ", "_")
            deck.append(TravelCard(f"aquisition_cards/trip/{t}.png"))

        # Flirts
        
        for loc in range(5):
            l = cls.FLIRT_LOCATIONS[0].replace(" ", "_")
            deck.append(FlirtCard(l, f"personnal_life/flirts/{l}.png"))

        
        # Mariages
        
        for loc in range(5):
            l = cls.MARRIAGE_LOCATIONS[0].replace(" ", "_").replace("-", "_")
            deck.append(MarriageCard(l, f"personnal_life/mariages/mariage_{l}.png"))
        
        # Adultères
        for _ in range(3):
            deck.append(AdulteryCard("personnal_life/mariages/adultere.png"))
        
        # Enfants
        
        for name in range(5):
            deck.append(ChildCard(cls.CHILDREN_NAMES[0], f"personnal_life/children/{cls.CHILDREN_NAMES[0]}.png"))
        
         # Cartes spéciales

        # deck.append(TrocCard("special_cards/troc.png"))
        # deck.append(TsunamiCard("special_cards/tsunami.png"))
        # deck.append(HeritageCard("special_cards/heritage.png"))
        # deck.append(PistonCard("special_cards/piston.png"))
        # deck.append(AnniversaireCard("special_cards/anniversaire.png"))
        # deck.append(CasinoCard("special_cards/casino.png"))
        # deck.append(ChanceCard("special_cards/chance.png"))
        # deck.append(EtoileFilanteCard("special_cards/etoile_filante.png"))
        # deck.append(VengeanceCard("special_cards/vengeance.png"))
        # deck.append(ArcEnCielCard("special_cards/arc_en_ciel.png"))

        deck.append(ChanceCard("special_cards/chance.png"))
        deck.append(ChanceCard("special_cards/chance.png"))
        deck.append(ChanceCard("special_cards/chance.png"))
        deck.append(ChanceCard("special_cards/chance.png"))
        deck.append(ChanceCard("special_cards/chance.png"))
        deck.append(ChanceCard("special_cards/chance.png"))




        # cartes d'attaques

        for _ in range(10):
            # deck.append(AccidentCard("hardship_cards/accident.png"))
            # deck.append(BurnOutCard("hardship_cards/burnout.png"))
            deck.append(DivorceCard("hardship_cards/divorce.png"))
            # deck.append(TaxCard("hardship_cards/tax.png"))
            # deck.append(LicenciementCard("hardship_cards/licenciement.png"))
            # deck.append(MaladieCard("hardship_cards/maladie.png"))
            # deck.append(RedoublementCard("hardship_cards/redoublement.png"))
        
        deck.append(PrisonCard("hardship_cards/prison.png"))
        deck.append(AttentatCard("hardship_cards/attentat.png"))
        
        
        

        return deck
    
    @classmethod
    def create_deck(cls) -> List[Card]:
        """Crée un deck complet de cartes"""
        #########################
        # return cls.test_create_deck(cls)
        # TESTING
        #########################
        
        deck = []
        
        # Métiers
        deck.append(ArchitecteJob("architecte", 3, 4, "personnal_life/professionnal_life/JobCards/architecte.png"))
        deck.append(AstronauteJob("astronaute", 4, 6, "personnal_life/professionnal_life/JobCards/astronaute.png"))
        deck.append(AvocatJob("avocat", 3, 4, "personnal_life/professionnal_life/JobCards/avocat.png"))
        deck.append(BanditJob("bandit", 4, 0, "personnal_life/professionnal_life/JobCards/bandit.png"))
        deck.append(BarmanJob("barman", 1, 0, "personnal_life/professionnal_life/JobCards/barman.png"))
        deck.append(ChefDesVentesJob("chef des ventes", 3, 3, "personnal_life/professionnal_life/JobCards/chef_des_ventes.png"))
        deck.append(ChefDesAchatsJob("chef des achats", 3, 3, "personnal_life/professionnal_life/JobCards/chef_des_achats.png"))
        deck.append(ChercheurJob("chercheur", 2, 6, "personnal_life/professionnal_life/JobCards/chercheur.png"))
        deck.append(ChirurgienJob("chirurgien", 4, 6, "personnal_life/professionnal_life/JobCards/chirurgien.png"))
        deck.append(DesignerJob("designer", 3, 4, "personnal_life/professionnal_life/JobCards/designer.png"))
        deck.append(EcrivainJob("ecrivain", 1, 0, "personnal_life/professionnal_life/JobCards/ecrivain.png"))
        deck.append(GaragisteJob("garagiste", 2, 1, "personnal_life/professionnal_life/JobCards/garagiste.png"))
        deck.append(GourouJob("gourou", 3, 0, "personnal_life/professionnal_life/JobCards/gourou.png"))
        deck.append(JardinierJob("jardinier", 1, 1, "personnal_life/professionnal_life/JobCards/jardinier.png"))
        deck.append(JournalisteJob("journaliste", 2, 3, "personnal_life/professionnal_life/JobCards/journaliste.png"))
        deck.append(MedecinJob("médecin", 4, 6, "personnal_life/professionnal_life/JobCards/medecin.png"))
        deck.append(MediumJob("médium", 1, 0, "personnal_life/professionnal_life/JobCards/medium.png"))
        deck.append(MilitaireJob("militaire", 1, 0, "personnal_life/professionnal_life/JobCards/militaire.png"))
        deck.append(PharmacienJob("pharmacien", 3, 5, "personnal_life/professionnal_life/JobCards/pharmacien.png"))
        deck.append(PiloteDeLigneJob("pilote de ligne", 4, 5, "personnal_life/professionnal_life/JobCards/pilote_de_ligne.png"))
        deck.append(PizzaioloJob("pizzaiolo", 2, 0, "personnal_life/professionnal_life/JobCards/pizzaiolo.png"))
        deck.append(PlombierJob("plombier", 1, 1, "personnal_life/professionnal_life/JobCards/plombier.png"))
        deck.append(PolicierJob("policier", 1, 1, "personnal_life/professionnal_life/JobCards/policier.png"))
        deck.append(ProfJob("prof anglais", 2, 2, "personnal_life/professionnal_life/JobCards/prof_anglais.png"))
        deck.append(ProfJob("prof francais", 2, 2, "personnal_life/professionnal_life/JobCards/prof_francais.png"))
        deck.append(ProfJob("prof histoire", 2, 2, "personnal_life/professionnal_life/JobCards/prof_histoire.png"))
        deck.append(ProfJob("prof maths", 2, 2, "personnal_life/professionnal_life/JobCards/prof_maths.png"))
        deck.append(ServeurJob("serveur", 1, 0, "personnal_life/professionnal_life/JobCards/serveur.png"))
        deck.append(StripTeaserJob("stripteaser", 1, 0, "personnal_life/professionnal_life/JobCards/stripteaser.png"))
        deck.append(GrandProfJob("grand prof", 3, "personnal_life/professionnal_life/JobCards/grand_prof.png"))


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
        deck.append(TrocCard("special_cards/troc.png"))
        deck.append(TsunamiCard("special_cards/tsunami.png"))
        deck.append(HeritageCard("special_cards/heritage.png"))
        deck.append(PistonCard("special_cards/piston.png"))
        deck.append(AnniversaireCard("special_cards/anniversaire.png"))
        deck.append(CasinoCard("special_cards/casino.png"))
        deck.append(ChanceCard("special_cards/chance.png"))
        deck.append(EtoileFilanteCard("special_cards/etoile_filante.png"))
        deck.append(VengeanceCard("special_cards/vengeance.png"))
        deck.append(ArcEnCielCard("special_cards/arc_en_ciel.png"))
        
        # Coups durs
        for _ in range(5):
            deck.append(AccidentCard("hardship_cards/accident.png"))
            deck.append(BurnOutCard("hardship_cards/burnout.png"))
            deck.append(DivorceCard("hardship_cards/divorce.png"))
            deck.append(TaxCard("hardship_cards/tax.png"))
            deck.append(LicenciementCard("hardship_cards/licenciement.png"))
            deck.append(MaladieCard("hardship_cards/maladie.png"))
            deck.append(RedoublementCard("hardship_cards/redoublement.png"))
        
        deck.append(PrisonCard("hardship_cards/prison.png"))
        deck.append(AttentatCard("hardship_cards/attentat.png"))
        
        
        # Autres
        deck.append(LegionCard(3, "personnal_life/professionnal_life/legion.png"))
        deck.append(PriceCard(4, "personnal_life/professionnal_life/price.png"))
        deck.append(PriceCard(4, "personnal_life/professionnal_life/price.png"))
        
        return deck
    