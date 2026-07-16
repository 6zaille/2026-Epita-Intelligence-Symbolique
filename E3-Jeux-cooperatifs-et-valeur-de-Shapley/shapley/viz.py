"""Visualisations pour les jeux cooperatifs a 3 joueurs.

Pour ``n = 3`` et un jeu efficace, toute allocation ``x`` verifie
``x_0 + x_1 + x_2 = v(N)`` : elle vit donc sur un plan que l'on represente
comme un **simplexe (triangle barycentrique)**. On y trace le coeur, la valeur
de Shapley, et les vecteurs marginaux (sommets du coeur si le jeu est convexe).
"""

from __future__ import annotations

import numpy as np

from .core import core_vertices_convex, in_core, is_convex
from .exact import shapley_exact


# Sommets du triangle de reference (coordonnees cartesiennes)
_TRI = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, np.sqrt(3) / 2]])


def barycentric_to_cartesian(x: np.ndarray, total: float) -> np.ndarray:
    """Projette une allocation 3D (somme = total) dans le triangle 2D."""
    w = np.asarray(x, dtype=float) / total
    return w @ _TRI


def plot_core_simplex(game, ax, title: str = None, grid: int = 220):
    """Trace le coeur d'un jeu a 3 joueurs sur le simplexe barycentrique.

    Le coeur est materialise en balayant le simplexe (allocations efficaces) et
    en gardant les points stables. La valeur de Shapley et les vecteurs
    marginaux sont superposes.
    """
    if game.n != 3:
        raise ValueError("la visualisation simplexe ne gere que n = 3")
    total = game.grand_coalition_value()

    # Contour du triangle
    tri = np.vstack([_TRI, _TRI[0]])
    ax.plot(tri[:, 0], tri[:, 1], color="0.4", lw=1.2, zorder=1)

    # Balayage du simplexe : allocations efficaces (a, b, c>=0, a+b+c=total)
    core_pts = []
    for ia in range(grid + 1):
        a = ia / grid
        for ib in range(grid + 1 - ia):
            b = ib / grid
            c = 1.0 - a - b
            if c < -1e-9:
                continue
            x = np.array([a, b, c]) * total
            if in_core(game, x, tol=1e-9):
                core_pts.append([a, b, c])
    if core_pts:
        pts = barycentric_to_cartesian(np.array(core_pts), 1.0)
        ax.scatter(pts[:, 0], pts[:, 1], s=6, color="#7fb2f0", alpha=0.5,
                   edgecolors="none", zorder=2, label="Coeur")

    # Vecteurs marginaux (sommets du coeur pour un jeu convexe)
    if is_convex(game):
        verts = core_vertices_convex(game)
        vc = barycentric_to_cartesian(verts, total)
        ax.scatter(vc[:, 0], vc[:, 1], s=45, facecolors="none",
                   edgecolors="#d1495b", lw=1.6, zorder=4,
                   label="Vecteurs marginaux")

    # Valeur de Shapley
    phi = shapley_exact(game)
    pc = barycentric_to_cartesian(phi, total)
    ax.scatter([pc[0]], [pc[1]], s=140, marker="*", color="#e8a13a",
               edgecolors="k", lw=0.6, zorder=5, label="Valeur de Shapley")

    # Etiquettes des sommets (joueurs), placees a l'exterieur du triangle
    offsets = [(-0.06, -0.06), (0.06, -0.06), (0.0, 0.06)]
    valigns = ["top", "top", "bottom"]
    for k, (px, py) in enumerate(_TRI):
        dx, dy = offsets[k]
        ax.annotate(game.names[k], (px + dx, py + dy), ha="center",
                    va=valigns[k], fontsize=12, fontweight="bold",
                    color="#333333")

    ax.set_aspect("equal")
    ax.axis("off")
    ax.margins(0.14)
    if title:
        # titre place SOUS le triangle pour ne pas heurter l'apex C
        ax.text(0.5, -0.16, title, transform=ax.transAxes, ha="center",
                va="top", fontsize=12, fontweight="bold")
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 1.0),
              fontsize=8, framealpha=0.9)
