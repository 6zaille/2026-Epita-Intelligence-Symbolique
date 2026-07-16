"""Smoke tests des fonctions de visualisation (headless, backend Agg).

On vérifie que les figures se construisent sans erreur et renvoient des objets
matplotlib cohérents. Le rendu fin est jugé visuellement dans le notebook ; ici
on protège seulement contre les régressions cassantes. Le widget interactif
(ipywidgets) n'est pas testé ici car il requiert un noyau notebook.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agents.alphabeta import AlphaBetaAgent
from agents.mcts import MCTSAgent
from agents.random_agent import RandomAgent
from game.connect_four import ConnectFour
from tournament.runner import run_tournament
from viz.board import agent_thoughts, draw_board, draw_thoughts
from viz.pruning import plot_nodes_vs_depth, plot_pruning_comparison, plot_search_tree
from viz.style import agent_color, apply_style
from viz.tournament_viz import (
    plot_ranking,
    plot_speed_vs_strength,
    plot_strength_vs_budget,
    plot_winrate_heatmap,
)


def setup_module(module):
    apply_style()


def make_game(moves):
    g = ConnectFour()
    for c in moves:
        g.play_move(c)
    return g


def test_style_agent_color():
    assert agent_color("AlphaBeta-d5").startswith("#")
    assert agent_color("Inconnu") == agent_color("Random")


def test_pruning_tree_builds():
    g = make_game([3, 3, 4, 2])
    fig, ax, nodes = plot_search_tree(g, depth=3)
    assert nodes > 0
    plt.close(fig)


def test_nodes_vs_depth_builds():
    g = make_game([3, 3])
    fig, ax, data = plot_nodes_vs_depth(g, depths=[1, 2, 3])
    # minimax explore au moins autant que la variante optimisée.
    assert data["minimax"][-1] >= data["+ αβ + TT + ordre"][-1]
    plt.close(fig)


def test_pruning_comparison_builds():
    g = make_game([3, 3, 4])
    fig, ax, vals = plot_pruning_comparison(g, depth=5)
    assert vals["minimax"] >= vals["+ αβ"]
    plt.close(fig)


def test_board_and_thoughts_build():
    g = make_game([3, 3, 4, 2])
    fig, ax = draw_board(g)
    plt.close(fig)

    ab = AlphaBetaAgent(depth=4)
    scores, label = agent_thoughts(ab, g)
    assert "αβ" in label
    assert set(scores).issubset(set(range(7)))
    fig, ax = draw_thoughts(scores, label)
    plt.close(fig)


def test_thoughts_uniform_across_agents():
    g = make_game([3, 3])
    for agent, key in [
        (AlphaBetaAgent(depth=3), "αβ"),
        (MCTSAgent(n_simulations=100, seed=0), "MCTS"),
    ]:
        scores, label = agent_thoughts(agent, g)
        assert scores
        assert key in label


def test_tournament_viz_build():
    agents = [RandomAgent(seed=i) for i in range(3)]
    for i, a in enumerate(agents):
        a.name = ["AlphaBeta", "MCTS", "DQN"][i]  # noms reconnus par la palette
    res = run_tournament(agents, n_games=4, verbose=False)
    for fn in (plot_winrate_heatmap, plot_ranking, plot_speed_vs_strength):
        fig, ax = fn(res)
        plt.close(fig)


def test_strength_vs_budget_build():
    fig, ax = plot_strength_vs_budget(
        budgets=[1, 2, 3],
        curves={"AlphaBeta": [0.5, 0.7, 0.9], "MCTS": [0.6, 0.65, 0.7]},
    )
    plt.close(fig)
