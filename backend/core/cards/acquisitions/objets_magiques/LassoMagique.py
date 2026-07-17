from matplotlib.style import available

from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class LassoMagique(ObjetMagique):
    def calcul_cost(self, player: "Player", game: "Game") -> int:
        from backend.core.cards.personnals.Children import DianaChild
        zone = player.get_card_from_group(groupe.VIE_PERSONNELLE) + player.get_card_from_group(groupe.CARTES_PROTEGEES) 
        for card in zone:
            if isinstance(card, DianaChild):
                return 0
        return super().calcul_cost(player, game)
    
    def get_available_cards(self, player: "Player", game: "Game", current_player: "Player"):
        cards = player.get_card_from_group(groupe.ACQUISITIONS)
        cards += player.get_card_from_group(groupe.CARTES_SPECIALES)
        cards += player.get_card_from_group(groupe.VIE_PERSONNELLE)
        cards += player.get_card_from_group(groupe.VIE_PROFESSIONNELLE)
        available = []
        for card in cards:
            success, reason = card.can_be_played(current_player, game)
            if success:
                available.append(card)
        return available

                        
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success

        # récupération des joueurs valides
        players_available = []
        for player in game.players:
            if player==current_player:
                continue
            cards = self.get_available_cards(player, game, current_player)
            if len(cards)>0:
                players_available.append(player)

        # demande de la sélection du joueur
        interface = current_player.get_interface()

        target_player = interface.ask_player(
            prompt="selectionner un joueur a qui vous allez voler une carte posé",
            players=players_available,
            kind=IOType.PLAYER_PICKER
        )
        assert target_player is not None, "aucune player selectionnee"

        # récupération des cartes disponible du joueur
        available = self.get_available_cards(target_player, game, current_player)

        selected_card = interface.ask_card(
            prompt="selectionner la carte que vous allez poser",
            cards=available,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None, "acune carte selectionnee"

        # gestion du transfer
        target_player.remove_card(selected_card, game)
        current_player.add_card_to_hand(selected_card)
        selected_card.play_card(game, current_player)

        return True
        
    def get_card_rule(self) -> str:
        return """permet de voler une carte posé d'un joueur pour la poser devant vous (cela doit respecter les règles du jeu).Gratuit si vous avez diana""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    