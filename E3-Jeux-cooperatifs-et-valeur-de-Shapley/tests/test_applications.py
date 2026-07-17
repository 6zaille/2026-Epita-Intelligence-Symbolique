"""Tests des applications : partage de couts (aeroport) et SHAP (ML)."""

import numpy as np
from sklearn.datasets import make_regression
from sklearn.ensemble import GradientBoostingRegressor

from applications.airport_cost import (
    airport_cost_allocation,
    airport_shapley_closed_form,
)
from applications.shap_ml import explain_instance
from shapley.games import airport_game
from shapley.exact import shapley_exact


def test_airport_closed_form_matches_shapley():
    for costs in [[1, 2, 4], [1, 2, 3, 5, 8], [5, 5, 5], [2, 7, 7, 9]]:
        closed = airport_shapley_closed_form(costs)
        exact = shapley_exact(airport_game(costs))
        assert np.allclose(closed, exact)


def test_airport_allocation_efficient():
    rep = airport_cost_allocation([1, 2, 4, 6, 10])
    assert rep["match"]
    assert abs(rep["total_finance"] - max([1, 2, 4, 6, 10])) < 1e-9


def test_shap_local_accuracy():
    names = [f"f{i}" for i in range(6)]
    X, y = make_regression(n_samples=300, n_features=6, n_informative=4,
                           noise=8.0, random_state=0)
    model = GradientBoostingRegressor(random_state=0).fit(X, y)
    rep = explain_instance(model, X[100], X[:100], names)
    assert rep["local_accuracy_ok"]
    assert abs(rep["somme_shap"] - rep["ecart_a_expliquer"]) < 1e-6


def test_shap_mc_matches_exact():
    names = [f"f{i}" for i in range(5)]
    X, y = make_regression(n_samples=200, n_features=5, n_informative=3,
                           noise=5.0, random_state=1)
    model = GradientBoostingRegressor(random_state=1).fit(X, y)
    rep = explain_instance(model, X[50], X[:80], names, mc_samples=6000, seed=2)
    assert rep["erreur_mc"] < 0.5
