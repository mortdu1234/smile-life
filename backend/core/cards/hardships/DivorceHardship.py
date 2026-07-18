from backend.core.Power import Power
from .HardshipCard import Hardship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
    from backend.userIo.interface import UserIO


class Divorce(Hardship):
    def can_be_targeted(self, player: "Player", game: "Game") -> bool:
        # Vérifie si le joueur possède un métier
        if not player.is_wedding():
            return False
        
        # Vérifie si le joueur est immunisé
        print(f"pouvoir du joueur '{player.name}':", player.get_power())
        if Power.NO_DIVORCE in player.get_power():
            return False
        
        return super().can_be_targeted(player, game)
    def get_name(self) -> str:
        return "Divorce"


    def hardship_effect(self, game: "Game", target: "Player") -> bool:
        """effectue simplement l'effet de la carte"""
        wedding_card = target.get_wedding()
        assert wedding_card is not None
        target.remove_card(wedding_card, game)
        game.add_card_to_discard(wedding_card)

        # Vérification du cas d'adultère
        adultery_card = target.get_adultery()
        if adultery_card:
            print("Cas d'adultère")
            target.remove_card(adultery_card, game)
            game.add_card_to_discard(adultery_card)

            # suppression de tous les enfants
            power = target.get_power()
            if Power.CHILDREN_PROTECTED in power:
                print("[DEBUG] Le joueur {} est protégé de la perte d'enfants".format(target.name))
            else:
                from ...PlayerCardGroup import PlayedCardGroup
                from ..personnals.Children import ChildCard
                for card in target.get_card_from_group(PlayedCardGroup.VIE_PERSONNELLE):
                    if isinstance(card, ChildCard) and not card.is_protected:
                        target.remove_card(card, game)
                        game.add_card_to_discard(card)            
        
        return super().hardship_effect(game, target)
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return False
        assert self.target_player is not None
        self.hardship_effect(game, self.target_player)
        return True

    def get_card_rule(self) -> str:
        return """Le divorce fait perdre son marriage à sa cible. La cible doit etre mariée."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()
