from z3 import Int, Bool, Distinct, Solver as Z3NativeSolver, sat
from typing import Iterable

from ..solver import Solver


class Z3Solver(Solver):
    def __init__(self):
        self.solver = Z3NativeSolver()
        self.vars = {}

    def create_int_var(self, name: str, lb: int, ub: int):
        v = Int(name)
        self.vars[name] = v
        self.solver.add(v >= lb, v <= ub)
        return v

    def create_bool_var(self, name: str):
        v = Bool(name)
        self.vars[name] = v
        return v

    def constraint(self, expression):
        self.solver.add(expression)

    def all_different(self, variables: Iterable):
        self.solver.add(Distinct(*variables))

    def solve(self):
        return self.solver.check() == sat

    def get_value(self, var):
        return self.solver.model()[var]
