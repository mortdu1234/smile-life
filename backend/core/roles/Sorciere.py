import random
from typing import TYPE_CHECKING

from .PlayerRole import PlayerRole
from ..Power import Power
from ..PlayerCardGroup import PlayedCardGroup as groupe
if TYPE_CHECKING:
    from backend.core.cards.personnals.Children import ChildCard
    from ..Game import Game
    from ..Player import Player

class Sorciere(PlayerRole):
    def __init__(self, img_path: str) -> None:
        super().__init__(img_path)
        self.powers = [Power.FREE_POTION]

    def can_use_instant_power(self, game: "Game", owner: "Player") -> "tuple[bool, str]":
        """vérifie si le joueur peut jouer son pouvoir de role"""
        from ..cards.ephemerides.PleineLune import PleineLune
        ephemeride = game.get_ephemeride()
        if not isinstance(ephemeride, PleineLune):
            return False, "Ce n'est pas le bon ephemeride"
        return super().can_use_instant_power(game, owner)

    def get_all_children(self, target: "Player") -> "list[ChildCard]":
        from backend.core.cards.personnals.Children import ChildCard
        zone = target.get_card_from_group(groupe.VIE_PERSONNELLE)
        children = []
        for card in zone:
            if isinstance(card, ChildCard) and not card.is_protected:
                children.append(card)
        random.shuffle(children)
        return children
        
     
    def apply_instant_power(self, game: "Game", owner: "Player"):
        """applique le pouvoir instantannée du role"""
        from ..cards.personnals.Children import MaleChild, FemaleChild, GirlPowerChild
        interface = owner.get_interface()
        for player in game.players:
            if player == owner:
                continue

            # récupération des enfants
            children = self.get_all_children(player)
            # récupération du choix
            choix = interface.choice(
                prompt=f"Choisi le type d'enfant que tu veux récupérer pour {player.name}",
                choices=["Garcon", "Fille", "Girl Power"]
            )
            compare_class = None
            match choix:
                case "Garcon":
                    compare_class = MaleChild
                case "Fille":
                    compare_class = FemaleChild
                case "Girl Power":
                    compare_class = GirlPowerChild
            assert compare_class is not None, "erreur aucun choix fait"
            for card in children:
                if isinstance(card, compare_class):
                    player.remove_card(card, game)
                    owner.add_card_to_played(card)
                else:
                    break
            
        return super().apply_instant_power(game, owner)
        
    def get_card_rule(self) -> str:
        return "PP : permet de poser des potions gratuitement | PE (Plein Lune) : Pour chaque joueur, vous selectionner entre Garcon, Fille et GirlPower, ensuite vous mélanger toutes les cartes enfants posé du joueur et vous les retournez une par une, si l'enfant correpond a votre choix, alors vous le posez face a vous sans conditions, sinon c'est la fin de la selection et vous passez au joueur suivant."+ "\n"+ "="*10+ "\n" + super().get_card_rule()
