from typing import TYPE_CHECKING

from ....Power import Power
from .....userIo.interface import IOType
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player
from .PotionCard import Potion

class ChancePotion(Potion):

    def apply_potion_effect(self, game: "Game", current_player: "Player"):
        turn = min(10, len(game.deck))
        next_10_cards = [game.deck[i] for i in range(turn)]
        interface = current_player.get_interface()
        selected_card = interface.ask_card(
            prompt="selectionner une carte pour pouvoir rejouer derriere",
            cards=next_10_cards,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None, "erreur, aucune carte selectionnees"

        game.deck.remove(selected_card)
        current_player.add_card_to_hand(selected_card)
        from ....Game import GameStateKey
        game.game_state[GameStateKey.CHANCE] += 1

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success
        self.apply_potion_effect(game, current_player)
        return True
        
    def get_card_rule(self) -> str:
        return """Choisissez une carte parmis les 10 prochaines cartes de la pioche puis rejouer (les autres cartes sont laissé dans la pioche)""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
        