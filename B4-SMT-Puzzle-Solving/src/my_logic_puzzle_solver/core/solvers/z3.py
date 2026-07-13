from typing import Iterable

import z3

from ..solver import Solver


class Z3Solver(Solver):
    def __init__(self):
        super().__init__()
        self.solver = z3.Solver()
        self.model = None

    def create_int_var(self, name: str, lb: int, ub: int):
        v = z3.Int(name)
        self.num_variables += 1
        self.solver.add(v >= lb, v <= ub)
        self.num_constraints += 1
        return v

    def create_bool_var(self, name: str):
        v = z3.Bool(name)
        self.num_variables += 1
        return v

    def constraint(self, expression):
        self.solver.add(expression)
        self.num_constraints += 1

    def all_different(self, variables: Iterable):
        self.solver.add(z3.Distinct(*variables))
        self.num_constraints += 1

    def exactly_one(self, variables: list) -> None:
        self.num_constraints += 1
        self.solver.add(z3.PbEq([(v, 1) for v in variables], 1))

    def abs_diff_eq(self, a, b, value: int) -> None:
        self.solver.add(z3.If(a - b >= 0, a - b, b - a) == value)
        self.num_constraints += 1

    def bool_and(self, *variables):
        return z3.And(*variables)

    def bool_or(self, *variables):
        return z3.Or(*variables)

    def bool_not(self, var):
        return z3.Not(var)

    def reify(self, expression, negated_expression):
        return expression

    def assert_true(self, var) -> None:
        self.solver.add(var)
        self.num_constraints += 1

    def solve(self):
        valid = self.solver.check() == z3.sat
        if valid:
            self.model = self.solver.model()
        return valid

    def get_value(self, var):
        if self.model is None:
            raise ValueError("Solver didn't solve any problem yet.")
        value = self.model.evaluate(var, model_completion=True)
        return value.as_long() if z3.is_int(var) else bool(value)
