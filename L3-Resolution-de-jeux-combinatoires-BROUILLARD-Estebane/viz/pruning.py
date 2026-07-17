"""Visualisation 1 : rendre l'élagage alpha-beta VISIBLE (Knuth & Moore 1975).

Deux figures complémentaires :

A. `plot_search_tree` : dessine l'arbre de recherche d'une position et colore en
   rouge les branches coupées par l'élagage αβ (jamais explorées). On voit
   littéralement le travail évité.

B. `plot_nodes_vs_depth` / `plot_pruning_comparison` : compare le NOMBRE de nœuds
   explorés selon les optimisations (minimax pur, +αβ, +TT, +move ordering), en
   fonction de la profondeur. C'est la mesure quantitative de l'argument de
   Knuth & Moore : à résultat identique, l'élagage réduit le coût de plusieurs
   ordres de grandeur.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np

from agents.alphabeta import AlphaBetaAgent, SearchNode
from game.connect_four import ConnectFour
from viz.style import PALETTE

# Configurations d'ablation comparées (ordre = ajout incrémental d'optimisations).
ABLATIONS: List[Tuple[str, dict]] = [
    ("minimax", dict(use_alpha_beta=False, use_transposition=False, use_move_ordering=False)),
    ("+ αβ", dict(use_alpha_beta=True, use_transposition=False, use_move_ordering=False)),
    ("+ αβ + TT", dict(use_alpha_beta=True, use_transposition=True, use_move_ordering=False)),
    ("+ αβ + TT + ordre", dict(use_alpha_beta=True, use_transposition=True, use_move_ordering=True)),
]
ABLATION_COLORS = ["#9aa0a6", "#e07a1f", "#3a9b76", "#1b6ca8"]


# --------------------------------------------------------------------------- #
# A. Arbre de recherche avec branches élaguées
# --------------------------------------------------------------------------- #
def _count_leaves(node: SearchNode, max_depth: int, depth: int = 0) -> int:
    """Nombre de feuilles dessinées sous `node` (pour la mise en page horizontale)."""
    if node.pruned or depth >= max_depth or not node.children:
        return 1
    return sum(_count_leaves(c, max_depth, depth + 1) for c in node.children)


def _layout(
    node: SearchNode,
    max_depth: int,
    x_start: float,
    depth: int,
    positions: Dict[int, Tuple[float, float]],
    edges: List[Tuple[int, int, bool]],
    parent_id: Optional[int],
) -> float:
    """Assigne récursivement des coordonnées (x, y) aux nœuds à dessiner.

    Renvoie la largeur (en nombre de feuilles) occupée par le sous-arbre.
    `edges` reçoit (parent_id, node_id, pruned) ; positions est indexé par id().
    """
    node_id = id(node)
    if node.pruned or depth >= max_depth or not node.children:
        x = x_start
        positions[node_id] = (x, -depth)
        if parent_id is not None:
            edges.append((parent_id, node_id, node.pruned))
        return 1

    # Place les enfants côte à côte, puis centre le parent au-dessus.
    width = 0.0
    child_xs = []
    for child in node.children:
        w = _layout(child, max_depth, x_start + width, depth + 1, positions, edges, node_id)
        child_xs.append(x_start + width + (w - 1) / 2.0)
        width += w
    x = float(np.mean(child_xs))
    positions[node_id] = (x, -depth)
    if parent_id is not None:
        edges.append((parent_id, node_id, False))
    return width


def plot_search_tree(
    game: ConnectFour,
    depth: int = 3,
    max_draw_depth: Optional[int] = None,
    ax: Optional[plt.Axes] = None,
    title: Optional[str] = None,
):
    """Dessine l'arbre αβ d'une position ; branches coupées en rouge pointillé.

    `depth` : profondeur de recherche de l'agent (avec αβ + move ordering, pour
    produire de vrais cutoffs). `max_draw_depth` : profondeur maximale dessinée
    (par défaut = depth). Renvoie (fig, ax) et le nombre de nœuds explorés.
    """
    if max_draw_depth is None:
        max_draw_depth = depth

    agent = AlphaBetaAgent(depth=depth, use_alpha_beta=True, use_move_ordering=True)
    agent.reset()
    agent.search(game, record_tree=True)
    root = agent.last_tree

    positions: Dict[int, Tuple[float, float]] = {}
    edges: List[Tuple[int, int, bool]] = []
    _layout(root, max_draw_depth, 0.0, 0, positions, edges, None)

    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    else:
        fig = ax.figure

    # Arêtes : rouge plein épais si la branche cible est élaguée (bien visible),
    # gris clair fin sinon.
    for parent_id, node_id, pruned in edges:
        x0, y0 = positions[parent_id]
        x1, y1 = positions[node_id]
        if pruned:
            ax.plot([x0, x1], [y0, y1], color=PALETTE["pruned"], lw=2.2, zorder=3)
        else:
            ax.plot([x0, x1], [y0, y1], color="#cdd6df", lw=0.7, zorder=1)

    # Nœuds : petits pour les branches explorées, marqués pour les coupes.
    pruned_ids = {nid for _, nid, p in edges if p}
    ex_x = [xy[0] for nid, xy in positions.items() if nid not in pruned_ids]
    ex_y = [xy[1] for nid, xy in positions.items() if nid not in pruned_ids]
    pr_x = [xy[0] for nid, xy in positions.items() if nid in pruned_ids]
    pr_y = [xy[1] for nid, xy in positions.items() if nid in pruned_ids]
    ax.scatter(ex_x, ex_y, s=22, color=PALETTE["explored"], zorder=2)
    ax.scatter(pr_x, pr_y, s=55, color=PALETTE["pruned"], marker="X", zorder=4,
               edgecolors="white", linewidths=0.6)

    n_pruned = len(pruned_ids)
    n_drawn = len(positions)
    ax.set_title(
        title or f"Arbre de recherche αβ (profondeur {depth})\n"
        f"{n_pruned} branches coupées sur {n_drawn} nœuds dessinés — "
        f"{agent.nodes} nœuds réellement explorés"
    )
    # Légende manuelle.
    ax.scatter([], [], color=PALETTE["explored"], label="branche explorée")
    ax.scatter([], [], color=PALETTE["pruned"], label="branche coupée (αβ)")
    ax.legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.08))
    ax.set_yticks(range(0, -max_draw_depth - 1, -1))
    ax.set_yticklabels([f"niv. {d}" for d in range(max_draw_depth + 1)])
    ax.set_xticks([])
    ax.grid(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    return fig, ax, agent.nodes


# --------------------------------------------------------------------------- #
# B. Nœuds explorés vs profondeur (comparaison des optimisations)
# --------------------------------------------------------------------------- #
def measure_nodes(game: ConnectFour, depths: List[int]) -> Dict[str, List[int]]:
    """Mesure le nombre de nœuds explorés pour chaque ablation et profondeur."""
    results: Dict[str, List[int]] = {label: [] for label, _ in ABLATIONS}
    for label, cfg in ABLATIONS:
        for d in depths:
            agent = AlphaBetaAgent(depth=d, **cfg)
            agent.reset()
            agent.search(game)
            results[label].append(agent.nodes)
    return results


def plot_nodes_vs_depth(
    game: ConnectFour,
    depths: List[int],
    ax: Optional[plt.Axes] = None,
):
    """Courbe log-échelle du nombre de nœuds explorés vs profondeur, par ablation."""
    data = measure_nodes(game, depths)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    for (label, _), color in zip(ABLATIONS, ABLATION_COLORS):
        ax.plot(depths, data[label], marker="o", color=color, label=label, lw=2)

    ax.set_yscale("log")
    ax.set_xlabel("Profondeur de recherche")
    ax.set_ylabel("Nœuds explorés (échelle log)")
    ax.set_title("Coût de la recherche selon les optimisations\n(Knuth & Moore : même résultat, bien moins de nœuds)")
    ax.set_xticks(depths)
    ax.legend(title="Configuration")
    return fig, ax, data


def plot_pruning_comparison(
    game: ConnectFour,
    depth: int = 6,
    ax: Optional[plt.Axes] = None,
):
    """Barres horizontales : nœuds explorés par chaque ablation à profondeur fixe."""
    data = measure_nodes(game, [depth])
    labels = [label for label, _ in ABLATIONS]
    values = [data[label][0] for label in labels]

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    bars = ax.barh(labels, values, color=ABLATION_COLORS)
    ax.set_xscale("log")
    ax.set_xlabel("Nœuds explorés (échelle log)")
    ax.set_title(f"Nœuds explorés à profondeur {depth}")
    # Annoter chaque barre avec sa valeur et le facteur de réduction vs minimax.
    base = values[0]
    for bar, v in zip(bars, values):
        ax.text(
            v * 1.1, bar.get_y() + bar.get_height() / 2,
            f"{v:,}".replace(",", " ") + (f"  (÷{base / v:.0f})" if v < base else ""),
            va="center", fontsize=10,
        )
    ax.set_xlim(right=base * 4)
    ax.invert_yaxis()
    return fig, ax, dict(zip(labels, values))
