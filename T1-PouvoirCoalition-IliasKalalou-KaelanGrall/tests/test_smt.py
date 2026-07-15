import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.games import WeightedVotingGame
from formal.smt_encoding import (
    count_swings_smt,
    enumerate_minimal_winning_smt,
    is_dictator_smt,
    is_dummy_smt,
    is_veto_smt,
)
from formal.smt_indices import banzhaf_smt, deegan_packel_smt, shapley_shubik_smt
from indices.banzhaf import banzhaf_normalized, swing_counts
from indices.deegan_packel import deegan_packel
from indices.shapley_shubik import shapley_shubik_exact

GAMES = [
    WeightedVotingGame(weights=(2, 1, 1), quota=3),
    WeightedVotingGame(weights=(49, 48, 3), quota=51),
    WeightedVotingGame(weights=(5, 1, 1), quota=4),
    WeightedVotingGame(weights=(3, 3, 1), quota=4),
    WeightedVotingGame(weights=(10, 8, 6, 4, 2), quota=16),
]


@pytest.mark.parametrize("game", GAMES)
def test_veto_smt_matches_combinatorial(game):
    for i in game.players:
        assert is_veto_smt(game, i) == game.is_veto(i)


@pytest.mark.parametrize("game", GAMES)
def test_dummy_smt_matches_combinatorial(game):
    for i in game.players:
        assert is_dummy_smt(game, i) == game.is_dummy(i)


@pytest.mark.parametrize("game", GAMES)
def test_dictator_smt_matches_combinatorial(game):
    for i in game.players:
        assert is_dictator_smt(game, i) == game.is_dictator(i)


@pytest.mark.parametrize("game", GAMES)
def test_swing_counts_smt_matches_combinatorial(game):
    combinatorial = swing_counts(game)
    smt = {i: count_swings_smt(game, i) for i in game.players}
    assert combinatorial == smt


@pytest.mark.parametrize("game", GAMES)
def test_minimal_winning_smt_matches_combinatorial(game):
    combinatorial = {frozenset(c) for c in game.minimal_winning_coalitions()}
    smt = set(enumerate_minimal_winning_smt(game))
    assert combinatorial == smt


@pytest.mark.parametrize("game", GAMES)
def test_shapley_shubik_smt_matches_enumeration(game):
    smt = shapley_shubik_smt(game)
    exact = shapley_shubik_exact(game)
    for i in game.players:
        assert smt[i] == pytest.approx(exact[i], abs=1e-9)


@pytest.mark.parametrize("game", GAMES)
def test_banzhaf_smt_matches_enumeration(game):
    smt = banzhaf_smt(game)
    exact = banzhaf_normalized(game)
    for i in game.players:
        assert smt[i] == pytest.approx(exact[i], abs=1e-9)


@pytest.mark.parametrize("game", GAMES)
def test_deegan_packel_smt_matches_enumeration(game):
    smt = deegan_packel_smt(game)
    exact = deegan_packel(game)
    for i in game.players:
        assert smt[i] == pytest.approx(exact[i], abs=1e-9)
