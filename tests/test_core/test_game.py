"""
tests/test_core/test_game.py — Tests du moteur de jeu pur (sans Flask).
"""
import pytest
from app.core.player import Player
from app.core.game import Game
from app.cards.concrete.professional.study_salary import StudyCard, SalaryCard
from app.cards.concrete.hardship.cards import AccidentCard, MaladieCard


def make_game(num_players: int = 2) -> tuple[Game, list[Player]]:
    players = [Player(i, f"Joueur{i}") for i in range(num_players)]
    game = Game("test-game", [], num_players)
    for p in players:
        game.add_player(p)
    return game, players


class TestPlayer:
    def test_initial_state(self):
        player = Player(0, "Alice")
        assert player.hand == []
        assert not player.has_job()
        assert not player.is_married()
        assert player.get_available_salary_sum() == 0

    def test_add_study_card(self):
        player = Player(0, "Alice")
        study = StudyCard("bac", 2, "")
        player.add_card_to_played(study)
        assert player.count_studies() == 2

    def test_can_play_salary_without_job(self):
        game, players = make_game()
        salary = SalaryCard(1, "")
        ok, reason = salary.can_be_played(players[0], game)
        assert not ok
        assert "métier" in reason

    def test_accident_skips_turn(self):
        game, players = make_game()
        accident = AccidentCard("")
        accident.apply_effect(game, players[1], players[0])
        assert players[1].skip_turns == 1

    def test_calculate_smiles_empty(self):
        player = Player(0, "Alice")
        assert player.calculate_smiles() == 0
