from .card import Card
from threading import Event
from typing import Dict, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from src.Game import Game
    from src.Player import Player
    from .acquisitions import AquisitionCard

class JobCard(Card):
    """Carte métier"""
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(image_path)
        self.job_name = job_name
        self.salary = salary
        self.studies = studies
        self.status = ""
        self.power = []
        self.smiles = 2
    
    def get_power(self):
        power = self.power
        if self.status == "fonctionnaire":
            power += ["no_fire"]
        return power
    
    def get_salary(self):
        return self.salary

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
        max_jobs = 1
        if "2_jobs" in player.get_power():
            max_jobs = 2
        
        if player.has_job():
            jobs = player.get_job()
            if len(jobs) == max_jobs:
                return False, "Vous avez déjà un métier"
                
        # Vérifier si le joueur a les études nécessaires
        if isinstance(self.studies, int) and self.studies > 0:
            if player.count_studies() < self.studies:
                return False, f"Vous avez besoin de {self.studies} études"
        
        if f"no_job_with_study_{self.studies}" in player.get_power():
            return False, f"Vous ne pouvez pas avoir de métier qui demande {self.studies} études"

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
        self.power = ["prix_possible"]
        self.is_link = False

    def get_salary(self):
        if self.is_link:
            return 4
        return self.salary



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
        self.power = []
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
        self.power = ["no_tax","no_fire"]
        
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
            if player.has_job() and "no_bandit" in player.get_power():
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
        self.power = []
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
        self.power = ["prix_possible"]
        self.selection_event: Event = Event()
        self.is_link = False
    
    def get_salary(self):
        if self.is_link:
            return 4
        return self.salary
    
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
        self.power = []
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
        self.power = []
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
        self.power = []

    
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
        self.power = []
        
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
        if not player.has_job():
            return False, "vous devez avoir un métier"
        jobs = player.get_job()
        for job in jobs:
            if isinstance(job, ProfJob):
                return True, ""
        return False, "Vous devez être professeur pour devenir grand prof"

    def apply_instant_power(self, game: 'Game', current_player: 'Player'):
        jobs = current_player.get_job()
        for job in jobs:
            if isinstance(job, ProfJob):
                current_player.remove_card_from_played(job)
                game.discard.append(job)

class GourouJob(JobCard):
    def __init__(self, job_name, salary, studies, image_path):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = []
    
    def get_card_rule(self):
        return "Nous avons une carte métier Gourou\n" \
        + f"il donne {self.smiles} smiles\n" \
        + f"il necessite {self.studies} études\n" \
        + f"il peut poser des salaire jusqu'à {self.salary}\n" \
        + "\nREGLES\n" \
        + ""
    
    def can_be_played(self, player, game):
        for player in game.players:
            if player.has_job() and "no_gourou" in player.get_power():
                return False, "il y a un job qui empeche le bandit"
        return super().can_be_played(player, game)

class PolicierJob(JobCard):
    def __init__(self, job_name, salary, studies, image_path):
        super().__init__(job_name, salary, studies, image_path)
        self.status = "fonctionnaire"
        self.power = ["no_bandit","no_gourou"]
    
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
            if player.has_job():
                jobs: list[JobCard] = player.get_job()
                for job in jobs:
                    if isinstance(job, (GourouJob, BanditJob)):
                        job.discard_play_card(game, player)

class ArchitecteJob(JobCard):
    def __init__(self, job_name: str, salary: int, studies: int, image_path: str):
        super().__init__(job_name, salary, studies, image_path)
        self.status = ""
        self.power = ["house_free"]
        
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
        self.power = ["no_divorce"]
    
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
        self.power = ["unlimited_flirt"]
    
    
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
        self.power = ["no_illness","extra_study"]
    
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
        self.power = []
    
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
        self.power = ["no_accident"]
    
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
        self.power = []
    
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
        self.power = ["no_maladie","extra_study"]
    
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
        self.power = ["no_attentat"]
    
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
        self.power = ["no_maladie"]
    
    
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
        self.power = ["travel_free"]

    
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
        self.power = []
    
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
        self.power = []
    
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
        self.power = []
    
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
        self.power = []
    
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
        self.power = ["prix_possible"]
        self.is_link = False

    def get_salary(self):
        if self.is_link:
            return 4
        return self.salary
    
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
        self.power = []
    
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
        self.power = []
    
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
        self.power = []
    
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
