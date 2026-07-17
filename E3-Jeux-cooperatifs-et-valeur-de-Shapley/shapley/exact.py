"""Calcul *exact* de la valeur de Shapley.

Deux formulations equivalentes sont fournies :

1. **Formule par coalitions** (``shapley_exact``), en ``O(2^n)`` evaluations :

   .. math::

       \\varphi_i(v) = \\sum_{S \\subseteq N \\setminus \\{i\\}}
           \\frac{|S|!\\,(n-|S|-1)!}{n!}
           \\bigl(v(S \\cup \\{i\\}) - v(S)\\bigr)

   Chaque terme pondere la *contribution marginale* du joueur ``i`` a la
   coalition ``S`` par la probabilite que ``S`` soit exactement l'ensemble des
   joueurs precedant ``i`` dans une permutation uniforme.

2. **Formule par permutations** (``shapley_by_permutations``), en ``O(n!)`` :

   .. math::

       \\varphi_i(v) = \\frac{1}{n!} \\sum_{\\pi \\in \\Pi(N)}
           \\bigl(v(P_i^\\pi \\cup \\{i\\}) - v(P_i^\\pi)\\bigr)

   ou ``P_i^\\pi`` est l'ensemble des joueurs precedant ``i`` dans l'ordre
   ``\\pi``. C'est la definition « intuitive » (moyenne des contributions
   marginales sur tous les ordres d'arrivee), utile en pedagogie mais limitee
   aux petits ``n``.

La formule par coalitions est l'implementation de reference : elle passe a
l'echelle jusqu'a ``n ~ 20`` la ou ``n!`` explose des ``n = 12``.
"""

from __future__ import annotations

from itertools import permutations
from math import factorial
from typing import List

import numpy as np

from .game import CooperativeGame, mask_size


def _weights(n: int) -> List[float]:
    """Poids de Shapley ``omega(s) = s!(n-s-1)!/n!`` pour ``s = 0..n-1``."""
    nfact = factorial(n)
    return [factorial(s) * factorial(n - s - 1) / nfact for s in range(n)]


def shapley_exact(game: CooperativeGame) -> np.ndarray:
    """Valeur de Shapley exacte par la formule des coalitions (``O(2^n)``).

    Parcourt une seule fois chaque coalition ``S`` et distribue sa
    contribution a tous les joueurs ``i`` en une passe, ce qui evite de
    recalculer ``v(S)`` pour chaque joueur.
    """
    n = game.n
    if n == 0:
        return np.zeros(0)
    weights = _weights(n)
    phi = np.zeros(n)
    full = 1 << n

    for mask in range(full):
        s = mask_size(mask)
        v_s = game.value_mask(mask)
        w_in = weights[s - 1] if s >= 1 else 0.0  # poids quand i vient d'entrer
        w_out = weights[s] if s < n else 0.0       # poids quand i n'est pas la
        for i in range(n):
            bit = 1 << i
            if mask & bit:
                # i est dans S : S le fait "entrer" -> terme +omega(|S|-1) v(S)
                phi[i] += w_in * v_s
            else:
                # i est hors de S : S est un predecesseur -> -omega(|S|) v(S)
                phi[i] -= w_out * v_s
    return phi


def shapley_by_permutations(game: CooperativeGame) -> np.ndarray:
    """Valeur de Shapley exacte par enumeration des ``n!`` permutations.

    Implementation directe de la definition. Reservee aux petits jeux
    (``n <= 10`` en pratique) ; sert de reference pedagogique et de test
    croise avec :func:`shapley_exact`.
    """
    n = game.n
    if n == 0:
        return np.zeros(0)
    if n > 11:
        raise ValueError(
            f"n={n} : {n}! permutations est trop grand ; "
            "utilisez shapley_exact (formule par coalitions)."
        )
    phi = np.zeros(n)
    for order in permutations(range(n)):
        mask = 0
        prev_value = 0.0  # v(emptyset)
        for i in order:
            new_mask = mask | (1 << i)
            new_value = game.value_mask(new_mask)
            phi[i] += new_value - prev_value  # contribution marginale de i
            mask, prev_value = new_mask, new_value
    phi /= factorial(n)
    return phi


def marginal_vector(game: CooperativeGame, order) -> np.ndarray:
    """Vecteur des contributions marginales pour un ordre d'arrivee donne.

    ``m_i = v(P_i \\cup {i}) - v(P_i)`` ou ``P_i`` precede ``i`` dans ``order``.
    Les vecteurs marginaux sont les sommets du coeur pour un jeu convexe, et
    leur moyenne sur toutes les permutations est la valeur de Shapley.
    """
    n = game.n
    m = np.zeros(n)
    mask = 0
    prev = 0.0
    for i in order:
        new_mask = mask | (1 << i)
        val = game.value_mask(new_mask)
        m[i] = val - prev
        mask, prev = new_mask, val
    return m
