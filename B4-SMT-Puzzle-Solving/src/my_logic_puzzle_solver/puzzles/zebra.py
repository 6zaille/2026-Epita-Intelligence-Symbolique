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
    """Constraint-based solver for the Zebra puzzle.

    The Zebra puzzle is a logic puzzle where five people live in five
    houses, and each house has a unique nationality, color, drink, smoke,
    and pet assignment. This class models each category value as an
    integer variable representing the house position and solves the
    resulting constraint problem.

    Parameters
    ----------
    solver : Solver
        Solver backend used to create variables, add constraints, and
        compute a solution.

    Notes
    -----
    Each variable represents the house index associated with a value.
    Houses are numbered from 1 to 5. For example, the variable
    ``vars["nationality"]["Englishman"]`` contains the house number where
    the Englishman lives.
    """

    def __init__(self, solver: Solver):
        """Initialize a Zebra puzzle instance.

        Parameters
        ----------
        solver : Solver
            Solver backend used to construct and solve the constraint
            model.
        """
        super().__init__(solver)
        self.vars = {
            cat: {val: solver.create_int_var(f"{cat}_{val}", 1, 5) for val in values}
            for cat, values in CATEGORIES.items()
        }

    def _eq(self, cat, val, house) -> None:
        """Constrain a value to a specific house.

        Parameters
        ----------
        cat : str
            Category name.
        val : str
            Value within the category.
        house : int
            House number to assign the value to.

        Returns
        -------
        None
        """
        self.solver.constraint(self.vars[cat][val] == house)

    def _same(self, cat1, val1, cat2, val2) -> None:
        """Constrain two values to belong to the same house.

        Parameters
        ----------
        cat1 : str
            First category name.
        val1 : str
            First category value.
        cat2 : str
            Second category name.
        val2 : str
            Second category value.

        Returns
        -------
        None
        """
        self.solver.constraint(self.vars[cat1][val1] == self.vars[cat2][val2])

    def _left_of(self, cat1, val1, cat2, val2) -> None:
        """Constrain one value to be immediately left of another.

        Parameters
        ----------
        cat1 : str
            Category name of the left value.
        val1 : str
            Value that must be on the left.
        cat2 : str
            Category name of the right value.
        val2 : str
            Value that must be on the right.

        Returns
        -------
        None
        """
        self.solver.constraint(self.vars[cat1][val1] == self.vars[cat2][val2] - 1)

    def _next_to(self, cat1, val1, cat2, val2) -> None:
        """Constrain two values to adjacent houses.

        Parameters
        ----------
        cat1 : str
            First category name.
        val1 : str
            First category value.
        cat2 : str
            Second category name.
        val2 : str
            Second category value.

        Returns
        -------
        None
        """
        self.solver.abs_diff_eq(self.vars[cat1][val1], self.vars[cat2][val2], 1)

    def _build_constraints(self) -> None:
        """Build all constraints defining the Zebra puzzle.

        Adds uniqueness constraints for every category and applies all
        logical clues from the classic Zebra puzzle.

        Returns
        -------
        None
        """
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

    def solve(self) -> dict[int, dict[str, str]] | None:
        """Solve the Zebra puzzle.

        Builds the constraint model, invokes the solver, and converts the
        resulting variable assignments into a house-based representation.

        Returns
        -------
        dict[int, dict[str, str]] or None
            Mapping from house numbers to their assigned attributes.
            Each house contains one value from every category. Returns
            ``None`` if no valid solution exists.
        """
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
