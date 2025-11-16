from .card import Card
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.Game import Game
    from src.Player import Player
    from .jobs import JobCard

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
        
        if "prix_possible" not in current_player.get_power():
            return False, "Votre métier ne permet pas de recevoir un prix"
        for job in current_player.get_job():
            if "prix_possible" in job.get_power():
                self.job_link = job.id
                job.is_link = True
        print("le link est : ", self.job_link)

        return True, ""
    
    def play_card(self, game: 'Game', current_player: 'Player'):
        super().play_card(game, current_player)



