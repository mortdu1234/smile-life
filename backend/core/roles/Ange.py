from typing import TYPE_CHECKING

from backend.userIo.interface import IOType


from .PlayerRole import PlayerRole
from ..PlayerCardGroup import PlayedCardGroup as groupe
from ..Power import Power
if TYPE_CHECKING:
    from backend.core.cards.hardships.Malefices.MaleficeCard import MaleficeCard
    from ..Game import Game
    from ..Player import Player

class Ange(PlayerRole):
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)
        self.powers = [Power.NO_MALEFICES_EFFECT]

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.Eclipse import Eclipse
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, Eclipse):
            return False, "Ce n'est pas le bon ephemeride"
        targets = self.get_available_target(game, owner)
        if len(targets) == 0:
            return False, "Il n'y a pas de cibles possibles"
        return super().can_use_instant_power(game, owner)

    def get_malefices(self, player: "Player") -> "list[MaleficeCard]":
        from ..cards.hardships.Malefices.MaleficeCard import MaleficeCard
        cards = player.get_card_from_group(groupe.HARDSHIP)
        malefices = []
        for card in cards:
            if isinstance(card, MaleficeCard):
                malefices.append(card)
        return malefices
    def get_available_target(self, game: "Game", owner: "Player") -> "list[Player]":
        """récupère l'ensemble des joueurs qui peuvent etre visé pour l'annulation du malus"""
        targets = []
        for player in game.players:
            if player == owner:
                continue
            malefices = self.get_malefices(player)
            if len(malefices) == 0:
                continue

            targets.append(player)
        return targets
     
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""
        targets = self.get_available_target(game, owner)
        interface = owner.get_interface()

        target = interface.ask_player(
            prompt="Selectionner un joueur a qui vous aller annuler un maléfice",
            players=targets,
            kind=IOType.PLAYER_PICKER
        )
        assert target is not None, "aucun joueur selectionnée"

        malefices = self.get_malefices(target)
        malefice = interface.ask_card(
            prompt="Selectionner un joueur a qui vous aller annuler un maléfice",
            cards=malefices, # type: ignore
            kind=IOType.CARD_PICKER
        )
        assert malefice is not None, "aucun malefice selectionnée"
        malefice.discard_card(game, target)
        
        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return "PP : ne peut subir d'effet de maléfices\n PE (Eclipe) : annule le maléfice d'un joueur"+ "\n"+ "="*10+ "\n" + super().get_card_rule()
