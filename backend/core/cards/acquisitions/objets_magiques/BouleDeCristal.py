from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class BouleDeCristal(ObjetMagique):
    def cristalEffect(self, game: "Game", current_player: "Player"):
        interface = current_player.get_interface()
        for player in game.players:
            if player == current_player:
                continue

            interface.show_cards(
                title=f"La main du {player.name}",
                prompt="Pouvoir de Boule de Cristal",
                cards=player.hand
            )

        interface.show_cards(
            title=f"Les Cartes de la pioche",
            prompt="Pouvoir de Boule de Cristal",
            cards=game.deck[::-1]
        )

    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        self.cristalEffect(game, current_player)
        return True

    def get_card_rule(self) -> str:
        return """permet de voir les cartes en main et les cartes dans la pioche. Cet effet s'active en posant la carte, puis peut etre réactivé mais en consommant un tour""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    