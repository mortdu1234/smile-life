from .card import Card, PermanentEffet, SalaryCard
from threading import Event
from typing import Dict, Any, TYPE_CHECKING
import random

if TYPE_CHECKING:
    from src.Game import Game
    from src.Player import Player
    from .jobs import JobCard
    from .children import ChildCard, FemaleChild
    from .card import MarriageCard
    from .hardship import HardshipCard

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

    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)

class RedistributionDesTachesCard(SpecialCard):
    def __init__(self, image_path):
        super().__init__("redistribution des taches", image_path)
        self.selection_event: Event = Event()
        self.choices: dict[int] = None

    def get_card_rule(self):
        return "Nous avons une carte Redistribution des taches\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- récupère tous les métiers présent et redistribue les a ta guise\n" \
        + "- il n'y a pas de regle concernant les niveaux de métier ou autre"
    
    def confirm_selection(self, data):
        """confirmation de la sélection de la cible"""
        self.choices = data.get('distribution', None)
        self.selection_event.set()  # Déclencher l'événement
    
    def apply_card_effect(self, game, current_player):
        initial_data = {}
        job_id_to_card = {}
        for player in game.players:
            jobs = []
            for job in player.get_job():
                jobs.append(job.id)
                job_id_to_card[job.id] = [job, player]
            initial_data[player.id] = [jobs, len(jobs)]
        
        print("[APPEL] : redistribution_des_taches")
        emit('redistribution_des_taches', {
            'card_id' : self.id,
            'data_initial': initial_data
        })

        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()
        print("[EVENT] : trigger selection")

        # Appliquer la redistribution si elle a été confirmée
        if self.choices:
            # Retirer tous les métiers de leurs joueurs actuels
            for job_id, (job_card, original_player) in job_id_to_card.items():
                original_player.remove_card_from_played(job_card)
            
            # Redistribuer selon les choix
            for player_id, job_ids in self.choices.items():
                player = game.players[int(player_id)]
                for job_id in job_ids:
                    if job_id in job_id_to_card:
                        job_card = job_id_to_card[job_id][0]
                        player.add_card_to_played(job_card)
        
        return True


            
        






    



class EgaliteDesSalaireCard(SpecialCard, PermanentEffet):
    def __init__(self, image_path:str):
        super().__init__("egalite des salaire", image_path)

    def get_card_rule(self):
        return "Nous avons une carte Egalite des Salaire\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- votre limite max de niveau de salaire est le meme que le meilleur joueur\n" \
        + "- effet permanant"
    
    def get_power(self):
        return ["egalite_salaire"]


class ClicheCard(SpecialCard, PermanentEffet):
    def __init__(self, image_path: str):
        super().__init__("cliché", image_path)

class ClicheAccident(ClicheCard):
    def __init__(self, image_path:str):
        super().__init__(image_path)

    def get_card_rule(self):
        return "Nous avons une carte cliché\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- ne peu plus subir d'accident\n" \
        + "- effet permanant"
    
    def get_power(self):
        return ["no_accident"]

class ClicheFlirt(ClicheCard):
    def __init__(self, image_path:str):
        super().__init__(image_path)

    def get_card_rule(self):
        return "Nous avons une carte cliché\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- flirt a volonté avant le marriage\n" \
        + "- effet permanant"
    
    def get_power(self):
        return ["unlimited_flirt"]

class ClicheMetier(ClicheCard):
    def __init__(self, image_path:str):
        super().__init__(image_path)

    def get_card_rule(self):
        return "Nous avons une carte cliché\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- vous pouvez cumuler 2 métier\n" \
        + "- effet permanant"
    
    def get_power(self):
        return ["2_jobs"]

class GirlPowerCard(SpecialCard, PermanentEffet):
    def __init__(self, image_path: str):
        super().__init__("girl power", image_path)
        self.special_cards_uses: list[SpecialCard] = []
        self.selection_event: Event = Event()
        self.special_card_id = None
        
    def get_card_rule(self):
        return "Nous avons une carte Spécial\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- chaque fille posée permet de rejouer une carte spéciale\n" \
        + "- effet permanant"
    
    def confirm_selection(self, data):
        """confirmation de la sélection des salaires"""
        self.special_card_id = data.get('selected_card_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_selection(self, data):
        """annulation de la sélection des salaires"""
        self.selection_event.set()  # Déclencher l'événement

    def effect(self, game, current_player):
        specials_cards: list[SpecialCard] = [card for card in current_player.get_played_carte_speciale() if isinstance(card, SpecialCard) and card not in self.special_cards_uses and card.can_be_played(current_player, game)]
        print("[appel] : select_girl_power_card")
        emit('select_girl_power_card', {
            'card_id': self.id,
            'special_cards': [card.to_dict() for card in specials_cards]
        })
        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection")

        if self.special_card_id is not None:
            selected_card: SpecialCard = current_player.get_played_carte_speciale_by_id(self.special_card_id)
            self.special_cards_uses.append(selected_card)
            current_player.remove_card_from_played(selected_card)
            current_player.add_card_to_hand(selected_card)
            selected_card.play_card(game, current_player)

    def apply_card_effect(self, game, current_player):
        """effectue a nouveaux toutes les cartes spéciales déja posée par le joueur"""
        nb_filles = 0
        for children in current_player.get_played_vie_perso():
            if isinstance(children, FemaleChild):
                nb_filles += 1
        
        for _ in range(nb_filles):
            self.effect(game, current_player)

        return True
    
    def get_power(self):
        return super().get_power() + ["double_special_card"]

class SoireeEntreFilleCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("soirée entre fille", image_path)
        self.target_player_id: int = ""
    
    def get_card_rule(self):
        return "Nous avons une carte Spécial\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- récupère tous les enfants dans les mains et pose les sans conditions"
    
    def apply_card_effect(self, game: 'Game', current_player: 'Player'):
        for player in game.players:
            nb_children = 0
            hand = player.hand
            for card in hand:
                if isinstance(card, ChildCard):
                    current_player.add_card_to_played(card)
                    player.remove_card_from_hand(card)
                    nb_children += 1
            for _ in range(nb_children):
                player.add_card_to_hand(game.get_card_from_deck())
        return True
    
class CoupDeFoudreCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("coup de foudre", image_path)
        self.selection_event: Event = Event()
        self.target_player_id: int = None
        self.target_player: Player = None

    def get_card_rule(self):
        return "Nous avons une carte Coup de Foudre\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- vole un marriage a un joueur"
    
    def can_be_played(self, current_player, game):
        for player in game.players:
            if player == current_player and player.is_married():
                return False, "le joueur est déja marrié"
            else:
                if player.is_married():
                    return True, ""
        return False, "aucun joueur n'est marrié"
    
    def confirm_selection(self, data):
        """confirmation de la sélection des salaires"""
        print("[appel] : confirm_target_selection")
        self.target_player_id = data.get('target_player_id')
        self.selection_event.set()  # Déclencher l'événement

    def discard_selection(self, data):
        """annulation de la sélection des salaires"""
        print("[appel] : discard_target_selection")
        self.target_player = None
        self.target_player_id = None
        self.selection_event.set()  # Déclencher l'événement
    
    def get_available_targets(self, game: 'Game', current_player: 'Player') -> list[dict]:
        targets = []
        for player in game.players:
            values = player.to_dict()
            values["immune"] = False
            if player == current_player:
                values["immune"] = True
            if not player.is_married():
                values["immune"] = True
            targets.append(values)
        return targets

    def apply_card_effect(self, game, current_player):
        targets = self.get_available_targets(game, current_player)
  
        print("[appel] : select_coup_de_foudre_target")
        emit('select_coup_de_foudre_target', {
            'card_id': self.id,
            'available_targets': targets
        })
        
        print("[EVENT] : Wait for selection")
        self.selection_event.wait()
        self.selection_event.clear()
        print("[EVENT] : trigger selection")
        
        self.target_player = game.players[self.target_player_id]
        marriage = self.target_player.get_marriage()
        self.target_player.remove_card_from_played(marriage)
        current_player.add_card_to_vie_perso(marriage)
        return True

class ErreurDetiquetageCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("erreur etiquetage", image_path)
        self.selection_event: Event = Event()
        self.target_player_id: int = None
        self.current_child_id: int = None
        self.target_child_id: int = None

    
    def get_card_rule(self):
        return "Nous avons une carte erreur d'étiquetage\n" \
        + f"il donne {self.smiles} smiles\n" \
        + "\nREGLES\n" \
        + "- echange un de vos enfants posé avec un autre joueur\n" 
    
    def confirm_children_selection(self, data):
        """confirmation de la sélection de la cible"""
        print("[confirm_children_selection]", end=" ")
        self.current_child_id = data.get('current_child_id', None)
        self.target_child_id = data.get('target_child_id', None)
        print(self.current_child_id, self.target_child_id)
        self.selection_event.set()  # Déclencher l'événement

    def confirm_target_selection(self, data):
        """confirmation de la sélection de la cible"""
        print("[confirm_target_selection]")
        self.target_player_id = int(data.get('target_id', None))
        self.selection_event.set()  # Déclencher l'événement

    def discard_selection(self, data):
        """annulation de la sélection de la cible"""
        print("[discard_selection]")
        self.selection_event.set()  # Déclencher l'événement

    def can_be_played(self, current_player, game):
        for player in game.players:
            if player != current_player:
                if any(isinstance(card, ChildCard) for card in player.get_played_vie_perso()):
                    return True, ""
        return False, "pas de cible disponibles ou pas de cartes recus"
    
    def get_available_targets(self, game: 'Game', current_player: 'Player') -> list[dict]:
        targets = []
        for player in game.players:
            values = player.to_dict()
            values["immune"] = False
            if player == current_player:
                values["immune"] = True
            if not any(isinstance(card, ChildCard) for card in player.get_played_vie_perso()):  
                values["immune"] = True
            targets.append(values)
        return targets
    
    def apply_card_effect(self, game, current_player):
        print("[START] : ErreurDetiquetageCard.apply_card_effect")
        targets = self.get_available_targets(game, current_player)

        print("[APPEL] : select_etiquetage_target")
        emit('select_etiquetage_target', {
            'card_id' : self.id,
            "targets" : targets
        }, room=current_player.session_id)

        print("[EVENT] : Wait for selection 1")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection 1")

        if self.target_player_id is None:
            return False

        target_player = game.players[self.target_player_id]
        print(f"le joueur target : {target_player}")
        target_children: list[ChildCard] = [card.to_dict() for card in target_player.get_played_vie_perso() if isinstance(card, ChildCard)]
        current_children: list[ChildCard] = [card.to_dict() for card in current_player.get_played_vie_perso() if isinstance(card, ChildCard)]
        # print(f"les enfants possible {target_children}")
        # print(f"tes enfants possible {current_children}")

        print("[APPEL] : select_etiquetage_children")
        emit('select_etiquetage_children', {
            'card_id' : self.id,
            "target_children" : target_children,
            "current_children" : current_children
        }, room=current_player.session_id)

        print("[EVENT] : Wait for selection 2")
        self.selection_event.wait()
        self.selection_event.clear()  # Réinitialiser l'événement
        print("[EVENT] : trigger selection 2")

        print(f"target id : {self.target_child_id}")
        if not self.target_child_id:
            return False


        target_child = target_player.get_played_vie_perso_by_id(self.target_child_id)
        current_child = current_player.get_played_vie_perso_by_id(self.current_child_id)

        print(f"les enfants : {target_child} {current_child}")
        target_player.remove_card_from_played(target_child)
        target_player.add_card_to_vie_perso(current_child)

        current_player.remove_card_from_played(current_child)
        current_player.add_card_to_vie_perso(target_child)
        return True

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
        return True
        
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
        return True

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
        return True

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
        return True

class VengeanceCard(SpecialCard):
    def __init__(self, image_path: str):
        super().__init__("vengeance", image_path)
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
        return True
            
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
        return True

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
        return True   
                
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
        return True

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
        return True


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
        return True

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
        return True


