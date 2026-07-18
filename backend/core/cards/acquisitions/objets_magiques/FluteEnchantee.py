from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
import random
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class FluteEnchantee(ObjetMagique):
    def get_player_available_card(self, player: "Player"):
        from ...animals.AnimalCard import AnimalCard
        cards=player.get_card_from_group(groupe.ANIMALS)
        res = []
        for card in cards:
            if isinstance(card, AnimalCard) and not card.is_protected:
                res.append(card)
        return res
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success

        # calcul des joueurs valides
        available_players = []
        for player in game.players:
            if player == current_player:
                continue
            available_cards = self.get_player_available_card(player)
            if len(available_cards) == 0:
                continue
            available_players.append(player)

        if len(available_players) == 0:
            return True 

        # demande de selection de la cible
        interface = current_player.get_interface()
        target_player = interface.ask_player(
            prompt="selection du joueur cible pour voler un animal aléatoirement",
            players=available_players,
            kind=IOType.PLAYER_PICKER
        )
        assert target_player is not None, "error le joueur n'est pas selectionné"

        # selection de l'animal ciblé
        cards = self.get_player_available_card(target_player)
        selected_card = random.choice(cards)

        print(f"[DEBUG] la carte selectionnée est {selected_card}")
        # getion du vol de carte
        current_player.add_card_to_played(selected_card)
        target_player.remove_card(selected_card, game)

        return True

        
    def get_card_rule(self) -> str:
        return """récupère un animal posé du joueur de mon choix (cet animal est choisi aléatoirement)""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    