from abc import ABC, abstractmethod
from typing import Any


class Solver(ABC):
    """Abstract interface for constraint programming solvers.

    This class defines a common API for creating variables, adding
    constraints, solving a constraint satisfaction model, and retrieving
    variable values. Concrete solver implementations must implement all
    abstract methods.
    """

    def __init__(self):
        """Initialize an empty solver instance.

        Initializes the counters tracking the number of created variables
        and constraints for benchmarks.
        """
        self.num_variables = 0
        self.num_constraints = 0

    @abstractmethod
    def create_int_var(self, name: str, lb: int, ub: int) -> Any:
        """Create an integer decision variable.

        Parameters
        ----------
        name : str
            Name of the variable.
        lb : int
            Inclusive lower bound of the variable domain.
        ub : int
            Inclusive upper bound of the variable domain.

        Returns
        -------
        Any
            Solver-specific integer variable object.
        """
        ...

    @abstractmethod
    def create_bool_var(self, name: str) -> Any:
        """Create a Boolean decision variable.

        Parameters
        ----------
        name : str
            Name of the variable.

        Returns
        -------
        Any
            Solver-specific Boolean variable object.
        """
        ...

    @abstractmethod
    def constraint(self, expression) -> None:
        """Add a constraint to the model.

        Parameters
        ----------
        expression : Any
            Solver-specific constraint expression.

        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def all_different(self, variables: list) -> None:
        """Add an all-different constraint.

        Enforces that all variables take pairwise distinct values.

        Parameters
        ----------
        variables : list
            List of decision variables.

        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def exactly_one(self, variables: list) -> None:
        """Add an exactly-one constraint.

        Enforces that exactly one Boolean variable is assigned ``True``.

        Parameters
        ----------
        variables : list
            List of Boolean variables.

        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def abs_diff_eq(self, a, b, value: int) -> None:
        """Add an absolute difference constraint.

        Enforces ``|a - b| == value``.

        Parameters
        ----------
        a : Any
            First integer variable or expression.
        b : Any
            Second integer variable or expression.
        value : int
            Required absolute difference.

        Returns
        -------
        None
        """
        ...

    @abstractmethod
    def bool_and(self, *variables) -> Any:
        """Create the conjunction of Boolean variables.

        Parameters
        ----------
        *variables : Any
            Boolean variables or Boolean expressions.

        Returns
        -------
        Any
            Solver-specific Boolean expression representing the logical AND.
        """
        ...

    @abstractmethod
    def bool_or(self, *variables) -> Any:
        """Create the disjunction of Boolean variables.

        Parameters
        ----------
        *variables : Any
            Boolean variables or Boolean expressions.

        Returns
        -------
        Any
            Solver-specific Boolean expression representing the logical OR.
        """
        ...

    @abstractmethod
    def bool_not(self, var) -> Any:
        """Negate a Boolean variable or expression.

        Parameters
        ----------
        var : Any
            Boolean variable or Boolean expression.

        Returns
        -------
        Any
            Solver-specific Boolean expression representing the logical NOT.
        """
        ...

    @abstractmethod
    def reify(self, expression, negated_expression) -> Any:
        """Create a Boolean variable equivalent to a constraint.

        Parameters
        ----------
        expression : Any
            Constraint expression to reify.
        negated_expression : Any
            Exact logical negation of ``expression``.

        Returns
        -------
        Any
            Solver-specific Boolean variable or expression equivalent to
            ``expression``.
        """
        ...

    @abstractmethod
    def assert_true(self, var) -> None:
        """Force a Boolean variable or expression to be true.

        Parameters
        ----------
        var : Any
            Boolean variable or Boolean expression.

        Returns
        -------
        None
        """
        ...

    def assert_equiv(self, a, b) -> None:
        """Add a logical equivalence constraint.

        Enforces that ``a`` and ``b`` evaluate to the same Boolean value.

        Parameters
        ----------
        a : Any
            First Boolean variable or expression.
        b : Any
            Second Boolean variable or expression.

        Returns
        -------
        None
        """
        self.assert_true(
            self.bool_or(
                self.bool_and(a, b),
                self.bool_and(self.bool_not(a), self.bool_not(b)),
            )
        )

    @abstractmethod
    def solve(self) -> bool:
        """Solve the current constraint model.

        Returns
        -------
        bool
            ``True`` if a feasible solution is found, otherwise ``False``.
        """
        ...

    @abstractmethod
    def get_value(self, var) -> int:
        """Return the value assigned to a variable.

        Parameters
        ----------
        var : Any
            Solver-specific decision variable.

        Returns
        -------
        int
            Value assigned to the variable in the current solution.
        """
        ...
