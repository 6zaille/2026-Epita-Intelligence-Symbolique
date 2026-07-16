"""Partage de couts d'infrastructure : le probleme de l'aeroport.

Plusieurs compagnies utilisent une meme piste. Chaque type d'avion ``i`` exige
une longueur de piste dont la construction coute ``c_i``. Une piste de longueur
suffisante pour l'avion le plus exigeant sert aussi tous les autres. Comment
repartir *equitablement* le cout total (= le plus grand ``c_i``) ?

La valeur de Shapley du jeu de couts ``c(S) = max_{i in S} c_i`` fournit la
regle historique de Littlechild & Owen (1973), qui admet une forme close
elegante : on decoupe la piste en *segments* de couts successifs, et le cout
de chaque segment est partage a parts egales entre tous les usagers qui en ont
besoin (ceux dont l'avion requiert ce segment ou au-dela).

Ce module calcule la repartition par les deux voies — formule fermee par
segments et valeur de Shapley generique — et verifie qu'elles coincident.
"""

from __future__ import annotations

from typing import Dict, List, Sequence

import numpy as np

from shapley.exact import shapley_exact
from shapley.games import airport_game


def airport_shapley_closed_form(costs: Sequence[float]) -> np.ndarray:
    """Regle de Littlechild-Owen par decoupage en segments (forme fermee).

    On trie les couts, on considere les increments de cout successifs
    (segments), et chaque segment est finance a parts egales par les usagers
    qui en ont besoin. Complexite ``O(n log n)`` (vs ``O(2^n)`` pour Shapley
    generique) : c'est l'interet d'une regle a forme close.
    """
    n = len(costs)
    order = sorted(range(n), key=lambda i: costs[i])  # usagers du - au + exigeant
    shares = np.zeros(n)
    prev_cost = 0.0
    for rank, i in enumerate(order):
        seg = costs[i] - prev_cost               # cout du segment courant
        n_users = n - rank                       # usagers atteignant ce segment
        if n_users > 0:
            per_user = seg / n_users
            for j in order[rank:]:               # partage entre eux
                shares[j] += per_user
        prev_cost = costs[i]
    return shares


def airport_cost_allocation(costs: Sequence[float]) -> Dict:
    """Repartition complete des couts + verification croisee et de l'efficacite.

    Returns
    -------
    dict avec ``shapley`` (via ``shapley_exact``), ``closed_form`` (segments),
    ``match`` (les deux coincident), ``total`` (cout total finance), et
    ``segments`` (detail pedagogique du decoupage).
    """
    costs = [float(c) for c in costs]
    game = airport_game(costs)
    phi = shapley_exact(game)
    closed = airport_shapley_closed_form(costs)

    # Detail des segments pour l'exposition
    n = len(costs)
    order = sorted(range(n), key=lambda i: costs[i])
    segments: List[dict] = []
    prev = 0.0
    for rank, i in enumerate(order):
        seg = costs[i] - prev
        if seg > 1e-12:
            users = order[rank:]
            segments.append(
                {
                    "de": prev,
                    "a": costs[i],
                    "cout": seg,
                    "nb_usagers": len(users),
                    "part_par_usager": seg / len(users),
                    "usagers": [game.names[j] for j in users],
                }
            )
        prev = costs[i]

    return {
        "noms": game.names,
        "couts": costs,
        "shapley": phi,
        "closed_form": closed,
        "match": bool(np.allclose(phi, closed, atol=1e-9)),
        "total_finance": float(np.sum(phi)),
        "cout_max": max(costs) if costs else 0.0,
        "segments": segments,
    }
