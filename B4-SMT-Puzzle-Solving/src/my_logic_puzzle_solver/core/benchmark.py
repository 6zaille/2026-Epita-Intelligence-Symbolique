import time
from dataclasses import dataclass
from typing import Callable

from .puzzle import Puzzle
from .solver import Solver


@dataclass
class BenchmarkResult:
    label: str
    solved: bool
    time_seconds: float
    num_variables: int
    num_constraints: int


def run_benchmark(
    label: str,
    solver_factory: Callable[[], Solver],
    puzzle_factory: Callable[[Solver], Puzzle],
) -> BenchmarkResult:
    solver = solver_factory()
    puzzle = puzzle_factory(solver)
    start = time.perf_counter()
    result = puzzle.solve()
    elapsed = time.perf_counter() - start
    return BenchmarkResult(
        label=label,
        solved=result is not None,
        time_seconds=elapsed,
        num_variables=solver.num_variables,
        num_constraints=solver.num_constraints,
    )


def run_benchmarks(
    cases: list[tuple[str, Callable[[], Solver], Callable[[Solver], Puzzle]]],
) -> list[BenchmarkResult]:
    return [run_benchmark(*case) for case in cases]
