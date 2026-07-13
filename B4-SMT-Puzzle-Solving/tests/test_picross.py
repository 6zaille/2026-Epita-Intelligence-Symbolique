from my_logic_puzzle_solver.core.solvers import CPSATSolver
from my_logic_puzzle_solver.core.solvers import Z3Solver
from my_logic_puzzle_solver.puzzles import Picross

row_clues = [[1, 1], [2, 2], [5], [3], [1]]
col_clues = [[2], [4], [3], [4], [2]]
for name, solver_cls in [("CP-SAT", CPSATSolver), ("Z3", Z3Solver)]:
    grid = Picross(solver_cls(), row_clues, col_clues).solve()
    print(f"[{name}] Picross:")
    for row in grid:
        print("".join("#" if cell else "." for cell in row))
