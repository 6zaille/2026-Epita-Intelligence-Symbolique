from abc import ABC, abstractmethod
from typing import Any


class Solver(ABC):
    @abstractmethod
    def create_int_var(self, name: str, lb: int, ub: int) -> Any: ...

    @abstractmethod
    def create_bool_var(self, name: str) -> Any: ...

    @abstractmethod
    def constraint(self, expression) -> None: ...

    @abstractmethod
    def all_different(self, variables: list) -> None: ...

    @abstractmethod
    def abs_diff_eq(self, a, b, value: int) -> None:
        """Adds constraint `|a - b| == value`."""
        ...

    @abstractmethod
    def solve(self) -> bool: ...

    @abstractmethod
    def get_value(self, var) -> int: ...
