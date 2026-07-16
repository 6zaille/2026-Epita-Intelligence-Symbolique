"""Partage de couts d'infrastructure : le probleme de l'aeroport.

Repartit le cout d'une piste entre des avions aux exigences differentes, via la
valeur de Shapley = regle de Littlechild-Owen (partage des segments). Verifie
que la forme close ``O(n log n)`` coincide avec le calcul generique ``O(2^n)``,
et visualise la repartition.
"""

import os

import _bootstrap
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from applications.airport_cost import airport_cost_allocation


def main():
    costs = [1, 2, 4, 6, 10]  # couts de piste croissants (petits -> gros avions)
    rep = airport_cost_allocation(costs)

    print("=" * 64)
    print("PARTAGE DES COUTS DE L'AEROPORT (valeur de Shapley)")
    print("=" * 64)
    print(f"couts requis        : {rep['couts']}")
    print(f"cout total (= max)  : {rep['cout_max']}")
    print(f"total finance       : {rep['total_finance']:.4f}  "
          f"(efficacite OK: {abs(rep['total_finance']-rep['cout_max'])<1e-9})")
    print(f"forme close == Shapley exact : {rep['match']}")
    print("\nRepartition par joueur :")
    for nm, part in zip(rep["noms"], rep["shapley"]):
        print(f"    {nm:16s} paie {part:7.4f}")
    print("\nDecoupage en segments (partage egal entre usagers concernes) :")
    for s in rep["segments"]:
        print(f"    [{s['de']:.0f} -> {s['a']:.0f}] cout {s['cout']:.0f} "
              f"/ {s['nb_usagers']} usagers = {s['part_par_usager']:.4f} chacun")

    # Figure : parts empilees par segment
    fig, ax = plt.subplots(figsize=(8, 5))
    n = len(costs)
    names = [nm.split("(")[0] for nm in rep["noms"]]
    bottoms = np.zeros(n)
    order = sorted(range(n), key=lambda i: costs[i])
    cmap = plt.get_cmap("viridis")
    for k, s in enumerate(rep["segments"]):
        heights = np.zeros(n)
        users_idx = [names.index(u.split("(")[0]) for u in s["usagers"]]
        for j in users_idx:
            heights[j] = s["part_par_usager"]
        ax.bar(range(n), heights, bottom=bottoms,
               color=cmap(k / max(len(rep["segments"]) - 1, 1)),
               edgecolor="white",
               label=f"segment [{s['de']:.0f}-{s['a']:.0f}]")
        bottoms += heights

    ax.set_xticks(range(n))
    ax.set_xticklabels(names)
    ax.set_ylabel("cout paye")
    ax.set_title("Partage des couts de l'aeroport par la valeur de Shapley")
    ax.legend(title="contribution par segment", fontsize=8)
    for i in range(n):
        ax.text(i, bottoms[i] + 0.1, f"{rep['shapley'][i]:.2f}",
                ha="center", fontsize=9, fontweight="bold")
    fig.tight_layout()
    out = os.path.join(_bootstrap.FIGDIR, "airport_cost.png")
    fig.savefig(out, dpi=130)
    print(f"\nfigure -> {out}")


if __name__ == "__main__":
    main()
