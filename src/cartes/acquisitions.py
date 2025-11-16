from .card import Card, SalaryCard
from threading import Event
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.Game import Game
    from src.Player import Player
    from .jobs import ArchitecteJob
    from .children import ChildCard, BeatrixChild
    
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
        player_powers = current_player.get_power()
        if 'house_free' in player_powers:
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
        if "house_free" in current_player.get_power():
            self.cost = 0
            if current_player.has_job():    
                jobs = current_player.get_job()
                for job in jobs:
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
        player_power = current_player.get_power()
        if 'travel_free' in player_power:
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
        if current_player.has_job() and "travel_free" in current_player.get_power():
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
        self.target_player_id: int = None
        self.hardship_id: str = None
    
    def confirm_sabre_selection(self, data):
        """confirmation de la sélection de la cible et de l'attaque"""
        self.target_player_id = data.get('target_id', None)
        self.hardship_id = data.get('hardship_id', None)
        self.selection_event.set()  # Déclencher l'événement

    def discard_sabre_selection(self, data):
        """annulation de la sélection de la cible"""
        self.selection_event.set()  # Déclencher l'événement
    
    def apply_card_effect(self, game: 'Game', current_player: 'Player'):
        children_played = current_player.get_played_vie_perso()
        if any(isinstance(card, BeatrixChild) for card in children_played):
            other_players = [p for p in game.players if p != current_player]
            
            for player in other_players:    
                received_hardships = [h for h in current_player.received_hardships if h.can_be_played(current_player, game)[0]]
                
                print("[APPEL] : select_sabre")
                emit('select_sabre', {
                    'card_id': self.id,
                    'target_player': player.to_dict(),
                    'received_hardships': [h.to_dict() for h in received_hardships]
                }, room=current_player.session_id)

                print("[EVENT] : Wait for selection")
                self.selection_event.wait()
                self.selection_event.clear()  # Réinitialiser l'événement
                print("[EVENT] : trigger selection")
    
                if not self.hardship_id:
                    continue
                    
                target_player = game.players[self.target_player_id]
                print(f"player target : {target_player.name} hardship_id = {self.hardship_id}")
                
                for card in current_player.received_hardships:
                    if card.id == self.hardship_id:                
                        current_player.received_hardships.remove(card)
                        card.apply_effect(game, target_player, current_player)
                        target_player.received_hardships.append(card)
                        break
        return True

class NounouCard(AquisitionCard):
    def __init__(self, cost: int, smiles: int, image_path: str):
        super().__init__(cost, smiles, image_path)
    
    def apply_card_effect(self, game: 'Game', current_player: 'Player'):
        for child in current_player.get_played_vie_perso():
            if isinstance(child, ChildCard):
                current_player.remove_card_from_played(child)
                current_player.add_card_to_salaire_depense(child)
        return True


