import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from formal.axioms import (
    prove_additivity,
    prove_all_axioms,
    prove_all_deegan_packel_axioms,
    prove_banzhaf_null_player,
    prove_banzhaf_symmetry,
    prove_deegan_packel_efficiency,
    prove_deegan_packel_null_player,
    prove_deegan_packel_symmetry,
    prove_efficiency,
    prove_null_player,
    prove_symmetry,
    refute_banzhaf_efficiency,
)
from formal.distinctions import (
    _satisfies_symmetry_and_null,
    axiom_matrix,
    banzhaf_additivity_counterexample,
)
from indices.deegan_packel import deegan_packel


@pytest.mark.parametrize("n", [3, 4, 5])
def test_efficiency_proved(n):
    result = prove_efficiency(n)
    assert result.proved, result.detail


@pytest.mark.parametrize("n", [3, 4, 5])
def test_null_player_proved(n):
    result = prove_null_player(n)
    assert result.proved, result.detail


@pytest.mark.parametrize("n", [3, 4, 5])
def test_symmetry_proved(n):
    result = prove_symmetry(n)
    assert result.proved, result.detail


@pytest.mark.parametrize("n", [3, 4, 5])
def test_additivity_proved(n):
    result = prove_additivity(n)
    assert result.proved, result.detail


def test_all_axioms_bundle():
    results = prove_all_axioms(4)
    assert len(results) == 4
    assert all(r.proved for r in results)


@pytest.mark.parametrize("n", [3, 4])
def test_banzhaf_symmetry_and_null_proved(n):
    assert prove_banzhaf_symmetry(n).proved
    assert prove_banzhaf_null_player(n).proved


@pytest.mark.parametrize("n", [3, 4])
def test_banzhaf_violates_efficiency(n):
    assert refute_banzhaf_efficiency(n).proved


def test_banzhaf_not_additive_counterexample():
    ce = banzhaf_additivity_counterexample()
    assert abs(ce["beta(v+w)_0"] - ce["beta(v)+beta(w)"]) > 1e-6


@pytest.mark.parametrize("n", [3, 4, 5])
def test_deegan_packel_symmetry_proved(n):
    result = prove_deegan_packel_symmetry(n)
    assert result.proved, result.detail


@pytest.mark.parametrize("n", [3, 4, 5])
def test_deegan_packel_null_player_proved(n):
    result = prove_deegan_packel_null_player(n)
    assert result.proved, result.detail


@pytest.mark.parametrize("n", [3, 4, 5])
def test_deegan_packel_efficiency_proved(n):
    result = prove_deegan_packel_efficiency(n)
    assert result.proved, result.detail


def test_deegan_packel_bundle():
    results = prove_all_deegan_packel_axioms(4)
    assert len(results) == 3
    assert all(r.proved for r in results)


def test_deegan_packel_empirical_cross_check():
    """La preuve Z3 est doublee d'une verification empirique sur une batterie de jeux."""
    assert _satisfies_symmetry_and_null(deegan_packel)


def test_axiom_matrix_distinguishes_indices():
    rows = {r["Axiome"]: r for r in axiom_matrix(4)}
    assert rows["Efficacite (somme = 1)"]["Shapley-Shubik"].startswith("satisfait")
    assert rows["Efficacite (somme = 1)"]["Banzhaf"].startswith("viole")
    assert rows["Additivite"]["Shapley-Shubik"].startswith("satisfait")
    assert rows["Additivite"]["Banzhaf"].startswith("viole")


def test_axiom_matrix_deegan_packel_proved_by_z3():
    rows = {r["Axiome"]: r for r in axiom_matrix(4)}
    assert "preuve Z3" in rows["Symetrie"]["Deegan-Packel"]
    assert "preuve Z3" in rows["Joueur nul"]["Deegan-Packel"]
    assert "preuve Z3" in rows["Efficacite (somme = 1)"]["Deegan-Packel"]
