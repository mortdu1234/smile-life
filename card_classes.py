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
            'image': self.image,
            'rule' : self.get_card_rule()
        }
    
    @abstractmethod
    def can_be_played(self, player: 'Player', game: 'Game') -> tuple[bool, str]:
        print("[WARNING] cette méthode ne devrait pas etre appellée")
        
        return True, ""
    
    def apply_card_effect(self, game: 'Game', current_player: 'Player'):
        pass
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        """pose la carte"""
        self.apply_card_effect(game, current_player)
        print("pose la carte")
        current_player.hand.remove(self)
        current_player.add_card_to_played(self)

    def get_card_rule(self):
        return "Nous avons une carte classique\n" \
        + f"il donne {self.smiles} smiles\n" 

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
    
    def get_card_rule(self):
        return "Nous avons une carte d'étude\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il s'agit d'une etdue {self.study_type} elle donne {self.levels} niveaux d'étude\n" \
        + "\nREGLES\n" \
        + "- il est possible de jouer cette carte que quand on n'a pas de métier\n" \
        + "- permet d'avoir un métier meilleur\n" \
        + "- il est interdit d'avoir plus de 6 cartes études de poser au total (sauf cas spécial)"
    
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte salaire\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il s'agit d'un salaire qui donne {self.level} liasse\n" \
        + "\nREGLES\n" \
        + "- il est possible de jouer cette carte après avoir un métier\n" \
        + "- il est possible de jouer cette carte au casino s'il est ouvert\n" \
        + "- permet d'acheter des acquisitions\n"
    
    
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
    
    
    def get_card_rule(self):
        return "Nous avons une carte flirt\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il s'agit du flirt dans {self.location}\n" \
        + "\nREGLES\n" \
        + "- il est possible de jouer cette carte tout le temps, sauf pendant un mariage\n" \
        + "- on a pas le droit d'avoir plus de 5 flirt sans marriage\n" \
        + "- si un joueur a en dernière carte un flirt de meme location que celui que vous poser, alors vous lui voler son flirt, ce vole peut dépasser la limite de flirt\n" \
        + "- permet de se marier\n"
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        # Peut flirter si pas marié OU si on a un adultère
        if current_player.is_married() and not current_player.has_adultery():
            return False, "Vous êtes marié(e) sans adultère"
        return True, ""
    
    def steal_same_card(self, game: 'Game', current_player: 'Player'):
        for player in game.players:
            if player == current_player:
                continue
            played_cards = player.played["vie personnelle"]
            idx = len(played_cards)-1
            while idx >= 0:
                card = played_cards[idx]
                if isinstance(card, MarriageCard):
                    idx = -1
                if isinstance(card, FlirtCard):
                    idx = -1
                    if card.location == self.location:
                        print("[INFO] : Vole de carte flirt")
                        player.remove_card_from_played(card)
                        current_player.add_card_to_played(card)
                idx -= 1

    def play_card(self, game: 'Game', current_player: 'Player'):
        self.steal_same_card(game, current_player)
        super().play_card(game, current_player)

class FlirtWithChildCard(FlirtCard):
    def __init__(self, location: str, image_path: str):
        super().__init__(location, image_path)
        self.child_link: ChildCard = None

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
    

    def get_card_rule(self):
        return "Nous avons une carte marriage\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il s'agit du marriage dans la ville de {self.location}\n" \
        + "\nREGLES\n" \
        + "- il faut avoir au moins 1 flirt avant de pouvoir se marier\n" \
        + "- il n'est pas possible d'avoir 2 marriage fois en meme temps sur le meme joueur\n" \
        + "- vous pouvez divorcer à n'importe quel tour, pour cela il suffit de ne pas piocher au début du tour et de défausser son marriage\n" \
        + "- permet de poser des enfants\n" \
        + "- permet de poser un adultaire\n"

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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Adultaire\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- il faut avoir au moins 1 marriage avant de pouvoir faire un adultaire\n" \
        + "- il n'est pas possible d'avoir 2 adultaire fois en meme temps sur le meme joueur\n" \
        + "- vous pouvez annuler votre adultaire à n'importe quel tour, pour cela il suffit de ne pas piocher au début du tour et de défausser son adultaire\n" \
        + "- permet de poser des flirts en dépassant la limite des flirts\n" \
        + "- attention en cas de divorce, vous perdrez, votre marriage, vos enfants et votre adultaire\n"
    
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
    def __init__(self, name: str, sexe: str, image_path: str):
        super().__init__(image_path)
        self.name = name
        self.sexe = sexe
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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Enfant\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"l'enfant s'appelle : {self.name}\n" \
        + "\nREGLES\n" \
        + "- il faut avoir au moins 1 marriage avant de pouvoir poser un enfant\n"
    

    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        last_flirt = current_player.get_last_flirt()
        if isinstance(last_flirt, FlirtWithChildCard) and last_flirt.child_link is None:
            return True, ""
        if not current_player.is_married():
            return False, "Vous devez être marié(e) pour avoir un enfant"
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        last_flirt = current_player.get_last_flirt()
        if isinstance(last_flirt, FlirtWithChildCard) and last_flirt.child_link is None:
            last_flirt.child_link = self
        super().play_card(game, current_player)
class AngelaChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "GirlPower", image_path)

class BeatrixChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Female", image_path)

class DaenerysChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Female", image_path)
        self.selection_event: Event = Event()
        self.target_card_id: int = None
        self.target_card: Card = None
    
    def confirm_player_selection(self, data):
        """confirmation de la carte a détruire"""
        self.target_card_id = data.get('target_card_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_player_selection(self, data):
        """annulation de la carte a détruire"""
        self.selection_event.set()  # Déclencher l'événement

    def apply_card_effect(self, game, current_player):
        if any(isinstance(c, DragonAnimal) for c in current_player.get_all_played_cards()):
            for player in game.players:
                if player != current_player:
                    played_cards: list[Card] = player.get_all_played_cards()
                    emit('select_burn_card', {
                        "card_id": self.id,
                        'player_name': player.name,
                        'available_targets': [c.to_dict() for c in played_cards] 
                    })

                    print("[EVENT] : Wait for selection")
                    self.selection_event.wait()
                    self.selection_event.clear()  # Réinitialiser l'événement
                    print("[EVENT] : trigger selection")
                    
                    if self.target_card_id:
                        self.target_card = player.get_played_card_by_id(self.target_card_id) 
                        player.remove_card_from_played(self.target_card)

class DianaChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Female", image_path)

class HarryChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Male", image_path)

class HermioneChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Female", image_path)

class LaraChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Female", image_path)

class LeiaChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Female", image_path)

class LouiseChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "GirlPower", image_path)

class LuigiChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Male", image_path)

class MarioChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Male", image_path)

class LukeChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Male", image_path)

class OlympeChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "GirlPower", image_path)

class RockyChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Male", image_path)

class SimoneChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "GirlPower", image_path)

class ZeldaChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, "Female", image_path)






class BeatrixChild(ChildCard):
    def __init__(self, name: str, image_path: str):
        super().__init__(name, image_path)

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
    
    def get_card_rule(self):
        return "Nous avons une carte Animal\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"l'animal est un : {self.animal_name}\n" \
        + "\nREGLES\n" \
        + "- possibilité de jouer la carte a tout moment\n"
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        return True, ""
    
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)



class LicorneAnimal(AnimalCard):
    def __init__(self, animal_name: str, smiles: int, image_path: str):
        super().__init__(animal_name, smiles, image_path)

class DragonAnimal(AnimalCard):
    def __init__(self, animal_name: str, smiles: int, image_path: str):
        super().__init__(animal_name, smiles, image_path)
        self.selection_event: Event = Event()
        self.target_card_id: int = None
        self.target_card: Card = None
    
    def confirm_player_selection(self, data):
        """confirmation de la carte a détruire"""
        self.target_card_id = data.get('target_card_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_player_selection(self, data):
        """annulation de la carte a détruire"""
        self.selection_event.set()  # Déclencher l'événement

    def apply_card_effect(self, game, current_player):
        if any(isinstance(c, DaenerysChild) for c in current_player.get_all_played_cards()):
            for player in game.players:
                if player != current_player:
                    played_cards: list[Card] = player.get_all_played_cards()
                    emit('select_burn_card', {
                        "card_id": self.id,
                        'player_name': player.name,
                        'available_targets': [c.to_dict() for c in played_cards] 
                    })

                    print("[EVENT] : Wait for selection")
                    self.selection_event.wait()
                    self.selection_event.clear()  # Réinitialiser l'événement
                    print("[EVENT] : trigger selection")
                    
                    if self.target_card_id:
                        self.target_card = player.get_played_card_by_id(self.target_card_id) 
                        player.remove_card_from_played(self.target_card)










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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Aquisition\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il coute : {self.cost} liasse de salaire\n" \
        + "\nREGLES\n" \
        + "\n"
    
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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Maison\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il coute : {self.cost} liasse de salaire\n" \
        + "\nREGLES\n" \
        + "- le prix de la maison est 50% moins chère quand le joueur est marrié\n" \
        + "- il est possible de poser plus de liasse de salaire que le prix minimum\n" \
        + "- permet d'investir les salaires, les salaires investis ne peuvent etre perdu\n"
    
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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Voyage\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il coute : {self.cost} liasse de salaire\n" \
        + "\nREGLES\n" \
        + "- il est possible de poser plus de liasse de salaire que le prix minimum\n" \
        + "- permet d'investir les salaires, les salaires investis ne peuvent etre perdu\n"
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        old_cost = self.cost
        if current_player.has_job() and "travel_free" in current_player.get_job().power:
            self.cost = 0
        super().play_card(game, current_player)
        self.cost = old_cost

class ConcertTicket(AquisitionCard):
    def __init__(self, cost: int, smiles: int, image_path: str):
        super().__init__(cost, smiles, image_path)

class SabreCard(AquisitionCard):
    def __init__(self, cost: int, smiles: int, image_path: str):
        super().__init__(cost, smiles, image_path)
        self.selection_event: Event = Event()
        self.hardship_id: int = None
    
    def confirm_vengeance_selection(self, data):
        """confirmation de la sélection de la cible"""
        self.hardship_id = data.get('hardship_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_vengeance_selection(self, data):
        """annulation de la sélection de la cible"""
        self.selection_event.set()  # Déclencher l'événement
    
    def apply_card_effect(self, game: 'Game', current_player: 'Player'):
        children_played = current_player.get_played_card_vie_perso()
        if any(isinstance(card, BeatrixChild) for card in children_played):
            other_players = [p for p in game.players if p != current_player]
            for player in other_players:    
                received_hardships = [h for h in current_player.received_hardships if h.can_be_played(current_player, game)]
                print("[APPEL] : select_vengeance")
                emit('select_vengeance', {
                    'card_id' : self.id,
                    'received_hardships': [h.to_dict() for h in received_hardships],
                    'available_targets': [player.to_dict()]
                }) # TODO

                print("[EVENT] : Wait for selection")
                self.selection_event.wait()
                self.selection_event.clear()  # Réinitialiser l'événement
                print("[EVENT] : trigger selection")
    
                print(f"player target : {player.name} hardship_id = {self.hardship_id} \n {player.received_hardships}")
                for card in current_player.received_hardships:
                    if card.id == self.hardship_id:                
                        current_player.received_hardships.remove(card)
                        card.apply_effect(game, self.target_player, current_player)
                        player.received_hardships.append(card)
                        break


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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Spécial\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n"
    
    def can_be_played(self, current_player: 'Player', game: 'Game') -> tuple[bool, str]:
        # Logique spécifique selon le type
        return True, ""
    
    def apply_card_effect(self, game: 'Game', current_player: 'Player'):
        pass

    def play_card(self, game: 'Game', current_player: 'Player'):
        self.apply_card_effect(game, current_player)
        super().play_card(game, current_player)

class GirlPowerCard(SpecialCard):
    def __init__(self, special_type: str, image_path: str):
        super().__init__(special_type, image_path)
        
    def get_card_rule(self):
        return "Nous avons une carte Spécial\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- chaque fille posée permet de rejouer une carte spéciale"
    
    def apply_card_effect(self, game, current_player):
        """effectue a nouveaux toutes les cartes spéciales déja posée par le joueur"""
        for special_card in current_player.get_played_card_special():
            if isinstance(special_card, SpecialCard) and special_card.can_be_played(current_player, game):
                special_card.apply_card_effect(game, current_player)

    
class TrocCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("troc", image_path)
        self.smiles = 0
        self.selection_event: Event = Event()
        self.target_player_id: int = None
        self.target_player: Player = None
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    def get_card_rule(self):
        return "Nous avons une carte Troc\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- il permet d'échanger 1 carte avec un autre joueur, entierement aléatoirement\n"
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte Tsunami\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- mélange toutes les cartes en main et redistribue les \n"
    
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
    def __init__(self, image_path: str, heritage_value):
        super().__init__("heritage", image_path)
        self.smiles = 0
        self.value = heritage_value
    
    def get_card_rule(self):
        return "Nous avons une carte Heritage\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il donne {self.value} liasse\n" \
        + "\nREGLES\n" \
        + "- permet d'avoir l'équivalent de liasse pour investir\n" 
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    def apply_card_effect(self, game, current_player):
        current_player.heritage += self.value

class PistonCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("piston", image_path)
        self.smiles = 0
        self.selection_event: Event = Event()
        self.job_id: int = None
        self.job_card: Player = None
        
    def get_card_rule(self):
        return "Nous avons une carte Piston\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- permet de poser un métier sans prendre en compte le niveau d'études requis\n" 
    
    
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

    
    def get_card_rule(self):
        return "Nous avons une carte Vengeance\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- permet d'attaquer quelqu'un avec une des cartes d'attaque que vous avez déja reçus\n" 
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte Chance\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- permet de piocher 3 cartes, en sélectionner 1 puis jouer normalement\n" 
    
    def confirm_card_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.selected_card_id = data.get('selected_card_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_card_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement

    def apply_card_effect(self, game, current_player):
        print("[START] : Chance.apply_card_effect")
        for _ in range(min(3, len(game.deck))):
            self.next_cards.append(game.deck.pop())
        

        print(f"[APPEL] : select_chance_card with {[c.to_dict() for c in self.next_cards]}")
        emit('select_chance_card', {
            'card_id': self.id,
            'cards': [c.to_dict() for c in self.next_cards]
        }, room=current_player.session_id)
        
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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Etoile Filante\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- permet de choisir une carte de la défausse et de la poser directement en respectant les regles pour la poser\n" 
    
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

    def get_card_rule(self):
        return "Nous avons une carte Casino\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- poser cette carte ouvre le casino\n" \
        + "- quand on ouvre le casino, il est possible de miser directement une cartes salaire de notre main\n" \
        + "Voici le fonctionnement du Casino\n" \
        + "- le premier joueur qui joue au casino peut miser une carte salaire\n" \
        + "- le deuxieme joueur qui joue au casino peut miser une carte salaire\n" \
        + "- si les 2 salaires misés sont identiques (meme niveau) alors c'est le joueur qui a misé en deuxieme qui pose ces deux salaires devant lui (meme sans métier)\n" \
        + "- si les 2 salaires misés sont différents alors c'est le joueur qui a misé en premier qui pose ces deux salaires devant lui\n" \
        + "- ensuite le casino est a nouveau disponible pour miser\n"
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte Anniversaire\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- tous les joueurs doivent sélectionner un de leurs salaires posés pour le donner au joueur dont c'est l'anniversaire\n" \
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte Arc en Ciel\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- après avoir posé cette car, il est possible de jouer jusqu'a 3 autres cartes, puis de repiocher\n"
        
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

class MuguetCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("muguet", image_path)
        self.smiles = 1
    
    def get_card_rule(self):
        return "Nous avons une carte Muguet\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- permet de rejouer\n" 
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)
    
    def apply_card_effect(self, game: 'Game', current_player):
        game.phase = "draw"


class HardshipCard(Card):
    """Carte coup dur"""
    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.smiles = 0
        self.selection_event: Event = Event()
        self.target_player: Player = None
        self.target_player_id: int = None

    def get_card_rule(self):
        return "Nous avons une carte Coup Dur\n" \
        + "\nREGLES\n" \
        + "- \n"
    
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

class ChargeMentalHardhip(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"ChargeMentalHardhip"
    
    
    def get_card_rule(self):
        return "Nous avons une carte Charge Mental\n" \
        + "\nREGLES\n" \
        + "- jetter un enfant dans la défausse\n" \
        + "- seul les joueurs qui ont un métier peuvent subir ce coup dur"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'ChargeMental'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', target_player: 'Player'):
        if target_player.has_job():
            return True
        cards = target_player.get_played_vie_perso()
        nb_children = 0
        for c in cards:
            if isinstance(c, ChildCard):
                nb_children += 1
        if nb_children == 0:
            return True
        return False 
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        cards = target_player.get_played_vie_perso()
        for last_child in cards[::-1]:
            if isinstance(last_child, ChildCard):
                game.discard.append(last_child)
                target_player.remove_card_from_played(last_child)

class TachesMenageresHardship(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"TachesMenageresHardship"
    
    
    def get_card_rule(self):
        return "Nous avons une carte Tache Ménagere\n" \
        + "\nREGLES\n" \
        + "- chaque maison posée vaut 1 smile de moi\n" \
        + "- seul les joueurs qui ont au moins une maison peuvent subir ce coup dur"
    
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'TachesMenageresHardship'
        })
        return base
    
    def other_rules(self, game: 'Game', current_player: 'Player', target_player: 'Player'):
        cards = target_player.get_played_acquisitions()
        nb_house = 0
        for c in cards:
            if isinstance(c, HouseCard):
                nb_house += 1
        if nb_house == 0:
            return True
        return False 
    
    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def apply_effect(self, game, target_player, current_player):
        cards = target_player.get_played_acquisitions()
        for house in cards:
            if isinstance(house, HouseCard):
                target_player.skip_turns += house.smiles

class TaxCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
    
    def __str__(self):
        return f"TaxCard"
    
    def get_card_rule(self):
        return "Nous avons une carte Impot sur le Revenu\n" \
        + "\nREGLES\n" \
        + "- retire le dernier salaire posé d'un joueur\n" \
        + "- seul les joueurs qui ont un métier peuvent subir ce coup dur"
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte Maladie\n" \
        + "\nREGLES\n" \
        + "- fait passer un tour\n"
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte Accident\n" \
        + "\nREGLES\n" \
        + "- fait passer un tour au joueur visé\n"
    
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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Attentat\n" \
        + "\nREGLES\n" \
        + "- défausse absolument tous les enfants posé meme les tiens\n"
    
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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Divorce\n" \
        + "\nREGLES\n" \
        + "- retire le marriage d'un joueur\n" \
        + "- seul les joueurs qui ont un marriage peuvent subir ce coup dur"
    
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
    
    
    def get_card_rule(self):
        return "Nous avons une carte BurnOut\n" \
        + "\nREGLES\n" \
        + "- fait passer un tour à un joueur\n" \
        + "- seul les joueurs qui ont un métier peuvent subir ce coup dur"
    
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
    
    
    def get_card_rule(self):
        return "Nous avons une carte Redoublement\n" \
        + "\nREGLES\n" \
        + "- retire le derniere carte étude posé d'un joueur\n" \
        + "- seul les joueurs qui n'ont pas un métier peuvent subir ce coup dur"
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte Prison\n" \
        + "\nREGLES\n" \
        + "- retire le métier de bandit d'un joueur\n" \
        + "- fait passer 3 tour à un joueur\n" \
        + "- défausse 2 cartes aléatoire de la main d'un joueur\n" \
        + "- seul les joueurs qui ont le métier de bandit peuvent subir ce coup dur"
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte Licenciement\n" \
        + "\nREGLES\n" \
        + "- retire le métier posé d'un joueur\n" \
        + "- seul les joueurs qui ont un métier qui n'est pas fonctionnaire peuvent subir ce coup dur"

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


    def get_card_rule(self):
        return "Nous avons une carte Other Card\n" \
        + "\nREGLES\n"

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
    
    def get_card_rule(self):
        return "Nous avons une carte Légion\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- peut etre poser que si le joueur n'as pas été bandit dans la partie (il peut etre bandit après avoir eu la légion)\n"

    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

class PriceCard(OtherCard):
    """Carte prix d'excellence"""
    def __init__(self, smiles: int, image_path: str):
        super().__init__('prix', smiles, image_path)
        self.job_link = None
        
    def get_card_rule(self):
        return "Nous avons une carte Grand Prix d'Exelence\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- peut etre poser que avec certain métier\n" \
        + "- permet a ces métier de pouvoir poser des salaires de 1 à 4" \
        + "- meme si le joueur perd son métier dont il a le prix d'exelence lier, il garde le bonus de smile du prix, mais ce prix n'as plus d'effet"

    
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
    
    def get_card_rule(self):
        return "Nous avons une carte JobCard\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n"
    
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


    def get_card_rule(self):
        return "Nous avons une carte métier Chercheur\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- grand prix d'exelence possible\n" \
        + "- jouer avec 6 cartes en mains\n"

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

    
    def get_card_rule(self):
        return "Nous avons une carte métier Astronaute\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- pouvoir instantanée : récupérer une carte posable depuis la défausse et poser la\n"
    
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
        
    def get_card_rule(self):
        return "Nous avons une carte métier Bandit\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- Ne peux pas subir d'Impot sur le Revenu\n" \
        + "- Ne peux pas etre licencier\n"

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
        
    def get_card_rule(self):
        return "Nous avons une carte métier Médium\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- pouvoir instantanée : regarder les 13 prochaine cartes de la pioche\n"
    
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


    def get_card_rule(self):
        return "Nous avons une carte métier Chercheur\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- grand prix d'exelence possible\n" \
        + "- pouvoir instantanée : voir la main des autres joueurs\n"

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

    
    def get_card_rule(self):
        return "Nous avons une carte métier Chef des Achats\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- pouvoir instantanée : récupère une carte Acquisition de la défausse et propose de l'acheter\n"
    
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

    
    def get_card_rule(self):
        return "Nous avons une carte métier Chercheur\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- pouvoir instantanée : choisi un salaire posable depuis la défausse et pose le\n"
    
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

    
    def get_card_rule(self):
        return "Nous avons une carte métier Prof\n" \
        + f"ce métier est un {self.status}\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- ne peux pas etre licencié\n"

class GrandProfJob(JobCard):
    def __init__(self, job_name: str, salary: int, image_path: str):
        super().__init__(job_name, salary, 0, image_path)
        self.status = "fonctionnaire"
        self.power = ""
        
    def get_card_rule(self):
        return "Nous avons une carte métier Grand Prof\n" \
        + f"ce métier est un {self.status}\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- ne peux pas etre licencié\n" \
        + "- remplace le métier de professeur\n" \
        + "- necessite d'etre professeur avant de poser cette carte\n"
        

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
    
    def get_card_rule(self):
        return "Nous avons une carte métier Gourou\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + ""
    
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
    
    def get_card_rule(self):
        return "Nous avons une carte métier Gourou\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- ne peux pas etre licencié\n" \
        + "- il ne peux pas y avoir de bandit ou de gourou avec un policier\n"
    
    def apply_instant_power(self, game, current_player):
        for player in game.players:
            if player.has_job() and isinstance(player.get_job(), (GourouJob, BanditJob)):
                player.get_job().discard_play_card(game, player)

class ArchitecteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "house_free"
        
    def get_card_rule(self):
        return "Nous avons une carte métier Architecte\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- permet de poser gratuitement la prochaine maison\n"
    
    def use_power(self):
        self.power = ""

    def loosing_continuous_power(self, game: 'Game', effected_player: 'Player'):
        self.power = "house_free"

class AvocatJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_divorce"
    
    def get_card_rule(self):
        return "Nous avons une carte métier Avocat\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- ne peux pas recevoir de Divorce\n"

class BarmanJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = "unlimited_flirt"
    
    
    def get_card_rule(self):
        return "Nous avons une carte métier Gourou\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- flirt illimité avant le mariage\n" \
        + "- possibilité de démissionner à n'importe quel moment du tour"

class ChirurgienJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_illness__extra_study"
    
    def get_card_rule(self):
        return "Nous avons une carte métier Chirurgien\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- ne peux pas recevoir de maladie\n" \
        + "- peut continuer les études a l'infini\n"

class DesignerJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
    
    def get_card_rule(self):
        return "Nous avons une carte métier Designer\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + ""

class GaragisteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_accident"
    
    def get_card_rule(self):
        return "Nous avons une carte métier Garagiste\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- ne peux pas subir d'accident"

class JardinierJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
    
    def get_card_rule(self):
        return "Nous avons une carte métier Jardinier\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + ""

class MedecinJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_maladie__extra_study"
    
    def get_card_rule(self):
        return "Nous avons une carte métier Médecin\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- ne peux pas recevoir de maladie\n" \
        + "- peut continuer les études a l'infini\n"

class MilitaireJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "fonctionnaire"
        self.power = "no_attentat"
    
    def get_card_rule(self):
        return "Nous avons une carte métier Jardinier\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- ne peux pas etre licencier\n" \
        + "- il ne peux pas y avoir d'attentat quand ce métier est posé\n"

class PharmacienJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "no_maladie"
    
    
    def get_card_rule(self):
        return "Nous avons une carte métier Jardinier\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- ne peux pas subir de Maladie\n"

class PiloteDeLigneJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "travel_free"

    
    def get_card_rule(self):
        return "Nous avons une carte métier Pilote de ligne\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- tous les voyages sont gratuits\n"

class PizzaioloJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
    
    def get_card_rule(self):
        return "Nous avons une carte métier Pizzaiolo\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + ""

class PlombierJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = ""
    
    def get_card_rule(self):
        return "Nous avons une carte métier Plombier\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- peux démissionner a tout moment du tour\n"

class ServeurJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = ""
    
    def get_card_rule(self):
        return "Nous avons une carte métier Serveur\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- peux démissionner a tout moment du tour\n"

class StripTeaserJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = ""
    
    def get_card_rule(self):
        return "Nous avons une carte métier StripTeaser\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- peux démissionner a tout moment du tour\n"

class EcrivainJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = "prix_possible"
    
    def get_card_rule(self):
        return "Nous avons une carte métier Ecrivain\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- grand prix d'exelence possible\n"

class YoutuberJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
    
    def get_card_rule(self):
        return "Nous avons une carte métier Youtubeur\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "-\n"

class CoiffeurJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ""
    
    def get_card_rule(self):
        return "Nous avons une carte métier Coiffeur\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "-\n"

class DeejayJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "intérimaire"
        self.power = ""
    
    def get_card_rule(self):
        return "Nous avons une carte métier Plombier\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + "- peux démissionner a tout moment du tour\n" \
        + "- quand on le pose, mélange toutes les cartes en main des joueurs\n"
    
    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        print("[START] : DeeJay.apply_instant_power")
        hands: list[Card] = []
        for player in game.players:
            hands.extend(player.hand)
        random.shuffle(hands)
        for player in game.players:
            nb_cards = len(player.hand)
            player.hand = []
            for _ in range(nb_cards):
                player.hand.append(hands.pop())


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
    
    def get_played_vie_pro(self):
        return self.played["vie professionnelle"]
    
    def get_played_vie_perso(self):
        return self.played["vie personnelle"]

    def get_played_acquisitions(self):
        return self.played["acquisitions"]
    
    def get_played_salaire_depense(self):
        return self.played["salaire dépensé"]
    
    def get_played_carte_speciale(self):
        return self.played["cartes spéciales"]

    def __str__(self):
        return "Player YOUSK"
    
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
    
    def get_played_card_vie_perso(self):
        return self.played["vie personnelle"]
    
    def get_played_card_vie_pro(self):
        return self.played["vie professionnelle"]
    
    def get_played_card_special(self):
        return self.played["cartes speciales"]

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
        has_licorne = any(isinstance(c, LicorneAnimal) for c in all_cards)
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
