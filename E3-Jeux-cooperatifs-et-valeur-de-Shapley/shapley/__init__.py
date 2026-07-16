"""Jeux cooperatifs et valeur de Shapley (projet E3, IA symbolique).

Package Python pur pour :

* representer un jeu cooperatif TU (:class:`~shapley.game.CooperativeGame`) ;
* calculer la valeur de Shapley exacte (formule des coalitions ``O(2^n)`` et
  enumeration des permutations ``O(n!)``) ;
* l'approcher par echantillonnage Monte Carlo (Castro et al. 2009) ;
* verifier numeriquement les quatre axiomes (efficacite, symetrie, joueur nul,
  additivite) ;
* etudier le coeur, la convexite, et le theoreme « Shapley dans le coeur » ;
* calculer les indices de pouvoir (Shapley-Shubik, Banzhaf).
"""

from .game import CooperativeGame, coalition_to_mask, mask_to_coalition
from .exact import shapley_exact, shapley_by_permutations, marginal_vector
from .monte_carlo import shapley_monte_carlo, convergence_curve
from .axioms import (
    check_efficiency,
    check_symmetry,
    check_null_player,
    check_additivity,
    verify_all_axioms,
    null_players,
    symmetric_pairs,
)
from .core import (
    is_convex,
    is_superadditive,
    in_core,
    core_constraints_violation,
    core_vertices_convex,
    core_check_report,
)
from .power_index import shapley_shubik_index, banzhaf_index, pivot_analysis
from . import games

__all__ = [
    "CooperativeGame",
    "coalition_to_mask",
    "mask_to_coalition",
    "shapley_exact",
    "shapley_by_permutations",
    "marginal_vector",
    "shapley_monte_carlo",
    "convergence_curve",
    "check_efficiency",
    "check_symmetry",
    "check_null_player",
    "check_additivity",
    "verify_all_axioms",
    "null_players",
    "symmetric_pairs",
    "is_convex",
    "is_superadditive",
    "in_core",
    "core_constraints_violation",
    "core_vertices_convex",
    "core_check_report",
    "shapley_shubik_index",
    "banzhaf_index",
    "pivot_analysis",
    "games",
]

__version__ = "1.0.0"
