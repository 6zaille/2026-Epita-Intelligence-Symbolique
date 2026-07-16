import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.games import WeightedVotingGame, majority_game
from indices.banzhaf import banzhaf_normalized
from indices.deegan_packel import deegan_packel
from indices.shapley_shubik import shapley_shubik_exact


def test_single_player_is_dictator_with_full_power():
    game = WeightedVotingGame(weights=(1,), quota=1)
    assert game.is_dictator(0)
    for index in (shapley_shubik_exact, banzhaf_normalized, deegan_packel):
        values = index(game)
        assert values[0] == pytest.approx(1.0)


def test_unanimity_game_equalises_power():
    # Quota = poids total : chaque joueur a un veto, donc un pouvoir egal.
    game = WeightedVotingGame(weights=(3, 2, 1), quota=6)
    assert all(game.is_veto(i) for i in game.players)
    ss = shapley_shubik_exact(game)
    for i in game.players:
        assert ss[i] == pytest.approx(1 / 3)


def test_or_game_quota_one_equalises_power():
    # Quota = 1 : toute liste non vide gagne ; par symetrie le pouvoir est egal.
    game = WeightedVotingGame(weights=(5, 3, 1), quota=1)
    bz = banzhaf_normalized(game)
    for i in game.players:
        assert bz[i] == pytest.approx(1 / 3)


def test_majority_game_helper_sets_absolute_majority():
    game = majority_game((10, 8, 6))
    assert game.quota == 24 // 2 + 1


def test_invalid_quota_zero_raises():
    with pytest.raises(ValueError):
        WeightedVotingGame(weights=(2, 1), quota=0)


def test_quota_above_total_raises():
    with pytest.raises(ValueError):
        WeightedVotingGame(weights=(2, 1), quota=99)


def test_negative_weight_raises():
    with pytest.raises(ValueError):
        WeightedVotingGame(weights=(2, -1), quota=1)


def test_names_count_mismatch_raises():
    with pytest.raises(ValueError):
        WeightedVotingGame(weights=(2, 1), quota=2, names=("A",))


def test_empty_game_raises():
    with pytest.raises(ValueError):
        WeightedVotingGame(weights=(), quota=1)
