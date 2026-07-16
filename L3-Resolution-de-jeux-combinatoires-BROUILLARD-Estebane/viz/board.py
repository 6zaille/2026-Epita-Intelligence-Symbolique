"""Visualisation 3 : plateau de jeu + « ce que pense l'agent ».

- `draw_board` : rend joliment un plateau de Puissance 4 (jetons colorés).
- `agent_thoughts` : extrait, pour un agent donné, son évaluation par colonne
  (scores αβ, visites MCTS, ou Q-valeurs DQN) de façon uniforme.
- `draw_thoughts` : barres de l'évaluation par colonne, alignées sous le plateau.

Le widget interactif (ipywidgets) qui assemble tout cela est dans `viz.interactive`
pour garder ce module sans dépendance à ipywidgets (donc testable hors notebook).
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch

from agents.base import Agent
from game.connect_four import COLS, ROWS, ConnectFour
from viz.style import BOARD_COLOR, DISC_COLORS


def draw_board(
    game: ConnectFour,
    ax: Optional[plt.Axes] = None,
    highlight_col: Optional[int] = None,
):
    """Dessine le plateau : fond bleu, jetons jaunes (J1) et rouges (J2)."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 5.3))
    else:
        fig = ax.figure

    # Fond du plateau.
    ax.add_patch(
        FancyBboxPatch(
            (-0.5, -0.5), COLS, ROWS,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            facecolor=BOARD_COLOR, edgecolor="none", zorder=0,
        )
    )

    # Jetons (ligne 0 = bas).
    for r in range(ROWS):
        for c in range(COLS):
            ax.add_patch(
                Circle((c, r), 0.42, facecolor=DISC_COLORS[game.board[r][c]],
                       edgecolor="#13283f", lw=1.2, zorder=2)
            )

    if highlight_col is not None:
        ax.add_patch(
            plt.Rectangle((highlight_col - 0.48, -0.5), 0.96, ROWS,
                          facecolor="white", alpha=0.12, zorder=1)
        )

    ax.set_xlim(-0.6, COLS - 0.4)
    ax.set_ylim(-0.6, ROWS - 0.4)
    ax.set_aspect("equal")
    ax.set_xticks(range(COLS))
    ax.set_xticklabels(range(COLS))
    ax.set_yticks([])
    ax.xaxis.set_ticks_position("top")
    ax.set_title("Plateau")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
    return fig, ax


def agent_thoughts(agent: Agent, game: ConnectFour) -> Tuple[Dict[int, float], str]:
    """Renvoie (scores_par_colonne, libellé) reflétant la « pensée » de l'agent.

    Uniformise les trois types d'agents :
    - AlphaBeta : valeur minimax par colonne (last_move_scores).
    - MCTS      : nombre de visites par colonne (last_visit_counts).
    - DQN       : Q-valeur par colonne (last_q_values).

    L'agent doit avoir « réfléchi » : on appelle `move` pour peupler ses caches.
    """
    # On déclenche une réflexion sur une copie pour ne pas modifier le jeu.
    agent.move(game.copy())

    if hasattr(agent, "last_visit_counts") and getattr(agent, "last_visit_counts"):
        return dict(agent.last_visit_counts), "Visites MCTS par colonne"
    if hasattr(agent, "last_move_scores") and getattr(agent, "last_move_scores"):
        return dict(agent.last_move_scores), "Évaluation αβ par colonne"
    if hasattr(agent, "last_q_values") and getattr(agent, "last_q_values"):
        return dict(agent.last_q_values), "Q-valeurs DQN par colonne"
    return {}, "Pensée indisponible"


# Au-delà de ce seuil, une évaluation αβ correspond à un mat forcé (gain/perte).
_MATE_THRESHOLD = 9000


def draw_thoughts(
    scores: Dict[int, float],
    label: str,
    ax: Optional[plt.Axes] = None,
    best_col: Optional[int] = None,
):
    """Barres de l'évaluation par colonne ; la meilleure colonne est mise en avant.

    Les valeurs de mat forcé (|v| très grand côté αβ) sont écrêtées à l'échelle
    des autres colonnes et annotées « ✓ mat » / « ✗ perd », sinon elles écrasent
    visuellement toutes les autres barres.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 2.4))
    else:
        fig = ax.figure

    cols = list(range(COLS))
    values = [scores.get(c, None) for c in cols]
    if best_col is None and scores:
        best_col = max(scores, key=scores.get)

    # Échelle d'affichage basée sur les valeurs « normales » (hors mats).
    normal = [abs(v) for v in values if v is not None and abs(v) < _MATE_THRESHOLD]
    cap = max(normal) if normal else 1.0
    cap = max(cap, 1.0)

    heights, colors, annotations = [], [], []
    for c, v in zip(cols, values):
        if v is None:
            heights.append(0.0)
            colors.append("#e9ecef")  # colonne pleine / non jouable
            annotations.append(None)
        elif abs(v) >= _MATE_THRESHOLD:
            # Mat forcé : écrête à l'échelle, garde le signe, annote.
            heights.append(cap * 1.15 * (1 if v > 0 else -1))
            colors.append("#3a9b76" if v > 0 else "#d1495b")
            annotations.append("✓ mat" if v > 0 else "✗ perd")
        else:
            heights.append(v)
            colors.append("#e07a1f" if c == best_col else "#1b6ca8")
            annotations.append(None)

    bars = ax.bar(cols, heights, color=colors)
    for bar, ann in zip(bars, annotations):
        if ann:
            y = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, y,
                    ann, ha="center", va="bottom" if y >= 0 else "top",
                    fontsize=9, fontweight="bold")
    ax.set_xticks(cols)
    ax.set_xlabel("Colonne")
    ax.set_title(label)
    ax.axhline(0, color="#444", lw=0.8)
    ax.margins(y=0.2)
    return fig, ax
