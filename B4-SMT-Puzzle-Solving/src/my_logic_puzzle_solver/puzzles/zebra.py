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
    "drink": ["tea", "coffee", "milk", "orange juice", "water"],
    "smoke": [
        "Old Gold",
        "Kools",
        "ChesterFields",
        "Lucky Strike",
        "Parliaments",
    ],
    "pet": ["dog", "snail", "fox", "horse", "zebra"],
}


class Zebra(Puzzle):
    def __init__(self, solver: Solver):
        super().__init__(solver)
        self.vars = {
            cat: {val: solver.create_int_var(f"{cat}_{val}", 1, 5) for val in values}
            for cat, values in CATEGORIES.items()
        }

    def _eq(self, cat, val, house):
        self.solver.constraint(self.vars[cat][val] == house)

    def _same(self, cat1, val1, cat2, val2):
        self.solver.constraint(self.vars[cat1][val1] == self.vars[cat2][val2])

    def _left_of(self, cat1, val1, cat2, val2):
        self.solver.constraint(self.vars[cat1][val1] == self.vars[cat2][val2] - 1)

    def _next_to(self, cat1, val1, cat2, val2):
        self.solver.abs_diff_eq(self.vars[cat1][val1], self.vars[cat2][val2], 1)

    def _build_constraints(self):
        for values in self.vars.values():
            self.solver.all_different(list(values.values()))

        # According to https://en.wikipedia.org/wiki/Zebra_Puzzle#Description:

        # The Englishman lives in the red house.
        self._same("nationality", "Englishman", "color", "red")
        # The Spaniard owns the dog.
        self._same("nationality", "Spaniard", "pet", "dog")
        # Coffee is drunk in the green house.
        self._same("color", "green", "drink", "coffee")
        # The Ukrainian drinks tea.
        self._same("nationality", "Ukrainian", "drink", "tea")
        # The green house is immediately to the right of the ivory house.
        self._left_of("color", "ivory", "color", "green")
        # The Old Gold smoker owns snails.
        self._same("smoke", "Old Gold", "pet", "snail")
        # Kools are smoked in the yellow house.
        self._same("color", "yellow", "smoke", "Kools")
        # Milk is drunk in the middle house.
        self._eq("drink", "milk", 3)
        # The Norwegian lives in the first house.
        self._eq("nationality", "Norwegian", 1)
        # The man who smokes Chesterfields lives in the house next to the man with the fox.
        self._next_to("smoke", "ChesterFields", "pet", "fox")
        # Kools are smoked in the house next to the house where the horse is kept.
        self._next_to("pet", "horse", "smoke", "Kools")
        # The Lucky Strike smoker drinks orange juice.
        self._same("smoke", "Lucky Strike", "drink", "orange juice")
        # The Japanese smokes Parliaments.
        self._same("nationality", "Japanese", "smoke", "Parliaments")
        # The Norwegian lives next to the blue house.
        self._next_to("nationality", "Norwegian", "color", "blue")

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
