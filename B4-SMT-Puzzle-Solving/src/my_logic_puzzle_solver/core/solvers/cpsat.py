from ortools.sat.python import cp_model
from typing import Iterable

from ..solver import Solver


class CPSATSolver(Solver):
    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        # self.vars = {}

    def create_int_var(self, name: str, lb: int, ub: int):
        v = self.model.new_int_var(lb, ub, name)
        # self.vars[name] = v
        return v

    def create_bool_var(self, name: str):
        v = self.model.new_bool_var(name)
        # self.vars[name] = v
        return v

    def constraint(self, expression):
        self.model.add(expression)

    def all_different(self, variables: Iterable):
        self.model.add_all_different(variables)

    def abs_diff_eq(self, a, b, value: int) -> None:
        is_ge = self.model.new_bool_var(f"is_ge_{id(a)}_{id(b)}")
        self.model.add(a - b == value).OnlyEnforceIf(is_ge)
        self.model.add(b - a == value).OnlyEnforceIf(is_ge.Not())

    def bool_and(self, *variables):
        r = self.model.new_bool_var("")
        self.model.add_bool_and(variables).only_enforce_if(r)
        self.model.add_bool_or([v.negated() for v in variables] + [r])
        return r

    def bool_or(self, *variables):
        r = self.model.new_bool_var("")
        self.model.add_bool_or(variables).only_enforce_if(r)
        for v in variables:
            self.model.add_implication(v, r)
        return r

    def bool_not(self, var):
        return var.negated()

    def reify(self, expression, negated_expression):
        r = self.model.new_bool_var("")
        self.model.add(expression).only_enforce_if(r)
        self.model.add(negated_expression).only_enforce_if(~r)
        return r

    def assert_true(self, var) -> None:
        self.model.add(var == 1)

    def solve(self):
        status = self.solver.solve(self.model)
        return status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    def get_value(self, var):
        return self.solver.value(var)
