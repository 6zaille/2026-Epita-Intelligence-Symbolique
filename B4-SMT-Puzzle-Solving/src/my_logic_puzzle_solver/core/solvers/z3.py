from typing import Iterable

import z3

from ..solver import Solver


class Z3Solver(Solver):
    """Constraint solver implementation based on the Z3 SMT solver.

    This class implements the :class:`Solver` interface using the Z3
    theorem prover. It provides methods for creating variables, adding
    constraints, solving the model, and retrieving solution values.
    """

    def __init__(self):
        """Initialize an empty Z3 solver instance.

        Creates a new Z3 solver and initializes the variable and
        constraint counters.
        """
        super().__init__()
        self.solver = z3.Solver()
        self.model = None

    def create_int_var(self, name: str, lb: int, ub: int) -> z3.ArithRef:
        """Create an integer decision variable.

        The variable domain is enforced by adding lower and upper bound
        constraints to the solver.

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
        z3.ArithRef
            Newly created integer variable.
        """
        v = z3.Int(name)
        self.num_variables += 1
        self.solver.add(v >= lb, v <= ub)
        self.num_constraints += 1
        return v

    def create_bool_var(self, name: str) -> z3.BoolRef:
        """Create a Boolean decision variable.

        Parameters
        ----------
        name : str
            Name of the variable.

        Returns
        -------
        z3.BoolRef
            Newly created Boolean variable.
        """
        v = z3.Bool(name)
        self.num_variables += 1
        return v

    def constraint(self, expression) -> None:
        """Add a constraint to the solver.

        Parameters
        ----------
        expression : z3.BoolRef
            Constraint expression to add.

        Returns
        -------
        None
        """
        self.solver.add(expression)
        self.num_constraints += 1

    def all_different(self, variables: Iterable) -> None:
        """Add an all-different constraint.

        Parameters
        ----------
        variables : Iterable[z3.ArithRef]
            Integer variables constrained to take distinct values.

        Returns
        -------
        None
        """
        self.solver.add(z3.Distinct(*variables))
        self.num_constraints += 1

    def exactly_one(self, variables: list) -> None:
        """Add an exactly-one constraint.

        Parameters
        ----------
        variables : list[z3.BoolRef]
            Boolean variables of which exactly one must be true.

        Returns
        -------
        None
        """
        self.num_constraints += 1
        self.solver.add(z3.PbEq([(v, 1) for v in variables], 1))

    def abs_diff_eq(self, a, b, value: int) -> None:
        """Add an absolute difference constraint.

        Enforces ``|a - b| == value``.

        Parameters
        ----------
        a : z3.ArithRef
            First integer variable.
        b : z3.ArithRef
            Second integer variable.
        value : int
            Required absolute difference.

        Returns
        -------
        None
        """
        self.solver.add(z3.If(a - b >= 0, a - b, b - a) == value)
        self.num_constraints += 1

    def bool_and(self, *variables) -> z3.BoolRef:
        """Create the conjunction of Boolean variables.

        Parameters
        ----------
        *variables : z3.BoolRef
            Boolean variables or Boolean expressions.

        Returns
        -------
        z3.BoolRef
            Boolean expression representing the logical AND of the inputs.
        """
        return z3.And(*variables)

    def bool_or(self, *variables) -> z3.BoolRef:
        """Create the disjunction of Boolean variables.

        Parameters
        ----------
        *variables : z3.BoolRef
            Boolean variables or Boolean expressions.

        Returns
        -------
        z3.BoolRef
            Boolean expression representing the logical OR of the inputs.
        """
        return z3.Or(*variables)

    def bool_not(self, var) -> z3.BoolRef:
        """Negate a Boolean variable or expression.

        Parameters
        ----------
        var : z3.BoolRef
            Boolean variable or expression.

        Returns
        -------
        z3.BoolRef
            Negated Boolean expression.
        """
        return z3.Not(var)

    def reify(self, expression, negated_expression) -> z3.BoolRef:
        """Return a Boolean expression equivalent to a constraint.

        Unlike CP-SAT, Z3 directly represents constraints as Boolean
        expressions. Therefore, this method simply returns
        ``expression`` and ignores ``negated_expression``.

        Parameters
        ----------
        expression : z3.BoolRef
            Constraint expression.
        negated_expression : z3.BoolRef
            Logical negation of ``expression``. This parameter is ignored.

        Returns
        -------
        z3.BoolRef
            The input Boolean expression.
        """
        return expression

    def assert_true(self, var) -> None:
        """Assert that a Boolean expression is true.

        Parameters
        ----------
        var : z3.BoolRef
            Boolean variable or expression.

        Returns
        -------
        None
        """
        self.solver.add(var)
        self.num_constraints += 1

    def solve(self) -> bool:
        """Solve the current constraint model.

        If the model is satisfiable, the resulting model is stored for
        subsequent calls to :meth:`get_value`.

        Returns
        -------
        bool
            ``True`` if the model is satisfiable, ``False`` otherwise.
        """
        valid = self.solver.check() == z3.sat
        if valid:
            self.model = self.solver.model()
        return valid

    def get_value(self, var) -> int | bool:
        """Return the value assigned to a variable.

        Parameters
        ----------
        var : z3.ExprRef
            Decision variable.

        Returns
        -------
        int or bool
            Value assigned to the variable in the current model.

        Raises
        ------
        ValueError
            If :meth:`solve` has not been called successfully.
        """
        if self.model is None:
            raise ValueError("Solver didn't solve any problem yet.")
        value = self.model.evaluate(var, model_completion=True)
        return value.as_long() if z3.is_int(var) else bool(value)
