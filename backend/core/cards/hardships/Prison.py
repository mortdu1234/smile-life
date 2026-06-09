from backend.core.cards.professionnals.Bandit import Bandit
from .HardshipCard import Hardship
import random
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
    from backend.userIo.interface import UserIO


class Prison(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        # Vérifie si le joueur possède le métier bandit
        job = player.get_job() 
        if not job or not isinstance(job, Bandit):
            return False
        
        return super().can_be_targeted(player, game)
    def get_name(self) -> str:
        return "Prison"
    def apply_card_effect(self, game: "Game", current_player: "Player", interface: "UserIO") -> bool:
        success = super().apply_card_effect(game, current_player, interface)
        if not success:
            return False
        assert self.target_player is not None
        job = self.target_player.get_job()
        if not job:
            print("[ERROR] métier non trouvé")
            return False
        # retire le métier
        self.target_player.remove_card(job)

        # retire 2 cartes aléatoire de la main du joueur
        nombre_de_carte_retiree = 2
        player_hand = self.target_player.get_hand()
        for _ in range(nombre_de_carte_retiree):
            selected_card = random.choice(player_hand)
            self.target_player.remove_card_from_hand(selected_card)
            game.add_card_to_discard(selected_card)
        for _ in range(nombre_de_carte_retiree):
            new_card = game.take_card_from_deck()
            self.target_player.add_card_to_hand(new_card)

        # fait passer 3 tours
        self.target_player.add_skip_turn(3)
        
        return True

    def get_card_rule(self) -> str:
        return """La prison est une carte qui peut s'appliquer uniquement sur quelqu'un qui est actuellement bandit. Son effet est de faire passer 3 tours, faire démissionner le bandit, retirer 2 cartes aléatoire de la main"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()