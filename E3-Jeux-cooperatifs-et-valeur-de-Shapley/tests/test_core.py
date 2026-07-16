"""Tests du coeur, de la convexite et du theoreme de Shapley (1971)."""

import numpy as np

from shapley.core import (
    core_constraints_violation,
    in_core,
    is_convex,
    is_superadditive,
)
from shapley.exact import shapley_exact
from shapley.games import (
    airport_game,
    convex_example,
    empty_core_example,
    gloves_game,
)


def test_convex_game_shapley_in_core():
    game = convex_example()
    assert is_convex(game)
    phi = shapley_exact(game)
    assert in_core(game, phi)


def test_empty_core_shapley_not_in_core():
    game = empty_core_example()
    assert not is_convex(game)
    phi = shapley_exact(game)
    assert not in_core(game, phi)
    # la coalition majoritaire garantit 1 mais recoit < 1
    assert core_constraints_violation(game, phi) > 0.1


def test_airport_is_convex_cost_game():
    # les jeux de couts de l'aeroport sont concaves en cout -> le jeu
    # d'economies associe est convexe ; ici on verifie la superadditivite
    # du jeu de couts au sens min (non requis) : on teste plutot Shapley in core
    game = airport_game([1, 2, 4])
    phi = shapley_exact(game)
    # pour un jeu de couts, la stabilite s'entend "aucune coalition ne paie
    # plus que son cout autonome" : sum_{i in S} phi_i <= c(S)
    n = game.n
    stable = True
    for mask in range(1, 1 << n):
        s = sum(phi[i] for i in range(n) if mask & (1 << i))
        if s > game.value_mask(mask) + 1e-9:
            stable = False
    assert stable


def test_superadditivity():
    assert is_superadditive(gloves_game(2, 2))
    assert is_superadditive(convex_example())


def test_convex_implies_superadditive():
    game = convex_example()
    assert is_convex(game)
    assert is_superadditive(game)
