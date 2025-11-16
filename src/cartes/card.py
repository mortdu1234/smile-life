import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.Player import Player
    from src.Game import Game

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
    
    def apply_card_effect(self, game: 'Game', current_player: 'Player') -> bool:
        """renvois true si success, false sinon"""
        return True
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        """pose la carte"""
        print("pose la carte")
        if self.apply_card_effect(game, current_player):
            current_player.hand.remove(self)
            current_player.add_card_to_played(self)

    def get_card_rule(self):
        return "Nous avons une carte classique\n" \
        + f"il donne {self.smiles} smiles\n" 

class PermanentEffet(ABC):
    def get_power(self) -> list[str]:
        return []

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
        if current_player.has_job() and 'extra_study' not in current_player.get_power():
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
        jobs = current_player.get_job()
        if not jobs:
            return False, "Vous devez avoir un métier pour recevoir un salaire"

        max_salary = max(job.get_salary() for job in jobs)
        if "egalite_salaire" in current_player.get_power():
            global_max_salary = 0
            for player in game.players:
                if player.has_job():
                    jobs = player.get_job()
                    for job in jobs:
                        global_max_salary = max(global_max_salary, job.get_salary())
            max_salary = max(max_salary, global_max_salary)
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
