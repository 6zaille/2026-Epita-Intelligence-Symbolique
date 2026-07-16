"""Valeur de Shapley et axiomes sur les jeux classiques.

Affiche, pour chaque jeu de reference, la valeur de Shapley exacte, la somme
(efficacite = v(N)) et le statut des axiomes verifies numeriquement.
"""

import _bootstrap  # noqa: F401
import numpy as np

from shapley.axioms import verify_all_axioms, null_players, symmetric_pairs
from shapley.exact import shapley_by_permutations, shapley_exact
from shapley.games import all_classic_games


def main():
    print("=" * 70)
    print("VALEUR DE SHAPLEY SUR LES JEUX CLASSIQUES")
    print("=" * 70)
    for name, game in all_classic_games().items():
        phi = shapley_exact(game)
        vN = game.grand_coalition_value()
        kind = "couts" if game.is_cost else "gains"
        print(f"\n### {name}  (n={game.n}, {kind})")
        for nm, val in zip(game.names, phi):
            print(f"    {nm:22s} : {val:+.4f}")
        print(f"    {'somme (= v(N))':22s} : {phi.sum():+.4f}   [v(N) = {vN:+.4f}]")

        ax = verify_all_axioms(game, phi)
        print(f"    axiomes  -> efficacite={ax['efficacite']}  "
              f"symetrie={ax['symetrie']}  joueur_nul={ax['joueur_nul']}")
        nulls = null_players(game)
        pairs = symmetric_pairs(game)
        if nulls:
            print(f"    joueurs nuls : {[game.names[i] for i in nulls]}")
        if pairs and game.n <= 6:
            print(f"    paires symetriques : "
                  f"{[(game.names[i], game.names[j]) for i, j in pairs]}")

        # verification croisee coalition vs permutation (petits jeux)
        if game.n <= 8:
            phi_perm = shapley_by_permutations(game)
            ok = np.allclose(phi, phi_perm)
            print(f"    coalitions O(2^n) == permutations O(n!) : {ok}")

    print("\n" + "=" * 70)
    print("Les 4 axiomes caracterisent de maniere UNIQUE la valeur de Shapley.")
    print("=" * 70)


if __name__ == "__main__":
    main()
