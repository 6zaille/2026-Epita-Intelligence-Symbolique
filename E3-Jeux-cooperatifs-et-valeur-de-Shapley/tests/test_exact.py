"""Tests de correction du calcul exact de la valeur de Shapley."""

import numpy as np
import pytest

from shapley.exact import shapley_by_permutations, shapley_exact
from shapley.game import CooperativeGame
from shapley.games import (
    airport_game,
    gloves_game,
    un_security_council_game,
)


def test_gloves_1_2_known_values():
    # 1 gant gauche (rare) vs 2 droits : L=2/3, R=1/6 chacun
    game = gloves_game(1, 2)
    phi = shapley_exact(game)
    assert np.allclose(phi, [2 / 3, 1 / 6, 1 / 6])


def test_airport_known_values():
    # couts [1,2,4] : parts 1/3, 5/6, 17/6
    game = airport_game([1, 2, 4])
    phi = shapley_exact(game)
    assert np.allclose(phi, [1 / 3, 5 / 6, 17 / 6])


def test_coalition_vs_permutation_agree():
    for game in [gloves_game(2, 3), airport_game([1, 3, 3, 7]), gloves_game(1, 4)]:
        assert np.allclose(shapley_exact(game), shapley_by_permutations(game))


def test_efficiency_holds():
    for game in [gloves_game(2, 2), airport_game([2, 5, 9]),
                 un_security_council_game()]:
        phi = shapley_exact(game)
        assert abs(phi.sum() - game.grand_coalition_value()) < 1e-9


def test_unsc_literature_values():
    game = un_security_council_game()
    phi = shapley_exact(game)
    # valeurs de reference (litterature)
    assert phi[0] == pytest.approx(0.196265, abs=1e-5)   # permanent
    assert phi[5] == pytest.approx(0.001865, abs=1e-5)   # non-permanent
    assert phi[:5].sum() == pytest.approx(0.98133, abs=1e-4)


def test_additive_game_equals_own_values():
    # jeu additif v(S) = sum a_i : Shapley = a
    a = [3.0, -1.0, 5.0, 2.0]
    game = CooperativeGame(4, lambda S: sum(a[i] for i in S))
    assert np.allclose(shapley_exact(game), a)


def test_dummy_game_dictator():
    # v(S)=1 ssi joueur 0 present : Shapley = (1,0,0)
    game = CooperativeGame(3, lambda S: 1.0 if 0 in S else 0.0)
    assert np.allclose(shapley_exact(game), [1.0, 0.0, 0.0])


def test_empty_game():
    game = CooperativeGame(0, lambda S: 0.0)
    assert shapley_exact(game).shape == (0,)
