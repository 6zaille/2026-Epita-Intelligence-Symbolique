"""Convergence de l'estimateur Monte Carlo vers la valeur de Shapley exacte.

Illustre le compromis cout/precision : la formule exacte coute ``O(2^n)`` (voire
``O(n!)`` par permutations) la ou l'estimateur Monte Carlo converge en
``O(1/sqrt(m))`` independamment de ``2^n``. On trace l'erreur maximale en
fonction du nombre de permutations echantillonnees, en echelle log-log, avec la
pente de reference ``-1/2``.
"""

import os

import _bootstrap
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from shapley.exact import shapley_exact
from shapley.games import airport_game, gloves_game
from shapley.monte_carlo import convergence_curve


def main():
    games = {
        "Gloves (3G, 4D)": gloves_game(3, 4),
        "Airport [1,2,3,5,8]": airport_game([1, 2, 3, 5, 8]),
    }
    sizes = np.unique(np.round(np.logspace(1, 4.3, 25)).astype(int))

    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    for name, game in games.items():
        exact = shapley_exact(game)
        curve = convergence_curve(game, exact, sizes, seed=42)
        ax.loglog(curve["sizes"], curve["errors"], marker="o", ms=4, label=name)
        print(f"{name}: erreur finale (m={curve['sizes'][-1]}) = "
              f"{curve['errors'][-1]:.4f}")

    # pente de reference O(1/sqrt(m))
    ref_x = np.array([sizes[0], sizes[-1]], dtype=float)
    ref_y = 0.6 * ref_x ** -0.5
    ax.loglog(ref_x, ref_y, "k--", lw=1, label=r"pente $O(1/\sqrt{m})$")

    ax.set_xlabel("nombre de permutations echantillonnees $m$")
    ax.set_ylabel(r"erreur max $\max_i |\hat\varphi_i - \varphi_i|$")
    ax.set_title("Convergence Monte Carlo de la valeur de Shapley")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(_bootstrap.FIGDIR, "convergence_mc.png")
    fig.savefig(out, dpi=130)
    print(f"figure -> {out}")


if __name__ == "__main__":
    main()
