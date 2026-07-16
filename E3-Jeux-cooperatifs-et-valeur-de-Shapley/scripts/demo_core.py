"""Coeur et convexite : la valeur de Shapley est-elle stable ?

Compare deux jeux a 3 joueurs sur le simplexe barycentrique :

* un jeu **convexe** : le coeur est non vide, ses sommets sont les vecteurs
  marginaux, et la valeur de Shapley (leur barycentre) tombe DANS le coeur ;
* un jeu de majorite au **coeur vide** : la valeur de Shapley existe toujours
  (1/3, 1/3, 1/3) mais n'est stabilisee par aucune allocation.
"""

import os

import _bootstrap
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from shapley.core import core_check_report
from shapley.games import convex_example, empty_core_example
from shapley.viz import plot_core_simplex


def main():
    games = [
        (convex_example(), "Jeu convexe : Shapley dans le coeur"),
        (empty_core_example(), "Jeu de majorite : coeur vide"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    for ax, (game, title) in zip(axes, games):
        rep = core_check_report(game)
        print(f"\n### {title}")
        print(f"    convexe        : {rep['convexe']}")
        print(f"    superadditif   : {rep['superadditif']}")
        print(f"    Shapley        : {np.round(rep['shapley'], 4)}")
        print(f"    dans le coeur  : {rep['shapley_dans_coeur']} "
              f"(deficit max = {rep['deficit_max']:.4f})")
        plot_core_simplex(game, ax, title=title)

    fig.suptitle("Coeur, convexite et valeur de Shapley (jeux a 3 joueurs)",
                 fontsize=13, y=0.98)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    out = os.path.join(_bootstrap.FIGDIR, "core_simplex.png")
    fig.savefig(out, dpi=130)
    print(f"\nfigure -> {out}")


if __name__ == "__main__":
    main()
