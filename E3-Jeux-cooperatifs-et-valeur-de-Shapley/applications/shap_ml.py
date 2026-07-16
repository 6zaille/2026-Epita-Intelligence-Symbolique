"""Explicabilite des modeles de ML : les valeurs SHAP comme valeur de Shapley.

Pour expliquer la prediction ``f(x*)`` d'un modele sur une instance ``x*``, on
construit un jeu cooperatif dont les *joueurs sont les features*. La valeur
d'une coalition ``S`` de features est la prediction moyenne du modele quand on
*connait* les valeurs ``x*_S`` et qu'on *marginalise* les autres sur un jeu de
donnees de reference (background) :

.. math::

    v(S) = \\mathbb{E}_{b \\sim \\text{background}}\\bigl[
        f(x^*_S, b_{-S})\\bigr] - \\mathbb{E}_b[f(b)].

Le terme constant recentre le jeu pour que ``v(\\emptyset) = 0``. La valeur de
Shapley ``phi_i`` de ce jeu est alors la **valeur SHAP** de la feature ``i``
(Lundberg & Lee, 2017, formulation *interventionnelle*/marginale).

L'axiome d'**efficacite** devient ici la propriete de *local accuracy* :

.. math::   \\sum_i \\phi_i = f(x^*) - \\mathbb{E}_b[f(b)],

c'est-a-dire que les contributions des features expliquent *exactement* l'ecart
entre la prediction et la prediction de reference. On calcule ces valeurs de
maniere exacte (enumeration des ``2^n`` coalitions de features, viable pour
``n`` petit) et on les recoupe avec l'estimateur Monte Carlo.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from shapley.exact import shapley_exact
from shapley.game import CooperativeGame
from shapley.monte_carlo import shapley_monte_carlo


def make_shap_game(
    model,
    x_star: np.ndarray,
    background: np.ndarray,
    feature_names: Optional[Sequence[str]] = None,
) -> CooperativeGame:
    """Construit le jeu cooperatif SHAP pour une instance ``x_star``.

    Parameters
    ----------
    model:
        Objet avec une methode ``predict`` (scalaire par ligne).
    x_star:
        Instance a expliquer, forme ``(n_features,)``.
    background:
        Echantillon de reference ``(n_bg, n_features)`` pour la marginalisation.
    feature_names:
        Etiquettes des features.
    """
    x_star = np.asarray(x_star, dtype=float).ravel()
    background = np.asarray(background, dtype=float)
    n = x_star.shape[0]
    baseline = float(np.mean(model.predict(background)))

    def v(S):
        # coalition S de features connues : on impose x*_S, on garde le fond
        # (marginalisation interventionnelle) et on moyenne les predictions.
        X = background.copy()
        for i in S:
            X[:, i] = x_star[i]
        return float(np.mean(model.predict(X))) - baseline

    names = list(feature_names) if feature_names is not None else [f"f{i}" for i in range(n)]
    game = CooperativeGame(n, v, names=names)
    game._baseline = baseline  # type: ignore[attr-defined]
    game._prediction = float(model.predict(x_star.reshape(1, -1))[0])  # type: ignore[attr-defined]
    return game


def explain_instance(
    model,
    x_star: np.ndarray,
    background: np.ndarray,
    feature_names: Optional[Sequence[str]] = None,
    mc_samples: int = 0,
    seed: int = 0,
) -> dict:
    """Explique ``f(x_star)`` par valeurs SHAP exactes (+ MC optionnel).

    Verifie la *local accuracy* (efficacite) :
    ``sum phi_i ~= f(x*) - E[f]``.
    """
    game = make_shap_game(model, x_star, background, feature_names)
    phi = shapley_exact(game)
    baseline = game._baseline  # type: ignore[attr-defined]
    prediction = game._prediction  # type: ignore[attr-defined]

    report = {
        "noms": game.names,
        "shap_exact": phi,
        "baseline": baseline,
        "prediction": prediction,
        "somme_shap": float(np.sum(phi)),
        "ecart_a_expliquer": prediction - baseline,
        "local_accuracy_ok": bool(abs(float(np.sum(phi)) - (prediction - baseline)) < 1e-6),
    }
    if mc_samples > 0:
        mc = shapley_monte_carlo(game, n_samples=mc_samples, seed=seed)
        report["shap_mc"] = mc
        report["erreur_mc"] = float(np.max(np.abs(mc - phi)))
    return report
