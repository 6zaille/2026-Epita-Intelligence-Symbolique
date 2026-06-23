from abc import ABC, abstractmethod
from typing import Any

from .solver import Solver


class Puzzle(ABC):
    def __init__(self, solver: Solver):
        self.solver = solver

    @abstractmethod
    def solve(self) -> Any | None: ...
