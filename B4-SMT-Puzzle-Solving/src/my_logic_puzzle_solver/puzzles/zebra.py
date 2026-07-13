from ..core import Puzzle, Solver

CATEGORIES = {
    "nationality": [
        "Englishman",
        "Spaniard",
        "Ukrainian",
        "Norwegian",
        "Japanese",
    ],
    "color": ["red", "green", "yellow", "ivory", "blue"],
    "drink": ["tea", "coffee", "milk", "orange juice", "<beverage>"],
    "smoke": [
        "Old Gold",
        "Kools",
        "ChesterFields",
        "Lucky Strike",
        "Parliaments",
    ],
    "pet": ["dog", "snail", "fox", "horse", "<animal>"],
}


class Zebra(Puzzle):
    def __init__(self, solver: Solver):
        super().__init__(solver)
        self.vars = {
            cat: {
                val: solver.create_int_var(f"{cat}_{val}", 1, 5)
                for val in values
            }
            for cat, values in CATEGORIES.items()
        }

    def _eq(self, cat, val, house):
        self.solver.constraint(self.vars[cat][val] == house)

    def _same(self, cat1, val1, cat2, val2):
        self.solver.constraint(self.vars[cat1][val1] == self.vars[cat2][val2])

    def _left_of(self, cat1, val1, cat2, val2):
        self.solver.constraint(
            self.vars[cat1][val1] == self.vars[cat2][val2] - 1
        )

    def _next_to(self, cat1, val1, cat2, val2):
        self.solver.abs_diff_eq(self.vars[cat1][val1], self.vars[cat2][val2], 1)

    def _build_constraints(self):
        for values in self.vars.values():
            self.solver.all_different(list(values.values()))

        self._same("nationality", "Englishman", "color", "red")
        self._same("nationality", "Spaniard", "pet", "dog")
        self._same("color", "green", "drink", "coffee")
        self._same("nationality", "Ukrainian", "drink", "tea")
        self._left_of("color", "green", "color", "ivory")
        self._same("smoke", "Old Gold", "pet", "snail")
        self._same("color", "yellow", "smoke", "Kools")
        self._eq("drink", "milk", 3)
        self._eq("nationality", "Norwegian", 1)
        self._next_to("smoke", "ChesterFields", "pet", "fox")
        self._next_to("pet", "horse", "smoke", "Kools")
        self._same("smoke", "Lucky Strike", "drink", "orange juice")
        self._same("nationality", "Japanese", "smoke", "Parliaments")
        self._next_to("nationality", "Norwegian", "color", "blue")
        # self._next_to("smoke", "blend", "drink", "water")

    def solve(self):
        self._build_constraints()
        if not self.solver.solve():
            return None
        return {
            house: {
                cat: next(
                    val
                    for val, var in values.items()
                    if self.solver.get_value(var) == house
                )
                for cat, values in self.vars.items()
            }
            for house in range(1, 6)
        }
