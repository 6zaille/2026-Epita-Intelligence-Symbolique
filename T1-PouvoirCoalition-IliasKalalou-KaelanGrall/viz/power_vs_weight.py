from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from core.games import WeightedVotingGame


SEATS_COLOR = "#B8C0D0"
SHAPLEY_COLOR = "#1E2761"
BANZHAF_COLOR = "#F2A900"
DEEGAN_COLOR = "#2C8A4A"


def plot_power_vs_weight(
    game: WeightedVotingGame,
    shapley: dict[int, float],
    banzhaf: dict[int, float],
    deegan: dict[int, float],
    title: str = "Pouvoir de vote contre part de sièges",
    figsize: tuple[float, float] | None = None,
) -> Figure:
    """
    Barres groupees : part de sieges et les trois indices, par joueur. Banzhaf est
    l'indice normalise, seule variante comparable aux deux autres puisqu'elle somme
    a 1 ; le Banzhaf brut ne sommant pas a 1, le superposer induirait en erreur.
    """
    players = list(game.players)
    labels = [game.names[i] for i in players]
    total_weight = game.total_weight

    seat_share = [game.weights[i] / total_weight for i in players]
    ss = [shapley[i] for i in players]
    bz = [banzhaf[i] for i in players]
    dp = [deegan[i] for i in players]

    x = np.arange(len(players))
    width = 0.2

    fig, ax = plt.subplots(figsize=figsize or (max(8, len(players) * 0.9), 5))
    ax.bar(x - 1.5 * width, seat_share, width, label="Part de sièges", color=SEATS_COLOR)
    ax.bar(x - 0.5 * width, ss, width, label="Shapley-Shubik", color=SHAPLEY_COLOR)
    ax.bar(x + 0.5 * width, bz, width, label="Banzhaf (normalisé)", color=BANZHAF_COLOR)
    ax.bar(x + 1.5 * width, dp, width, label="Deegan-Packel", color=DEEGAN_COLOR)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel("Part (fraction du total)")
    ax.set_title(title)
    ax.legend()
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    return fig


def plot_power_gap(
    game: WeightedVotingGame,
    power: dict[int, float],
    index_name: str = "Shapley-Shubik",
) -> Figure:
    """Ecart pouvoir moins part de sieges, trie ; positif = pouvoir superieur au poids."""
    total_weight = game.total_weight
    gaps = {i: power[i] - game.weights[i] / total_weight for i in game.players}
    ordered = sorted(game.players, key=lambda i: gaps[i])
    labels = [game.names[i] for i in ordered]
    values = [gaps[i] * 100 for i in ordered]
    colors = ["#d62728" if v < 0 else "#2ca02c" for v in values]

    fig, ax = plt.subplots(figsize=(max(8, len(ordered) * 0.9), 5))
    ax.bar(labels, values, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Écart pouvoir − sièges (points de %)")
    ax.set_title(f"Écart entre pouvoir {index_name} et part de sièges")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    return fig
