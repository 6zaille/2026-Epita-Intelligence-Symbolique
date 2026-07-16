import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.games import WeightedVotingGame
from indices.banzhaf import banzhaf_absolute, banzhaf_normalized
from indices.deegan_packel import deegan_packel
from indices.shapley_shubik import shapley_shubik_exact, shapley_shubik_monte_carlo


def _approx(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def test_shapley_shubik_three_player_apex():
    game = WeightedVotingGame(weights=(2, 1, 1), quota=3)
    ss = shapley_shubik_exact(game)
    assert _approx(ss[0], 4 / 6)
    assert _approx(ss[1], 1 / 6)
    assert _approx(ss[2], 1 / 6)
    assert _approx(sum(ss.values()), 1.0)


def test_banzhaf_three_player_apex():
    game = WeightedVotingGame(weights=(2, 1, 1), quota=3)
    bz = banzhaf_normalized(game)
    assert _approx(bz[0], 3 / 5)
    assert _approx(bz[1], 1 / 5)
    assert _approx(bz[2], 1 / 5)


def test_paradox_small_party_equal_power():
    game = WeightedVotingGame(weights=(49, 48, 3), quota=51)
    ss = shapley_shubik_exact(game)
    bz = banzhaf_normalized(game)
    for i in game.players:
        assert _approx(ss[i], 1 / 3)
        assert _approx(bz[i], 1 / 3)


def test_dictator_holds_all_power():
    game = WeightedVotingGame(weights=(5, 1, 1), quota=4)
    assert game.is_dictator(0)
    ss = shapley_shubik_exact(game)
    assert _approx(ss[0], 1.0)
    assert _approx(ss[1], 0.0)
    assert _approx(ss[2], 0.0)


def test_dummy_player_has_zero_power():
    game = WeightedVotingGame(weights=(2, 2, 1), quota=4)
    assert game.is_dummy(2)
    for index in (shapley_shubik_exact, banzhaf_normalized, deegan_packel):
        values = index(game)
        assert _approx(values[2], 0.0)


def test_unsc_shapley_shubik_permanent_members():
    weights = (7,) * 5 + (1,) * 10
    game = WeightedVotingGame(weights=weights, quota=39)
    ss = shapley_shubik_exact(game)
    for i in range(5):
        assert ss[i] == pytest.approx(0.19627, abs=1e-4)
    for i in range(5, 15):
        assert ss[i] == pytest.approx(0.001865, abs=1e-4)
    assert sum(ss.values()) == pytest.approx(1.0, abs=1e-9)


def test_efficiency_sums_to_one():
    game = WeightedVotingGame(weights=(10, 8, 6, 4, 2), quota=16)
    for index in (shapley_shubik_exact, banzhaf_normalized, deegan_packel):
        values = index(game)
        assert sum(values.values()) == pytest.approx(1.0, abs=1e-9)


def test_monte_carlo_converges_to_exact():
    game = WeightedVotingGame(weights=(8, 5, 4, 3, 2), quota=12)
    exact = shapley_shubik_exact(game)
    approx = shapley_shubik_monte_carlo(game, n_samples=200_000, seed=7)
    for i in game.players:
        assert approx[i] == pytest.approx(exact[i], abs=5e-3)


def test_banzhaf_absolute_is_probability():
    game = WeightedVotingGame(weights=(6, 4, 3, 2), quota=8)
    bz_abs = banzhaf_absolute(game)
    for value in bz_abs.values():
        assert 0.0 <= value <= 1.0
