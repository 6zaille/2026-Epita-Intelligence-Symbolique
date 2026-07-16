from ortools.sat.python import cp_model
from typing import Iterable

from ..solver import Solver


class CPSATSolver(Solver):
    """Constraint solver implementation based on OR-Tools CP-SAT.

    This class implements the :class:`Solver` interface using Google's
    OR-Tools CP-SAT backend. It provides methods for creating decision
    variables, adding constraints, solving the model, and retrieving
    solution values.
    """

    def __init__(self):
        """Initialize an empty CP-SAT solver instance.

        Creates a new CP-SAT model and solver, and initializes the
        variable and constraint counters.
        """
        super().__init__()
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()

    def create_int_var(self, name: str, lb: int, ub: int) -> cp_model.IntVar:
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
        cp_model.IntVar
            Newly created integer variable.
        """
        self.num_variables += 1
        v = self.model.new_int_var(lb, ub, name)
        return v

    def create_bool_var(self, name: str) -> cp_model.IntVar:
        """Create a Boolean decision variable.

        Parameters
        ----------
        name : str
            Name of the variable.

        Returns
        -------
        cp_model.IntVar
            Newly created Boolean variable.
        """
        self.num_variables += 1
        v = self.model.new_bool_var(name)
        return v

    def constraint(self, expression) -> None:
        """Add a constraint to the model.

        Parameters
        ----------
        expression : cp_model.BoundedLinearExpression
            Constraint expression to add.

        Returns
        -------
        None
        """
        self.model.add(expression)
        self.num_constraints += 1

    def all_different(self, variables: Iterable) -> None:
        """Add an all-different constraint.

        Parameters
        ----------
        variables : Iterable[cp_model.IntVar]
            Integer variables constrained to take distinct values.

        Returns
        -------
        None
        """
        self.model.add_all_different(variables)
        self.num_constraints += 1

    def exactly_one(self, variables: list) -> None:
        """Add an exactly-one constraint.

        Parameters
        ----------
        variables : list[cp_model.IntVar]
            Boolean variables of which exactly one must be true.

        Returns
        -------
        None
        """
        self.num_constraints += 1
        self.model.add_exactly_one(variables)

    def abs_diff_eq(self, a, b, value: int) -> None:
        """Add an absolute difference constraint.

        Enforces ``|a - b| == value``.

        Parameters
        ----------
        a : cp_model.IntVar
            First integer variable.
        b : cp_model.IntVar
            Second integer variable.
        value : int
            Required absolute difference.

        Returns
        -------
        None
        """
        is_ge = self.model.new_bool_var(f"is_ge_{id(a)}_{id(b)}")
        self.num_variables += 1
        self.model.add(a - b == value).OnlyEnforceIf(is_ge)
        self.model.add(b - a == value).OnlyEnforceIf(is_ge.Not())
        self.num_constraints += 2

    def bool_and(self, *variables) -> cp_model.IntVar:
        """Create the conjunction of Boolean variables.

        Parameters
        ----------
        *variables : cp_model.IntVar
            Boolean variables.

        Returns
        -------
        cp_model.IntVar
            Boolean variable representing the logical AND of the inputs.
        """
        r = self.model.new_bool_var("")
        self.num_variables += 1
        self.model.add_bool_and(variables).only_enforce_if(r)
        self.model.add_bool_or([v.negated() for v in variables] + [r])
        self.num_constraints += 2
        return r

    def bool_or(self, *variables) -> cp_model.IntVar:
        """Create the disjunction of Boolean variables.

        Parameters
        ----------
        *variables : cp_model.IntVar
            Boolean variables.

        Returns
        -------
        cp_model.IntVar
            Boolean variable representing the logical OR of the inputs.
        """
        r = self.model.new_bool_var("")
        self.num_variables += 1
        self.model.add_bool_or(variables).only_enforce_if(r)
        for v in variables:
            self.model.add_implication(v, r)
        self.num_constraints += 1 + len(variables)
        return r

    def bool_not(self, var) -> cp_model.Literal:
        """Negate a Boolean variable.

        Parameters
        ----------
        var : cp_model.IntVar
            Boolean variable.

        Returns
        -------
        cp_model.Literal
            Negated Boolean literal.
        """
        return var.negated()

    def reify(self, expression, negated_expression) -> cp_model.IntVar:
        """Reify a constraint as a Boolean variable.

        Parameters
        ----------
        expression : cp_model.BoundedLinearExpression
            Constraint expression.
        negated_expression : cp_model.BoundedLinearExpression
            Logical negation of ``expression``.

        Returns
        -------
        cp_model.IntVar
            Boolean variable equivalent to the given constraint.
        """
        r = self.model.new_bool_var("")
        self.num_variables += 1
        self.model.add(expression).only_enforce_if(r)
        self.model.add(negated_expression).only_enforce_if(~r)
        self.num_constraints += 2
        return r

    def assert_true(self, var) -> None:
        """Force a Boolean variable to be true.

        Parameters
        ----------
        var : cp_model.IntVar
            Boolean variable to constrain.

        Returns
        -------
        None
        """
        self.model.add(var == 1)
        self.num_constraints += 1

    def solve(self) -> bool:
        """Solve the current CP-SAT model.

        Returns
        -------
        bool
            ``True`` if a feasible or optimal solution is found,
            ``False`` otherwise.
        """
        status = self.solver.solve(self.model)
        return status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    def get_value(self, var) -> int:
        """Return the value assigned to a variable.

        Parameters
        ----------
        var : cp_model.IntVar
            Decision variable.

        Returns
        -------
        int
            Value assigned to the variable in the current solution.
        """
        return self.solver.value(var)
