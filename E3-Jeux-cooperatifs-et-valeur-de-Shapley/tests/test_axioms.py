"""Tests des quatre axiomes de Shapley."""

import numpy as np

from shapley.axioms import (
    check_additivity,
    check_efficiency,
    check_null_player,
    check_symmetry,
    null_players,
    symmetric_pairs,
)
from shapley.exact import shapley_exact
from shapley.game import CooperativeGame
from shapley.games import airport_game, gloves_game


def test_efficiency():
    game = gloves_game(2, 3)
    assert check_efficiency(game, shapley_exact(game))


def test_symmetry_detects_pairs():
    game = gloves_game(2, 2)
    pairs = symmetric_pairs(game)
    assert (0, 1) in pairs and (2, 3) in pairs
    assert check_symmetry(game, shapley_exact(game))


def test_null_player_zero():
    # joueur 2 est nul (n'apparait jamais dans v)
    game = CooperativeGame(3, lambda S: 1.0 if {0, 1} <= set(S) else 0.0)
    assert 2 in null_players(game)
    phi = shapley_exact(game)
    assert check_null_player(game, phi)
    assert abs(phi[2]) < 1e-12


def test_additivity():
    g1 = gloves_game(2, 2)
    g2 = airport_game([1, 2, 3, 4])
    assert check_additivity(g1, g2)


def test_additivity_manual():
    n = 3
    va = [1.0, 2.0, 3.0]
    vb = [0.5, -1.0, 4.0]
    g1 = CooperativeGame(n, lambda S: sum(va[i] for i in S))
    g2 = CooperativeGame(n, lambda S: sum(vb[i] for i in S))
    phi_sum = shapley_exact(CooperativeGame(n, lambda S: sum(va[i] + vb[i] for i in S)))
    assert np.allclose(phi_sum, shapley_exact(g1) + shapley_exact(g2))
