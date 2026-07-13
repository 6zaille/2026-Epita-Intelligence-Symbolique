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
    def bool_and(self, *variables) -> Any:
        """AND expression of the given `variables`."""
        ...

    @abstractmethod
    def bool_or(self, *variables) -> Any:
        """OR expression of the given `variables`."""
        ...

    @abstractmethod
    def bool_not(self, var) -> Any:
        """Not expression of `var`."""
        ...

    @abstractmethod
    def reify(self, expression, negated_expression) -> Any:
        """New expression equivalent to `expression`.

        `negated_expression` must be `expression`'s exact negation
        (for solvers using double implication).
        """
        ...

    @abstractmethod
    def assert_true(self, var) -> None:
        """Add true constraint on `var`."""
        ...

    def assert_equiv(self, a, b) -> None:
        """Add equivalence constraint between `a` and `b`."""
        self.assert_true(
            self.bool_or(
                self.bool_and(a, b),
                self.bool_and(self.bool_not(a), self.bool_not(b)),
            )
        )

    @abstractmethod
    def solve(self) -> bool: ...

    @abstractmethod
    def get_value(self, var) -> int: ...
