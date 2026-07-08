
from .SpecialCard import SpecialCard
from typing import TYPE_CHECKING
from ...Power import Power
from random import shuffle
if TYPE_CHECKING:
    from ..professionnals.JobCard import JobCard
    from ....userIo.interface import UserIO
    from ...Game import Game
    from ...Player import Player
    from ..Card import Card

class RedistributionTaches(SpecialCard):    
    def can_be_played(self, player: "Player", game: "Game") -> tuple[bool, str]:
        return super().can_be_played(player, game)
    
    def get_name(self) -> str:
        return "Redistribution Des Taches"
    
    def apply_card_effect(self, game: "Game", current_player: "Player") -> bool:
        players = game.players
        available_player: "list[Player]" = []
        available_job: "list[JobCard]" = []
        for player in players:
            job = player.get_job()
            if job:
                available_player.append(player)
                available_job.append(job)
        shuffle(available_job)
        for idx, player in enumerate(available_player):
            job = player.get_job()
            new_job = available_job[idx]
            assert job is not None, "erreur"
            if job == new_job:
                continue
            player.remove_card(job, game)
            player.add_card_to_hand(new_job)
            new_job.play_card(game, player)

        return super().apply_card_effect(game, current_player)

    def discard_card(self, game: "Game", owner: "Player") -> None:
        return super().discard_card(game, owner)
    
    def get_card_rule(self) -> str:
        return """Redistribue aléatoirement l'ensemble des métiers posé."""+ "\n"+ "="*10+ "\n" + super().get_card_rule()