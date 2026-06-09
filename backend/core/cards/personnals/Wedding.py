from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...Game import Game
    from ...Player import Player

from ..Card import Card

class Wedding(Card):
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        if player.get_last_flirt() is None:
            return False, "il faut avoir fait au moins 1 flirt"
        is_wedding = player.get_wedding()
        if is_wedding:
            return False, "Tu es déja marié petit chenapant"
        return super().can_be_played(player, game)

    def can_be_discard(self, player: "Player", game: "Game") -> tuple[bool, str]:
        """vérifie si on peut annuler son marriage ou non"""
        from ...Game import TurnState
        if game.turn_state == TurnState.PIOCHE:
            return True, ""
        return False, "on ne peut divorcer que avant de piocher"
    def get_name(self) -> str:
        return "Marriage"
    def get_card_rule(self) -> str:
        return """Le Marriage peut etre posé a partir du moment où le joueur a poser au moins 1 flirt devant lui. Le marriage permet d'avoir autant d'enfant qu'il souahite et permet d'avoir les prix des maison diviser par 2. Le joueur peut défausser son marriage, pour cela il se défausse de son marriage avant de piocher et cela vas passer son tour."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()

class Adultery(Card):
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        if not player.is_wedding():
            return False, "il faut etre marriée"
        is_adultery = player.get_adultery()
        if is_adultery:
            return False, "Tu es déja en adultère, tu ne crois pas qu'un ca suffit ?"
        return super().can_be_played(player, game)
    def get_name(self) -> str:
        return "Adultère"
    def can_be_discard(self, player: "Player", game: "Game") -> tuple[bool, str]:
        """vérifie si on peut annuler son adultère ou non"""
        from ...Game import TurnState
        if game.turn_state == TurnState.PIOCHE:
            return True, ""
        return False, "on ne peut quitter son adultère que avant de piocher"
    def get_card_rule(self) -> str:
        return """Les adultères permet de continuer a flirter après le marriage, les flirts pendant un adultère ne peuvent pas etre volé. Par contre en cas de divorce, le joueur pert son marriage, son adultère et aussi tous ces enfants. Le joueur peut défausser son adultère a tout moment, alors il ne pert rien, et il jette son adultère dans la défausse. Il ne perd pas de tour a défausser son adultère, il peut le faire a tout moment"""+ "\n"+ "="*10+ "\n" + super().get_card_rule()
