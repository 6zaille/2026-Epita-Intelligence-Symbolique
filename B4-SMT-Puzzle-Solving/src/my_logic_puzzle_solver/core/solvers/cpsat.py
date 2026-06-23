from ortools.sat.python import cp_model
from typing import Iterable

from ..solver import Solver


class CPSATSolver(Solver):
    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.vars = {}

    def create_int_var(self, name: str, lb: int, ub: int):
        v = self.model.new_int_var(lb, ub, name)
        self.vars[name] = v
        return v

    def create_bool_var(self, name: str):
        v = self.model.new_bool_var(name)
        self.vars[name] = v
        return v

    def constraint(self, expression):
        self.model.add(expression)

    def all_different(self, variables: Iterable):
        self.model.add_all_different(variables)

    def solve(self):
        status = self.solver.solve(self.model)
        return status in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    def get_value(self, var):
        return self.solver.value(var)
