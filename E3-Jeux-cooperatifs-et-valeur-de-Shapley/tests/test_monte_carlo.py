"""Tests de l'estimateur Monte Carlo (Castro et al. 2009)."""

import numpy as np

from shapley.exact import shapley_exact
from shapley.games import airport_game, gloves_game
from shapley.monte_carlo import convergence_curve, shapley_monte_carlo


def test_mc_close_to_exact():
    game = gloves_game(3, 3)
    exact = shapley_exact(game)
    mc = shapley_monte_carlo(game, n_samples=50000, seed=0)
    assert np.max(np.abs(mc - exact)) < 0.02


def test_mc_reproducible():
    game = airport_game([1, 2, 4, 8])
    a = shapley_monte_carlo(game, n_samples=2000, seed=7)
    b = shapley_monte_carlo(game, n_samples=2000, seed=7)
    assert np.allclose(a, b)


def test_mc_unbiased_efficiency_preserved():
    # chaque permutation repartit exactement v(N) -> l'estimateur aussi
    game = airport_game([2, 5, 9])
    mc = shapley_monte_carlo(game, n_samples=1000, seed=1)
    assert abs(mc.sum() - game.grand_coalition_value()) < 1e-9


def test_convergence_decreasing_trend():
    game = gloves_game(3, 4)
    exact = shapley_exact(game)
    curve = convergence_curve(game, exact, [100, 1000, 10000, 40000], seed=3)
    # l'erreur au plus grand m est nettement plus petite qu'au plus petit
    assert curve["errors"][-1] < curve["errors"][0]


def test_mc_std_returned():
    game = gloves_game(2, 3)
    mc, std = shapley_monte_carlo(game, n_samples=5000, seed=0, return_std=True)
    assert mc.shape == std.shape == (5,)
    assert np.all(std >= 0)
