"""Style visuel cohérent pour toutes les figures du projet.

Objectif : des figures lisibles en présentation projetée (titres/axes clairs,
palette cohérente, pas le matplotlib par défaut). On centralise ici la palette
et un `apply_style()` à appeler en tête de notebook.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Palette du projet : une couleur par agent + couleurs sémantiques.
PALETTE = {
    "AlphaBeta": "#1b6ca8",   # bleu profond
    "MCTS": "#e07a1f",        # orange
    "DQN": "#3a9b76",         # vert
    "Random": "#9aa0a6",      # gris
    # Couleurs sémantiques pour l'arbre d'élagage.
    "explored": "#1b6ca8",    # branche explorée
    "pruned": "#d1495b",      # branche coupée par alpha-beta
    "leaf": "#6b9bc3",        # feuille / évaluation
    "win": "#3a9b76",
    "loss": "#d1495b",
    "draw": "#9aa0a6",
}

# Colormap continue (bleu -> blanc -> orange) pour les heatmaps de score.
SCORE_CMAP = LinearSegmentedColormap.from_list(
    "score", ["#1b6ca8", "#f5f5f5", "#e07a1f"]
)

# Couleurs des jetons sur le plateau.
DISC_COLORS = {0: "#22303c", 1: "#e8c547", 2: "#d1495b"}  # vide, J1 (jaune), J2 (rouge)
BOARD_COLOR = "#1b3a5c"


def agent_color(name: str) -> str:
    """Couleur associée à un agent d'après son nom (préfixe), gris par défaut."""
    for key, color in PALETTE.items():
        if name.startswith(key):
            return color
    return PALETTE["Random"]


def apply_style() -> None:
    """Applique les réglages matplotlib globaux (à appeler une fois)."""
    mpl.rcParams.update(
        {
            "figure.figsize": (9, 5.5),
            "figure.dpi": 110,
            "savefig.dpi": 120,
            "font.size": 12,
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
            "axes.labelsize": 12,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "grid.linestyle": "--",
            "legend.frameon": False,
            "axes.prop_cycle": plt.cycler(
                color=["#1b6ca8", "#e07a1f", "#3a9b76", "#d1495b", "#9b59b6", "#9aa0a6"]
            ),
        }
    )
