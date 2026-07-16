from ..core import Puzzle, Solver


class KnightsKnaves(Puzzle):
    def __init__(self, solver: Solver, persons: list[str], statements: dict):
        super().__init__(solver)
        self.persons = persons
        self.statements = statements
        self.is_knight = {name: solver.create_bool_var(name) for name in persons}

    def _build_constraints(self):
        for name, statement_fn in self.statements.items():
            knight = self.is_knight[name]
            statement = statement_fn(self.is_knight, self.solver)
            # Knights tells truth and Knaves lies : is_knight <=> statement.
            self.solver.assert_equiv(knight, statement)

    def solve(self):
        self._build_constraints()
        if not self.solver.solve():
            return None
        return {
            name: "knight" if self.solver.get_value(var) else "knave"
            for name, var in self.is_knight.items()
        }
