from my_logic_puzzle_solver.puzzles import Zebra, Picross
from my_logic_puzzle_solver.core.solvers import CPSATSolver, Z3Solver
from my_logic_puzzle_solver.core.benchmark import run_benchmarks

row_clues = [[1, 1], [2, 2], [5], [3], [1]]
col_clues = [[2], [4], [3], [4], [2]]

results = run_benchmarks(
    [
        ("Zebra/CP-SAT", CPSATSolver, lambda s: Zebra(s)),
        ("Zebra/Z3", Z3Solver, lambda s: Zebra(s)),
        (
            "Picross/CP-SAT",
            CPSATSolver,
            lambda s: Picross(s, row_clues, col_clues),
        ),
        ("Picross/Z3", Z3Solver, lambda s: Picross(s, row_clues, col_clues)),
    ]
)
for r in results:
    print(
        f"{r.label}: solved={r.solved} temps={r.time_seconds:.4f}s vars={r.num_variables} contraintes={r.num_constraints}"
    )
