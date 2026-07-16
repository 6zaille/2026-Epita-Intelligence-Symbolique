"""Indices de pouvoir pour les jeux de vote (jeux simples).

Un *jeu simple* est un jeu cooperatif ``v : 2^N -> {0, 1}`` monotone : une
coalition est *gagnante* (``v = 1``) ou *perdante* (``v = 0``). Deux mesures
classiques du pouvoir d'un joueur y sont definies a partir des situations ou
il est *pivot* (son depart fait basculer une coalition gagnante en perdante) :

* **Indice de Shapley-Shubik** : c'est exactement la valeur de Shapley d'un
  jeu simple. Il compte la fraction des ``n!`` ordres d'arrivee ou le joueur
  est pivot (celui qui fait franchir le quota).
* **Indice de Banzhaf** : compte les *coalitions* ou le joueur est decisif
  (« swing »), rapporte au nombre total de swings. Contrairement a
  Shapley-Shubik il ne respecte pas l'efficacite (sa somme n'est pas 1) mais
  se prete a une belle interpretation probabiliste (votes independants).
"""

from __future__ import annotations

import numpy as np

from .exact import shapley_exact
from .game import CooperativeGame, mask_size


def shapley_shubik_index(game: CooperativeGame) -> np.ndarray:
    """Indice de Shapley-Shubik = valeur de Shapley du jeu simple (somme = 1)."""
    return shapley_exact(game)


def banzhaf_index(game: CooperativeGame, normalized: bool = True) -> np.ndarray:
    """Indice de Banzhaf.

    Un joueur ``i`` est *decisif* pour la coalition ``S`` (avec ``i in S``) si
    ``v(S) = 1`` et ``v(S \\ {i}) = 0``. Le nombre de swings de ``i`` est le
    Banzhaf brut. Si ``normalized=True``, on divise par la somme des swings de
    tous les joueurs (les indices somment alors a 1) ; sinon on renvoie le
    Banzhaf « absolu » ``swings_i / 2^{n-1}``.
    """
    n = game.n
    swings = np.zeros(n)
    for i in range(n):
        bit = 1 << i
        for mask in range(1 << n):
            if not (mask & bit):
                continue
            if game.value_mask(mask) - game.value_mask(mask ^ bit) > 0.5:
                swings[i] += 1
    if normalized:
        total = swings.sum()
        return swings / total if total > 0 else swings
    return swings / (1 << (n - 1))


def pivot_analysis(game: CooperativeGame) -> dict:
    """Rapport comparatif Shapley-Shubik vs Banzhaf pour un jeu de vote."""
    ss = shapley_shubik_index(game)
    bz = banzhaf_index(game, normalized=True)
    return {
        "noms": game.names,
        "shapley_shubik": ss,
        "banzhaf": bz,
    }
