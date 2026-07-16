import time
from dataclasses import dataclass
from typing import Callable

from .puzzle import Puzzle
from .solver import Solver


@dataclass
class BenchmarkResult:
    """Container for the result of a solver benchmark.

    Stores the outcome of solving a puzzle instance along with
    performance metrics and model statistics.

    Attributes
    ----------
    label : str
        Name identifying the benchmark case.
    solved : bool
        Whether the puzzle was successfully solved.
    time_seconds : float
        Time required to solve the puzzle, in seconds.
    num_variables : int
        Number of variables created by the solver.
    num_constraints : int
        Number of constraints added to the solver model.
    """
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
    """Run a single puzzle solving benchmark.

    Creates a new solver instance and puzzle instance, solves the puzzle,
    and records execution time together with solver statistics.

    Parameters
    ----------
    label : str
        Name identifying the benchmark case.
    solver_factory : Callable[[], Solver]
        Factory function returning a new solver instance.
    puzzle_factory : Callable[[Solver], Puzzle]
        Factory function returning a puzzle instance configured with
        the provided solver.

    Returns
    -------
    BenchmarkResult
        Benchmark outcome containing solving status, execution time,
        and solver statistics.
    """
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
    """Run multiple puzzle solving benchmarks.

    Parameters
    ----------
    cases : list[tuple[str, Callable[[], Solver], Callable[[Solver], Puzzle]]]
        Benchmark cases. Each case contains:
        
        - a benchmark label,
        - a solver factory function,
        - a puzzle factory function.

    Returns
    -------
    list[BenchmarkResult]
        List of benchmark results in the same order as the input cases.
    """
    return [run_benchmark(*case) for case in cases]
