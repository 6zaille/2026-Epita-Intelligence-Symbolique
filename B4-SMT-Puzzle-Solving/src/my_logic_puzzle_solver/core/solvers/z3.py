from typing import Iterable

import z3

from ..solver import Solver


class Z3Solver(Solver):
    def __init__(self):
        self.solver = z3.Solver()
        self.model = None
        # self.vars = {}

    def create_int_var(self, name: str, lb: int, ub: int):
        v = z3.Int(name)
        # self.vars[name] = v
        self.solver.add(v >= lb, v <= ub)
        return v

    def create_bool_var(self, name: str):
        v = z3.Bool(name)
        # self.vars[name] = v
        return v

    def constraint(self, expression):
        self.solver.add(expression)

    def all_different(self, variables: Iterable):
        self.solver.add(z3.Distinct(*variables))

    def abs_diff_eq(self, a, b, value: int) -> None:
        self.solver.add(z3.If(a - b >= 0, a - b, b - a) == value)

    def solve(self):
        valid = self.solver.check() == z3.sat
        if valid:
            self.model = self.solver.model()
        return valid

    def get_value(self, var):
        if self.model is None:
            raise ValueError("Solver didn't solve any problem yet.")
        return self.model.evaluate(var, model_completion=True).as_long()
