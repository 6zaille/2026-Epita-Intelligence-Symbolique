"""Approximation de la valeur de Shapley par echantillonnage Monte Carlo.

Algorithme de Castro, Gomez & Tejada (2009). La valeur de Shapley s'ecrit
comme une esperance sur les permutations uniformes :

.. math::

    \\varphi_i(v) = \\mathbb{E}_{\\pi}\\bigl[
        v(P_i^\\pi \\cup \\{i\\}) - v(P_i^\\pi)\\bigr].

On l'estime en tirant ``m`` permutations aleatoires et en moyennant les
contributions marginales. Chaque permutation tiree fournit *en une passe* une
contribution marginale pour **chacun** des ``n`` joueurs, ce qui rend
l'estimateur tres econome en evaluations de ``v`` (``m(n+1)`` au lieu de
``2^n``). L'estimateur est sans biais et son erreur decroit en
``O(1/\\sqrt{m})`` (theoreme central limite).
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from .game import CooperativeGame


def shapley_monte_carlo(
    game: CooperativeGame,
    n_samples: int = 10000,
    seed: Optional[int] = None,
    return_std: bool = False,
):
    """Estime la valeur de Shapley par ``n_samples`` permutations aleatoires.

    Parameters
    ----------
    game:
        Le jeu cooperatif.
    n_samples:
        Nombre ``m`` de permutations tirees.
    seed:
        Graine du generateur aleatoire (reproductibilite).
    return_std:
        Si ``True``, renvoie aussi l'erreur-type estimee de chaque composante
        (ecart-type de l'estimateur = ecart-type des marginales / sqrt(m)).

    Returns
    -------
    phi : ndarray
        Estimation de la valeur de Shapley.
    std : ndarray, optionnel
        Erreur-type estimee (si ``return_std=True``).
    """
    n = game.n
    rng = np.random.default_rng(seed)
    if n == 0:
        return (np.zeros(0), np.zeros(0)) if return_std else np.zeros(0)

    # Statistiques en ligne (Welford) pour la moyenne et la variance des
    # contributions marginales de chaque joueur.
    mean = np.zeros(n)
    m2 = np.zeros(n)

    order = np.arange(n)
    for k in range(1, n_samples + 1):
        rng.shuffle(order)
        mask = 0
        prev = 0.0
        for i in order:
            new_mask = mask | (1 << int(i))
            val = game.value_mask(new_mask)
            contrib = val - prev
            # mise a jour de Welford pour le joueur i
            delta = contrib - mean[i]
            mean[i] += delta / k
            m2[i] += delta * (contrib - mean[i])
            mask, prev = new_mask, val

    if return_std:
        var = m2 / max(n_samples - 1, 1)
        std = np.sqrt(var / n_samples)  # erreur-type de la moyenne
        return mean, std
    return mean


def convergence_curve(
    game: CooperativeGame,
    exact: np.ndarray,
    sample_sizes,
    seed: Optional[int] = None,
) -> dict:
    """Trace la convergence de l'estimateur vers la valeur exacte.

    Pour chaque taille d'echantillon ``m`` dans ``sample_sizes``, calcule
    l'erreur maximale absolue ``max_i |phi_hat_i(m) - phi_i|``. Les
    estimations sont produites de facon incrementale (un seul flux de
    permutations reutilise), ce qui reflete honnetement la trajectoire de
    convergence.

    Returns
    -------
    dict avec les cles ``sizes`` et ``errors`` (listes de meme longueur).
    """
    n = game.n
    rng = np.random.default_rng(seed)
    sizes = sorted(int(s) for s in sample_sizes)
    max_m = sizes[-1]

    mean = np.zeros(n)
    order = np.arange(n)
    errors = []
    idx = 0
    for k in range(1, max_m + 1):
        rng.shuffle(order)
        mask = 0
        prev = 0.0
        for i in order:
            new_mask = mask | (1 << int(i))
            val = game.value_mask(new_mask)
            contrib = val - prev
            mean[i] += (contrib - mean[i]) / k
            mask, prev = new_mask, val
        if idx < len(sizes) and k == sizes[idx]:
            errors.append(float(np.max(np.abs(mean - exact))))
            idx += 1
    return {"sizes": sizes, "errors": errors}
