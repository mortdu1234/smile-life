from .ObjetMagique import ObjetMagique
from typing import TYPE_CHECKING
from ....Power import Power
from ....PlayerCardGroup import PlayedCardGroup as groupe
from .....userIo.interface import IOType
if TYPE_CHECKING:
    from backend.core.Game import Game
    from backend.core.Player import Player

class Grimoire(ObjetMagique):
    def calcul_cost(self, player: "Player", game: "Game") -> int:
        from backend.core.roles.Magicien import Magicien
        role = player.get_role()
        if isinstance(role, Magicien):
            return 0
        return super().calcul_cost(player, game)
    
    def get_player_available_card(self, player: "Player"):
        from ...professionnals.StudyCard import StudyCard
        cards=player.get_card_from_group(groupe.VIE_PROFESSIONNELLE)
        res = []
        for card in cards:
            if isinstance(card, StudyCard) and not card.is_protected:
                res.append(card)
        return res
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        success = super().apply_card_effect(game, current_player)
        if not success:
            return success

        # selection du joueur cible
        targets_players = []
        players = game.players
        for player in players:
            if player == current_player:
                continue
            available_cards = self.get_player_available_card(player)
            if len(available_cards) == 0:
                continue
            targets_players.append(player)

        # demande de la cible
        interface = current_player.get_interface()
        target_player = interface.ask_player(
            prompt="selection du joueur cible pour voler un étude",
            players=targets_players,
            kind=IOType.PLAYER_PICKER
        )
        assert target_player is not None, "error le joueur n'est pas selectionné"

        # détermination des cartes valides
        cards = self.get_player_available_card(target_player)

        # selection de la carte
        selected_card = interface.ask_card(
            prompt="selection de la carte d'étude",
            cards=cards,
            kind=IOType.CARD_PICKER
        )
        assert selected_card is not None, "error la carte n'est pas selectionné"

        # récupération
        target_player.remove_card(selected_card, game)
        current_player.add_card_to_played(selected_card)
        current_player.move_placed_cards(selected_card, groupe.VIE_PROFESSIONNELLE, groupe.CARTES_PROTEGEES)

        return True
    
    def get_card_rule(self) -> str:
        return """vole une carte étude de votre choix a un joueur de votre choix et la pose sans condition et sans compter dans la limite. Gratuit pour le magicien""" + "\n"+ "="*10+ "\n" + super().get_card_rule()
    