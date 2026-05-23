from rcc8.rcc8solver import RCC8Solver
from rcc8.relations import inverse_relation


# -----------------------------
# helper
# -----------------------------
def build_solver(vars=("A", "B", "C", "D")):
    R = {}

    all_rel = {
        "DC", "EC", "PO", "TPP",
        "NTPP", "TPPI", "NTPPI", "EQ"
    }

    for i in vars:
        for j in vars:
            if i == j:
                continue
            R[(i, j)] = set(all_rel)

    return RCC8Solver(list(vars), R, inverse_relation)


# -----------------------------
# 1. TEST SYMÉTRIE
# -----------------------------
def test_symmetry():
    solver = build_solver(("A", "B"))

    solver.R[("A", "B")] = {"EC"}
    solver.pc2()

    assert "EC" in solver.R[("A", "B")]
    assert "EC" in solver.R[("B", "A")]

    print("TEST SYMÉTRIE OK")


# -----------------------------
# 2. TEST CONTRAINTE SIMPLE
# -----------------------------
def test_simple_coherent():
    solver = build_solver(("A", "B", "C"))

    solver.R[("A", "B")] = {"TPP"}
    solver.R[("B", "C")] = {"EC"}
    solver.R[("A", "C")] = {
        "DC", "EC", "PO", "TPP", "NTPP", "TPPI", "NTPPI"
    }

    solver.pc2()

    # rien ne doit être vide
    assert len(solver.R[("A", "B")]) > 0
    assert len(solver.R[("B", "C")]) > 0
    assert len(solver.R[("A", "C")]) > 0

    print("TEST SIMPLE OK")


# -----------------------------
# 3. TEST INCOHÉRENCE DIRECTE
# -----------------------------
def test_incoherent_direct():
    solver = build_solver(("A", "B", "C"))

    solver.R[("A", "B")] = {"TPP"}
    solver.R[("B", "C")] = {"TPPI"}
    solver.R[("A", "C")] = {"DC"}

    try:
        solver.pc2()
        assert False, "Inconsistency not detected"
    except ValueError:
        print("TEST INCOHERENCE DIRECT OK")


# -----------------------------
# 4. TEST PROPAGATION CHAÎNE
# -----------------------------
def test_chain_propagation():
    solver = build_solver(("A", "B", "C"))

    solver.R[("A", "B")] = {"TPP"}
    solver.R[("B", "C")] = {"TPP"}

    solver.pc2()

    # A-C doit être réduit mais pas vide
    assert len(solver.R[("A", "C")]) > 0

    print("TEST CHAINE OK")


# -----------------------------
# 5. TEST CONTRADICTION CACHÉE
# -----------------------------
def test_hidden_inconsistency():
    solver = build_solver(("A", "B", "C"))

    solver.R[("A", "B")] = {"TPP"}
    solver.R[("B", "C")] = {"NTPPI"}
    solver.R[("C", "A")] = {"DC"}  # contradiction globale

    try:
        solver.pc2()
        assert False, "Should detect inconsistency"
    except ValueError:
        print("TEST HIDDEN INCONSISTENCY OK")


# -----------------------------
# 6. TEST COMPLET STABILITÉ
# -----------------------------
def test_complex_network():
    solver = build_solver(("A", "B", "C", "D"))

    solver.R[("A", "B")] = {"TPP"}
    solver.R[("B", "C")] = {"EC"}
    solver.R[("C", "D")] = {"PO"}
    solver.R[("A", "D")] = {
        "DC", "EC", "PO", "TPP", "NTPP", "TPPI", "NTPPI"
    }

    solver.pc2()

    for (i, j), rels in solver.R.items():
        assert len(rels) > 0

    print("TEST COMPLEXE OK")


# -----------------------------
# RUN ALL
# -----------------------------
if __name__ == "__main__":
    test_symmetry()
    test_simple_coherent()
    test_incoherent_direct()
    test_chain_propagation()
    test_hidden_inconsistency()
    test_complex_network()