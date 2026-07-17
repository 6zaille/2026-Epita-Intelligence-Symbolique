from my_logic_puzzle_solver.core.solvers import CPSATSolver
from my_logic_puzzle_solver.core.solvers import Z3Solver
from my_logic_puzzle_solver.puzzles import KnightsKnaves

persons = ["A", "B"]
statements = {
    "A": lambda k, s: s.bool_and(s.bool_not(k["A"]), s.bool_not(k["B"])),
}
for name, solver_cls in [("CP-SAT", CPSATSolver), ("Z3", Z3Solver)]:
    result = KnightsKnaves(solver_cls(), persons, statements).solve()
    print(f"[{name}] Knights and Knaves -> {result}")
