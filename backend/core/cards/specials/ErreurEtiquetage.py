from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
from ...Power import Power
from ...PlayerCardGroup import PlayedCardGroup as groupe
from ....userIo.interface import IOType
if TYPE_CHECKING:
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ..Card import Card
    from ..personnals.Children import ChildCard

class ErreurEtiquetage(SpecialCard):    
    def get_children(self, player: "Player") -> "list[ChildCard]":
        from ..personnals.Children import ChildCard
        children = []
        card_played = player.get_card_from_group(groupe.VIE_PERSONNELLE)
        for card in card_played:
            if isinstance(card, ChildCard):
                children.append(card)
        return children


    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        owner_children = self.get_children(player)
        if len(owner_children) == 0:
            return False, "Vous n'avez pas d'enfants posé"
        players = game.players
        other_cards = []
        for player_i in players:
            if player_i == player:
                continue
            other_cards.append(len(self.get_children(player_i)))
        if sum(other_cards) == 0:
            return False, "Personne ne possède d'enfant posé"
        return super().can_be_played(player, game)
    
    def get_name(self) -> str:
        return "Erreur d'étiquetage"

    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        owner_children = self.get_children(current_player)
        other_players = [p for p in game.players if p != current_player]
        other_cards: "list[list[ChildCard]]" = [self.get_children(p) for p in other_players]

        interface = current_player.get_interface()
        owner_card, target_card, target_player = interface.erreur_detiquetage_interface(
            owner=current_player,
            others=other_players,
            children_owner=owner_children,
            children_others=other_cards,
        )

        target_player.remove_card(target_card, game)
        current_player.remove_card(owner_card, game)
        target_player.add_card_to_played(owner_card)
        current_player.add_card_to_played(target_card)

        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: "Game", owner: "Player") -> None:
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """Permet d'échanger un de ces enfants avec l'enfant d'un autre joueur"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()