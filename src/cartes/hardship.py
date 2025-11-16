from .card import Card, PermanentEffet, StudyCard, SalaryCard
from threading import Event
from typing import Dict, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from src.Game import Game
    from src.Player import Player
    from .jobs import JobCard, BanditJob, ArchitecteJob
    from .children import ChildCard
    from .acquisitions import HouseCard
    from .card import MarriageCard, AdulteryCard



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

class GynocratieHardship(HardshipCard, PermanentEffet):
    def __init__(self, image_path):
        super().__init__(image_path)
    def __str__(self):
        return f"smile : {self.smiles} - HardshipCard"
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'GynocratieHardship'
        })
        return base
    
    def get_card_rule(self):
        return "Nous avons une carte Gynocratie\n" \
        + "\nREGLES\n" \
        + "- s'applique a quelqu'un d'autre\n" \
        + "- chaque enfant Femme valent 1 smile de moins\n" \
        + "- ne peux pas etre cumuler avec Phalocratie"

    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        effets_permanent = player.get_played_effet_permanent()
        for card in effets_permanent:
            if isinstance(card, (PhalocratieHardship, GynocratieHardship)):
                return True
        return False

class PhalocratieHardship(HardshipCard, PermanentEffet):
    def __init__(self, image_path):
        super().__init__(image_path)
    def __str__(self):
        return f"smile : {self.smiles} - HardshipCard"
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'PhalocratieHardship'
        })
        return base
    
    def get_card_rule(self):
        return "Nous avons une carte Phalocratie\n" \
        + "\nREGLES\n" \
        + "- s'applique a quelqu'un d'autre\n" \
        + "- chaque enfant Homme valent 1 smile de moins\n" \
        + "- ne peux pas etre cumuler avec Gynocratie"
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        effets_permanent = player.get_played_effet_permanent()
        for card in effets_permanent:
            if isinstance(card, (PhalocratieHardship, GynocratieHardship)):
                return True
        return False

class PlafondDeVerreHardship(HardshipCard, PermanentEffet):
    def __init__(self, image_path):
        super().__init__(image_path)
    def __str__(self):
        return f"smile : {self.smiles} - HardshipCard"
    def to_dict(self) -> Dict[str, Any]:
        base = super().to_dict()
        base.update({
            'subtype': 'PlafondDeVerreHardship'
        })
        return base
    
    def get_card_rule(self):
        return "Nous avons une carte Plafond de Verre\n" \
        + "\nREGLES\n" \
        + "- s'applique a quelqu'un d'autre\n" \
        + "- ne peux pas avoir de métier qui demande un niveau d'étude de 5 ou 6\n" \
        + "- l'effet est valide sur tous les nouveaux métiers"
    
    def get_power(self):
        return ["no_job_with_study_5", "no_job_with_study_6"]
    
class PorcHardship(HardshipCard):
    def __init__(self, image_path):
        super().__init__(image_path)

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

    def get_card_rule(self):
        return "Nous avons une carte Balance Ton Porc\n" \
        + "\nREGLES\n" \
        + "- s'applique a un autre joueur\n" \
        + "- défausse le mariage et le métier du joueur\n"
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        if not player.is_married():
            return True
        if not player.has_job():
            return True
        return False
    
    def apply_effect(self, game: 'Game', target_player: 'Player', current_player: 'Player'):
        # Supprime le marriage
        DivorceCard("").apply_effect(game, target_player, current_player)
        # licenciement
        LicenciementCard("").apply_effect(game, target_player, current_player)

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
        if "no_tax" in player.get_power():
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
        return player.has_job() and "no_maladie" in player.get_power()
             
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
        print("[START] : accidentCard.other_rules")
        return "no_accident" in player.get_power()

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
            if player.has_job() and "no_attentat" in player.get_power():
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
        if player.has_job() and "no_divorce" in player.get_power():
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
        if player.has_job():
            jobs: list[JobCard] = player.get_job()
            for job in jobs:
                if isinstance(job, BanditJob):
                    return False
        return True
        
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
        LicenciementCard("").apply_effect(game, target_player, current_player)

class LicenciementCard(HardshipCard):
    def __init__(self, image_path: str):
        super().__init__(image_path)
        self.targeted_job_id = None

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
        if "no_fire" in player.get_power():
            return True
        return False

    def can_be_played(self, current_player, game):
        return super().can_be_played(current_player, game)

    def play_card(self, game, current_player):
        super().play_card(game, current_player)

    def confirm_select_job_licenciement(self, data):
        """confirmation de la sélection des salaires"""
        print("[appel] : confirm_target_selection")
        self.targeted_job_id = data.get("target_job_id", None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_select_job_licenciement(self, data):
        """annulation de la sélection des salaires"""
        print("[appel] : discard_target_selection")
        self.selection_event.set()  # Déclencher l'événement
    
    def other_rules(self, game: 'Game', current_player: 'Player', player: 'Player'):
        return False
    def apply_effect(self, game, target_player, current_player):
        target_jobs = target_player.get_job() 
        if len(target_jobs) == 1:
            target_jobs[0].discard_play_card(game, target_player)
        else:
            print("A FAIRE, AFFICHAGE POUR SELECTIONNER UN JOB PARMIS LA LISTE")
            print("[appel] : select_job_licenciement")
            emit('select_job_licenciement', {
                'card': self.to_dict(),
                'jobs': [job.to_dict() for job in target_jobs]
            })
            
            print("[EVENT] : Wait for selection")
            self.selection_event.wait()
            self.selection_event.clear()
            print("[EVENT] : trigger selection")
            
            if self.targeted_job_id is None:
                job = random.choice(target_jobs)
            else:
                for j in target_jobs:
                    if j.id == self.targeted_job_id:
                        job = j
            job.discard_play_card(game, target_player)
