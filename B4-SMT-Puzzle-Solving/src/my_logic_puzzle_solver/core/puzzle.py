from abc import ABC, abstractmethod
from typing import Any

from .solver import Solver


class Puzzle(ABC):
    """Abstract base class for constraint-based puzzles.

    A puzzle defines a problem to be solved using a provided
    :class:`Solver` implementation. Concrete puzzle classes must
    implement the :meth:`solve` method to build the model, invoke the
    solver, and return the corresponding solution.
    """

    def __init__(self, solver: Solver):
        """Initialize a puzzle with a solver backend.

        Parameters
        ----------
        solver : Solver
            Solver instance used to create variables, add constraints,
            and compute a solution.
        """
        self.solver = solver

    @abstractmethod
    def solve(self) -> Any | None:
        """Solve the puzzle instance.

        Implementations should create the required variables and
        constraints using the configured solver, then return the
        solution if one exists.

        Returns
        -------
        Any or None
            Puzzle solution in an implementation-specific format, or
            ``None`` if no solution exists.
        """
        ...
