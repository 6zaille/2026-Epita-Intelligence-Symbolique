"""Coeur d'un jeu cooperatif, convexite, et lien avec la valeur de Shapley.

Le **coeur** d'un jeu ``(N, v)`` est l'ensemble des allocations ``x`` a la fois
*efficaces* et *stables* (aucune coalition n'a interet a faire secession) :

.. math::

    \\mathrm{Core}(v) = \\Bigl\\{ x \\in \\mathbb{R}^n :
        \\textstyle\\sum_{i} x_i = v(N),\\;
        \\sum_{i \\in S} x_i \\ge v(S)\\ \\forall S \\subseteq N \\Bigr\\}.

C'est un polytope, possiblement vide.

Un jeu est **convexe** (supermodulaire) si
``v(S) + v(T) <= v(S u T) + v(S n T)`` pour toutes coalitions, ce qui equivaut
a des contributions marginales croissantes. Theoreme de Shapley (1971) : pour
un jeu convexe, le coeur est non vide, ses sommets sont exactement les
``n!`` vecteurs marginaux, et **la valeur de Shapley en est le barycentre** —
donc appartient au coeur.
"""

from __future__ import annotations

from itertools import combinations
from typing import List

import numpy as np

from .game import CooperativeGame, mask_size

TOL = 1e-9


# ----------------------------------------------------------------------
# Convexite / supermodularite
# ----------------------------------------------------------------------
def is_convex(game: CooperativeGame, tol: float = TOL) -> bool:
    """Teste la supermodularite via les contributions marginales croissantes.

    Il suffit de verifier que pour tout joueur ``i`` et toutes coalitions
    ``S subset T`` avec ``i`` hors de ``T`` :
    ``v(S u {i}) - v(S) <= v(T u {i}) - v(T)``. On teste la condition sur les
    paires ``(S, T = S u {j})`` (aretes du treillis), ce qui est equivalent.
    """
    n = game.n
    full = 1 << n
    for i in range(n):
        bi = 1 << i
        for S in range(full):
            if S & bi:
                continue
            marg_S = game.value_mask(S | bi) - game.value_mask(S)
            rest = (full - 1) ^ S ^ bi
            bit = rest
            while bit:
                j = bit & (-bit)
                T = S | j
                marg_T = game.value_mask(T | bi) - game.value_mask(T)
                if marg_S > marg_T + tol:
                    return False
                bit ^= j
    return True


def is_superadditive(game: CooperativeGame, tol: float = TOL) -> bool:
    """``v(S u T) >= v(S) + v(T)`` pour toutes coalitions disjointes."""
    n = game.n
    full = 1 << n
    for S in range(full):
        # sous-ensembles disjoints de S
        comp = (full - 1) ^ S
        T = comp
        while True:
            if T != 0 and (S & T) == 0:
                if game.value_mask(S | T) + tol < game.value_mask(S) + game.value_mask(T):
                    return False
            if T == 0:
                break
            T = (T - 1) & comp
    return True


# ----------------------------------------------------------------------
# Appartenance au coeur
# ----------------------------------------------------------------------
def core_constraints_violation(game: CooperativeGame, x: np.ndarray) -> float:
    """Deficit maximal de stabilite : ``max_S (v(S) - sum_{i in S} x_i)``.

    Vaut ``<= 0`` (a la tolerance pres) ssi ``x`` respecte toutes les
    contraintes de coalition. On ignore l'efficacite ici (testee a part).
    """
    n = game.n
    worst = -np.inf
    for mask in range(1, 1 << n):
        coalition_sum = sum(x[i] for i in range(n) if mask & (1 << i))
        worst = max(worst, game.value_mask(mask) - coalition_sum)
    return float(worst)


def in_core(game: CooperativeGame, x: np.ndarray, tol: float = 1e-6) -> bool:
    """``x`` est-il dans le coeur (efficace ET stable) ?"""
    if abs(float(np.sum(x)) - game.grand_coalition_value()) > tol:
        return False
    return core_constraints_violation(game, x) <= tol


# ----------------------------------------------------------------------
# Sommets du coeur pour un jeu convexe
# ----------------------------------------------------------------------
def core_vertices_convex(game: CooperativeGame) -> np.ndarray:
    """Sommets du coeur d'un jeu convexe = vecteurs marginaux des permutations.

    Renvoie un tableau ``(k, n)`` des vecteurs marginaux distincts. Valide
    uniquement pour un jeu convexe (sinon ces vecteurs ne bornent pas le coeur).
    """
    from itertools import permutations

    from .exact import marginal_vector

    n = game.n
    seen = set()
    verts: List[np.ndarray] = []
    for order in permutations(range(n)):
        m = marginal_vector(game, order)
        key = tuple(np.round(m, 9))
        if key not in seen:
            seen.add(key)
            verts.append(m)
    return np.array(verts)


def core_check_report(game: CooperativeGame) -> dict:
    """Rapport synthetique : convexite, superadditivite, Shapley dans le coeur."""
    from .exact import shapley_exact

    phi = shapley_exact(game)
    convex = is_convex(game)
    return {
        "convexe": convex,
        "superadditif": is_superadditive(game),
        "shapley": phi,
        "shapley_efficace": abs(float(np.sum(phi)) - game.grand_coalition_value()) <= 1e-9,
        "shapley_dans_coeur": in_core(game, phi),
        "deficit_max": core_constraints_violation(game, phi),
    }
