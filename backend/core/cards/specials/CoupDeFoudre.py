

from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
from ...Power import Power
from ....userIo.interface import IOType
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ..Card import Card

class CoupDeFoudre(SpecialCard):    
    def _get_available_target(self, game: "Game", current_player: "Player") -> "list[Player]":
        available_targets = []
        for target in game.players:
            if target==current_player:
                continue
            if target.is_wedding():
                available_targets.append(target)
        return available_targets

    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        if player.is_wedding():
            return False, "Tu es déjà marié, tu ne crois pas qu'une ca suffit ?"
        targets = self._get_available_target(game, player)
        if len(targets) == 0:
            return False, "Il n'y a pas de marriage posé."
        return super().can_be_played(player, game)
    
    def get_name(self) -> str:
        return "Coup De Foudre"
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        targets = self._get_available_target(game, current_player)
        interface = current_player.get_interface()
        selected_target = interface.ask_player(
            prompt="selection du joueur a qui tu vas voler le marriage",
            players=targets,
            kind=IOType.PLAYER_PICKER
        )
        assert selected_target is not None, "Aucune carte selectionnées"
        wedding_card = selected_target.get_wedding()
        assert wedding_card is not None, "error"
        selected_target.remove_card(wedding_card, game)
        current_player.add_card_to_played(wedding_card)
        
        return super().apply_card_effect(game, current_player)
    
    def get_card_rule(self) -> str:
        return """Permet de voler un marriage posé de son choix et de le poser directement (sans condition). Ne peut pas etre posé dans le cas ou le joueur possède déja un marriage, ne peut pas etre posé si aucun autre joueurs ne possède de marriage posé."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()