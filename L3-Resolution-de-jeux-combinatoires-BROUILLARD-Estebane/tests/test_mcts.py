"""Tests de l'agent MCTS (étape 4).

Vérifie : coups légaux, respect du budget, exposition des visites par coup,
correction tactique (trouve un mat en 1, bloque une menace), et qu'un budget
plus large produit un jeu au moins aussi fort (bat nettement le hasard).
"""

import math

from agents.mcts import MCTSAgent
from agents.random_agent import RandomAgent
from game.connect_four import PLAYER1, ConnectFour
from tournament.runner import play_match


def make_game(moves):
    g = ConnectFour()
    for c in moves:
        g.play_move(c)
    return g


def test_mcts_plays_legal_move():
    g = ConnectFour()
    agent = MCTSAgent(n_simulations=200, seed=0)
    assert agent.move(g) in g.legal_moves()


def test_budget_simulations_honored():
    g = ConnectFour()
    agent = MCTSAgent(n_simulations=300, seed=0)
    agent.move(g)
    assert agent.last_simulations == 300


def test_visit_counts_exposed_and_sum():
    g = ConnectFour()
    agent = MCTSAgent(n_simulations=500, seed=1)
    agent.move(g)
    # Une entrée par coup légal au plus, et la somme des visites des enfants
    # de la racine vaut le nombre de simulations (chaque sim visite un enfant).
    assert set(agent.last_visit_counts).issubset(set(g.legal_moves()))
    assert sum(agent.last_visit_counts.values()) == agent.last_simulations
    assert set(agent.last_win_rates) == set(agent.last_visit_counts)


def test_time_budget_honored():
    import time
    g = ConnectFour()
    agent = MCTSAgent(n_simulations=None, time_budget=0.2, seed=0)
    t0 = time.perf_counter()
    agent.move(g)
    elapsed = time.perf_counter() - t0
    # Tolérance large : le budget temps doit être globalement respecté.
    assert 0.1 < elapsed < 1.0
    assert agent.last_simulations > 0


def test_mcts_takes_immediate_win():
    # J1 menace de compléter col 3 (mat en 1) ; MCTS doit le trouver.
    g = make_game([0, 0, 1, 1, 2, 2])
    assert g.current_player == PLAYER1
    agent = MCTSAgent(n_simulations=800, seed=2)
    assert agent.move(g) == 3


def test_mcts_blocks_immediate_threat():
    # J2 menace col 4 (cf. test alpha-beta) ; J1 doit bloquer en 4.
    g = make_game([0, 1, 5, 2, 6, 3])
    assert g.current_player == PLAYER1
    agent = MCTSAgent(n_simulations=1500, seed=3)
    assert agent.move(g) == 4


def test_mcts_beats_random_decisively():
    mcts = MCTSAgent(n_simulations=400, seed=4)
    rnd = RandomAgent(seed=5)
    out = play_match(mcts, rnd, n_games=20)
    # MCTS avec quelques centaines de simulations doit dominer le hasard.
    assert out["wins_a"] >= 16
