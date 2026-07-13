from my_logic_puzzle_solver.core.solvers import CPSATSolver
from my_logic_puzzle_solver.core.solvers import Z3Solver
from my_logic_puzzle_solver.puzzles import Zebra

for name, solver_cls in [("CP-SAT", CPSATSolver), ("Z3", Z3Solver)]:
    result = Zebra(solver_cls()).solve()
    owner = next(h for h, attrs in result.items() if attrs["pet"] == "<animal>")
    print(f"[{name}] Maison {owner} possède le poisson -> {result[owner]}")
