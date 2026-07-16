"""Outil SMT — satisfiabilite modulo theories via Z3.

Le probleme est fourni en **SMT-LIB 2** (le format standard des solveurs SMT),
que les LLM savent generer. On charge les assertions, on appelle le solveur, et
on renvoie sat/unsat/unknown avec, le cas echeant, un modele.

Exemple SMT-LIB2 :
    (declare-const x Int)
    (declare-const y Int)
    (assert (> x 0))
    (assert (= (+ x y) 10))
    (assert (< y x))
"""

from __future__ import annotations

from typing import Any

import z3


def solve_smt(
    smtlib2: str,
    get_model: bool = True,
    timeout_ms: int = 10000,
) -> dict[str, Any]:
    """Verifie la satisfiabilite d'un ensemble de contraintes SMT-LIB2 avec Z3.

    Args:
        smtlib2: le probleme au format SMT-LIB 2 (declarations + assertions).
            Les commandes `(check-sat)`/`(get-model)` eventuelles sont ignorees :
            la verification est pilotee par l'outil.
        get_model: si True et le probleme est `sat`, renvoie un modele temoin.
        timeout_ms: budget temps du solveur en millisecondes.

    Returns:
        dict avec `status` = "sat" | "unsat" | "unknown", un `model` eventuel
        (dict {symbole: valeur}), et un `summary` en langage naturel.
    """
    if not isinstance(smtlib2, str) or not smtlib2.strip():
        return {
            "ok": False,
            "tool": "smt_solve",
            "error": "Le champ 'smtlib2' doit etre une chaine SMT-LIB2 non vide.",
        }

    solver = z3.Solver()
    if timeout_ms and timeout_ms > 0:
        solver.set("timeout", int(timeout_ms))

    try:
        solver.from_string(smtlib2)
    except z3.Z3Exception as exc:
        return {
            "ok": False,
            "tool": "smt_solve",
            "error": f"Erreur d'analyse SMT-LIB2 : {exc}",
        }

    result = solver.check()
    status = str(result)  # 'sat' | 'unsat' | 'unknown'

    out: dict[str, Any] = {
        "ok": True,
        "tool": "smt_solve",
        "status": status,
    }

    if result == z3.sat:
        model = solver.model()
        if get_model:
            out["model"] = {str(d.name()): str(model[d]) for d in model.decls()}
        pairs = ", ".join(f"{k}={v}" for k, v in out.get("model", {}).items())
        out["summary"] = (
            "sat — les contraintes sont satisfiables."
            + (f" Modele temoin : {pairs}." if pairs else "")
        )
    elif result == z3.unsat:
        out["summary"] = (
            "unsat — les contraintes sont insatisfiables : il n'existe aucune "
            "affectation des variables qui les satisfasse toutes."
        )
    else:
        reason = solver.reason_unknown()
        out["reason_unknown"] = reason
        out["summary"] = (
            f"unknown — Z3 n'a pas pu conclure (raison : {reason}). "
            "Essayez d'augmenter timeout_ms ou de simplifier le probleme."
        )

    return out
