"""Visualisation 2 : heatmap du tournoi + courbe « force vs budget ».

A. `plot_winrate_heatmap` : matrice agent×agent du score (victoire=1, nul=0.5),
   pour lire d'un coup d'œil qui domine qui.

B. `plot_ranking` : classement des agents par score total + temps de réflexion
   moyen (le compromis force/vitesse).

C. `plot_strength_vs_budget` : taux de victoire en fonction du budget de temps/
   profondeur alloué — illustre que αβ domine à temps long tandis que MCTS reste
   compétitif à budget serré.
"""

from __future__ import annotations

from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

from tournament.runner import TournamentResult
from viz.style import SCORE_CMAP, agent_color


def plot_winrate_heatmap(result: TournamentResult, ax: Optional[plt.Axes] = None):
    """Heatmap du score de la ligne i contre la colonne j (dans [0, 1])."""
    names = result.names
    n = len(names)
    mat = result.score_matrix

    if ax is None:
        fig, ax = plt.subplots(figsize=(1.6 * n + 2, 1.4 * n + 1))
    else:
        fig = ax.figure

    im = ax.imshow(mat, cmap=SCORE_CMAP, vmin=0.0, vmax=1.0)

    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(names, rotation=30, ha="right")
    ax.set_yticklabels(names)
    ax.set_xlabel("Adversaire (colonne)")
    ax.set_ylabel("Agent (ligne)")
    ax.set_title("Taux de victoire du tournoi\n(ligne contre colonne ; 1 = gagne toujours)")

    # Annoter chaque case avec le score (diagonale grisée).
    for i in range(n):
        for j in range(n):
            if i == j:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, color="#e9ecef"))
                ax.text(j, i, "—", ha="center", va="center", color="#9aa0a6")
            else:
                v = mat[i, j]
                ax.text(
                    j, i, f"{v:.0%}", ha="center", va="center",
                    color="white" if (v < 0.25 or v > 0.75) else "#222",
                    fontweight="bold",
                )
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="score (0–1)")
    return fig, ax


def plot_ranking(result: TournamentResult, ax: Optional[plt.Axes] = None):
    """Classement par score total, barres colorées par agent."""
    items = sorted(result.total_score.items(), key=lambda kv: kv[1], reverse=True)
    names = [k for k, _ in items]
    scores = [v for _, v in items]
    colors = [agent_color(n) for n in names]

    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    bars = ax.bar(names, scores, color=colors)
    ax.set_ylabel("Score total (points marqués)")
    ax.set_title("Classement du tournoi round-robin")
    for bar, name in zip(bars, names):
        t = result.avg_move_time.get(name, 0.0)
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height(),
            f"{bar.get_height():.0f}\n({t*1000:.0f} ms/coup)",
            ha="center", va="bottom", fontsize=10,
        )
    ax.margins(y=0.18)
    return fig, ax


def plot_speed_vs_strength(result: TournamentResult, ax: Optional[plt.Axes] = None):
    """Nuage temps de réflexion (x) vs score total (y) : le compromis force/vitesse."""
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    for name in result.names:
        x = result.avg_move_time[name] * 1000  # ms
        y = result.total_score[name]
        ax.scatter(x, y, s=160, color=agent_color(name), zorder=3)
        ax.annotate(name, (x, y), xytext=(6, 6), textcoords="offset points", fontsize=11)

    ax.set_xscale("log")
    ax.set_xlabel("Temps de réflexion moyen par coup (ms, échelle log)")
    ax.set_ylabel("Score total au tournoi")
    ax.set_title("Compromis force / vitesse")
    return fig, ax


def plot_strength_vs_budget(
    budgets: List[float],
    curves: Dict[str, List[float]],
    xlabel: str = "Budget de temps par coup (s)",
    logx: bool = True,
    ax: Optional[plt.Axes] = None,
):
    """Courbes taux de victoire vs budget, une par agent/configuration.

    `curves[name]` est la liste des taux de victoire alignée sur `budgets`.
    """
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.figure

    for name, ys in curves.items():
        ax.plot(budgets, ys, marker="o", lw=2, color=agent_color(name), label=name)

    if logx:
        ax.set_xscale("log")
    ax.axhline(0.5, color="#9aa0a6", ls="--", lw=1, alpha=0.7)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Taux de victoire")
    ax.set_title("Force en fonction du budget alloué")
    ax.legend(title="Agent")
    return fig, ax
