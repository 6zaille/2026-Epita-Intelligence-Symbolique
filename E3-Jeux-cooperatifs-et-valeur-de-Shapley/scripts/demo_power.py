"""Indices de pouvoir : le Conseil de securite de l'ONU.

Le pouvoir reel d'un votant ne se lit pas dans son "poids" apparent. Au Conseil
de securite (5 membres permanents avec veto, 10 non-permanents), on compare
l'indice de Shapley-Shubik (= valeur de Shapley du jeu de vote) et l'indice de
Banzhaf. Resultat classique : chaque permanent detient ~19,6 % du pouvoir, un
non-permanent ~0,19 % ; les 5 permanents cumulent ~98 %.
"""

import os

import _bootstrap
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from shapley.games import un_security_council_game
from shapley.power_index import banzhaf_index, shapley_shubik_index


def main():
    game = un_security_council_game()
    ss = shapley_shubik_index(game)
    bz = banzhaf_index(game, normalized=True)

    print("=" * 64)
    print("CONSEIL DE SECURITE DE L'ONU — INDICES DE POUVOIR")
    print("=" * 64)
    print(f"{'membre':12s} {'Shapley-Shubik':>16s} {'Banzhaf':>12s}")
    print(f"{'permanent':12s} {ss[0]:>16.5f} {bz[0]:>12.5f}")
    print(f"{'non-perm.':12s} {ss[5]:>16.5f} {bz[5]:>12.5f}")
    print(f"\n5 permanents cumulent : Shapley-Shubik={ss[:5].sum():.4f}  "
          f"Banzhaf={bz[:5].sum():.4f}")
    print(f"10 non-permanents     : Shapley-Shubik={ss[5:].sum():.4f}  "
          f"Banzhaf={bz[5:].sum():.4f}")
    print(f"ratio pouvoir permanent / non-permanent : {ss[0]/ss[5]:.1f}x")

    # Figure : pouvoir vs "poids" naif (part des sieges)
    fig, ax = plt.subplots(figsize=(8, 5))
    cats = ["Membre\npermanent", "Membre\nnon-permanent"]
    naive = [1 / 15, 1 / 15]  # part naive (1 siege / 15)
    shubik = [ss[0], ss[5]]
    x = np.arange(len(cats))
    w = 0.35
    ax.bar(x - w / 2, naive, w, label="poids naif (1/15 siege)", color="#adb5bd")
    ax.bar(x + w / 2, shubik, w, label="pouvoir de Shapley-Shubik",
           color="#4361ee")
    for xi, val in zip(x + w / 2, shubik):
        ax.text(xi, val + 0.005, f"{val:.3f}", ha="center", fontsize=9,
                fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(cats)
    ax.set_ylabel("part du pouvoir")
    ax.set_title("ONU : pouvoir reel (Shapley-Shubik) vs poids apparent")
    ax.legend()
    fig.tight_layout()
    out = os.path.join(_bootstrap.FIGDIR, "unsc_power.png")
    fig.savefig(out, dpi=130)
    print(f"\nfigure -> {out}")


if __name__ == "__main__":
    main()
