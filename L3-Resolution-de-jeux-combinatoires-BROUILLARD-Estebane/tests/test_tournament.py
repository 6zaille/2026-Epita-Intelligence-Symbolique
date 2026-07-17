"""Tests du tournoi instrumenté (étape 6)."""

import numpy as np

from agents.alphabeta import AlphaBetaAgent
from agents.random_agent import RandomAgent
from tournament.runner import run_tournament, strength_vs_budget


def test_tournament_matrix_shapes_and_consistency():
    agents = [RandomAgent(seed=i) for i in range(3)]
    for i, a in enumerate(agents):
        a.name = f"R{i}"
    res = run_tournament(agents, n_games=6, verbose=False)

    n = 3
    assert res.score_matrix.shape == (n, n)
    # Diagonale non définie (un agent ne joue pas contre lui-même).
    assert all(np.isnan(res.score_matrix[i, i]) for i in range(n))
    # Cohérence : wins[i,j] == losses[j,i].
    for i in range(n):
        for j in range(n):
            assert res.wins_matrix[i, j] == res.losses_matrix[j, i]
    # Scores symétriques complémentaires : s[i,j] + s[j,i] == 1 (hors diagonale).
    for i in range(n):
        for j in range(n):
            if i != j:
                assert abs(res.score_matrix[i, j] + res.score_matrix[j, i] - 1.0) < 1e-9
    # Temps de réflexion mesurés pour chaque agent.
    assert set(res.avg_move_time) == {"R0", "R1", "R2"}
    assert all(t >= 0 for t in res.avg_move_time.values())


def test_alphabeta_beats_random_in_tournament():
    ab = AlphaBetaAgent(depth=3, name="AB")
    rnd = RandomAgent(seed=0)
    rnd.name = "Rand"
    res = run_tournament([ab, rnd], n_games=10, verbose=False)
    # L'alpha-beta doit largement dominer le hasard.
    i = res.names.index("AB")
    j = res.names.index("Rand")
    assert res.score_matrix[i, j] > 0.8


def test_strength_vs_budget_increases_with_depth():
    rnd = RandomAgent(seed=1)
    winrates = strength_vs_budget(
        lambda d: AlphaBetaAgent(depth=int(d)),
        rnd,
        budgets=[1, 3],
        n_games=10,
    )
    assert len(winrates) == 2
    assert all(0.0 <= w <= 1.0 for w in winrates)
    # Une profondeur 3 doit battre le hasard au moins aussi bien qu'une profondeur 1.
    assert winrates[1] >= winrates[0] - 0.1
