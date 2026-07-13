from my_logic_puzzle_solver.core.benchmark import run_benchmarks
from my_logic_puzzle_solver.core.solvers.cpsat import CPSATSolver
from my_logic_puzzle_solver.core.solvers.z3 import Z3Solver
from my_logic_puzzle_solver.puzzles.sudoku import (
    SudokuBoolean,
    SudokuInteger,
    SudokuMixed,
)

sudoku_grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]
sudoku_cases = []
for enc_name, enc_cls in [
    ("bool", SudokuBoolean),
    ("int", SudokuInteger),
    ("mixte", SudokuMixed),
]:
    for solver_name, solver_cls in [("CP-SAT", CPSATSolver), ("Z3", Z3Solver)]:
        sudoku_cases.append(
            (
                f"Sudoku/{enc_name}/{solver_name}",
                solver_cls,
                lambda s, cls=enc_cls: cls(s, sudoku_grid),
            )
        )
sudoku_results = run_benchmarks(sudoku_cases)  # ty:ignore[invalid-argument-type]
for r in sudoku_results:
    print(
        f"{r.label}: solved={r.solved} temps={r.time_seconds:.4f}s vars={r.num_variables} contraintes={r.num_constraints}"
    )
