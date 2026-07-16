"""Verification numerique des quatre axiomes de Shapley.

Shapley (1953) montre que sa valeur est l'**unique** application ``phi`` qui,
pour tout jeu, satisfait simultanement :

* **Efficacite** : ``sum_i phi_i(v) = v(N)`` (tout le gain est reparti).
* **Symetrie** : si ``i`` et ``j`` sont interchangeables
  (``v(S u {i}) = v(S u {j})`` pour toute coalition ``S`` ne contenant ni
  ``i`` ni ``j``), alors ``phi_i(v) = phi_j(v)``.
* **Joueur nul** : si ``i`` ne contribue jamais
  (``v(S u {i}) = v(S)`` pour tout ``S``), alors ``phi_i(v) = 0``.
* **Additivite** : ``phi(v + w) = phi(v) + phi(w)`` pour tous jeux ``v, w``.

Ce module fournit des predicats testables sur des instances concretes ; il
*illustre* les axiomes (il ne remplace pas une preuve formelle), et sert de
garde-fou de correction pour l'implementation.
"""

from __future__ import annotations

from itertools import combinations
from typing import Callable, List, Tuple

import numpy as np

from .exact import shapley_exact
from .game import CooperativeGame

TOL = 1e-9


# ----------------------------------------------------------------------
# Detection des relations structurelles entre joueurs
# ----------------------------------------------------------------------
def null_players(game: CooperativeGame) -> List[int]:
    """Liste des joueurs nuls : ``v(S u {i}) = v(S)`` pour toute coalition."""
    n = game.n
    nulls = []
    for i in range(n):
        bit = 1 << i
        is_null = True
        for mask in range(1 << n):
            if mask & bit:
                continue
            if abs(game.value_mask(mask | bit) - game.value_mask(mask)) > TOL:
                is_null = False
                break
        if is_null:
            nulls.append(i)
    return nulls


def symmetric_pairs(game: CooperativeGame) -> List[Tuple[int, int]]:
    """Paires de joueurs interchangeables (symetriques)."""
    n = game.n
    pairs = []
    for i, j in combinations(range(n), 2):
        bi, bj = 1 << i, 1 << j
        interchangeable = True
        for mask in range(1 << n):
            if mask & bi or mask & bj:
                continue
            if abs(game.value_mask(mask | bi) - game.value_mask(mask | bj)) > TOL:
                interchangeable = False
                break
        if interchangeable:
            pairs.append((i, j))
    return pairs


# ----------------------------------------------------------------------
# Predicats d'axiomes
# ----------------------------------------------------------------------
def check_efficiency(game: CooperativeGame, phi: np.ndarray, tol: float = TOL) -> bool:
    """``sum_i phi_i == v(N)`` ?"""
    return abs(float(np.sum(phi)) - game.grand_coalition_value()) <= tol


def check_symmetry(game: CooperativeGame, phi: np.ndarray, tol: float = TOL) -> bool:
    """Les joueurs symetriques recoivent-ils la meme part ?"""
    for i, j in symmetric_pairs(game):
        if abs(phi[i] - phi[j]) > tol:
            return False
    return True


def check_null_player(game: CooperativeGame, phi: np.ndarray, tol: float = TOL) -> bool:
    """Les joueurs nuls recoivent-ils zero ?"""
    for i in null_players(game):
        if abs(phi[i]) > tol:
            return False
    return True


def check_additivity(
    game_v: CooperativeGame,
    game_w: CooperativeGame,
    tol: float = TOL,
) -> bool:
    """``phi(v + w) == phi(v) + phi(w)`` ?"""
    if game_v.n != game_w.n:
        raise ValueError("les deux jeux doivent avoir le meme nombre de joueurs")
    n = game_v.n

    def v_plus_w(S):
        return game_v.value(S) + game_w.value(S)

    game_sum = CooperativeGame(n, v_plus_w)
    phi_sum = shapley_exact(game_sum)
    phi_sep = shapley_exact(game_v) + shapley_exact(game_w)
    return bool(np.allclose(phi_sum, phi_sep, atol=tol))


def verify_all_axioms(game: CooperativeGame, phi: np.ndarray = None) -> dict:
    """Renvoie un rapport ``{axiome: bool}`` (hors additivite, binaire)."""
    if phi is None:
        phi = shapley_exact(game)
    return {
        "efficacite": check_efficiency(game, phi),
        "symetrie": check_symmetry(game, phi),
        "joueur_nul": check_null_player(game, phi),
    }
