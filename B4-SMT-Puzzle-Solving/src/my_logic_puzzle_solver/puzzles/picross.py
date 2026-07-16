from ..core import Puzzle, Solver


class Picross(Puzzle):
    """Constraint-based solver for Picross puzzles.

    Picross (also known as Nonogram) is a grid puzzle where each row and
    column contains clues describing consecutive groups of filled cells.
    This class models each cell as a Boolean variable and creates
    constraints ensuring that the grid satisfies all row and column clues.

    Parameters
    ----------
    solver : Solver
        Solver backend used to create variables, add constraints, and
        compute a solution.
    row_clues : list[list[int]]
        Clues describing the filled cell groups for each row. Each inner
        list contains the lengths of consecutive filled blocks in that row.
    col_clues : list[list[int]]
        Clues describing the filled cell groups for each column. Each inner
        list contains the lengths of consecutive filled blocks in that column.
    """

    def __init__(
        self,
        solver: Solver,
        row_clues: list[list[int]],
        col_clues: list[list[int]],
    ):
        """Initialize a Picross puzzle instance.

        Parameters
        ----------
        solver : Solver
            Solver backend used to construct and solve the constraint
            model.
        row_clues : list[list[int]]
            Row clue definitions. Each list describes the lengths of
            consecutive filled blocks in the corresponding row.
        col_clues : list[list[int]]
            Column clue definitions. Each list describes the lengths of
            consecutive filled blocks in the corresponding column.
        """
        super().__init__(solver)
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.n_rows = len(row_clues)
        self.n_cols = len(col_clues)
        self.grid = [
            [solver.create_bool_var(f"cell_{i}_{j}") for j in range(self.n_cols)]
            for i in range(self.n_rows)
        ]

    def _line_constraints(self, cells: list, clues: list[int], line_id: str) -> None:
        """Add constraints for a single row or column.

        Creates constraints ensuring that the given sequence of Boolean
        cells matches the provided Picross clues. Consecutive filled blocks
        are represented using integer start positions, with mandatory
        separation between adjacent blocks.

        Parameters
        ----------
        cells : list
            Boolean variables representing the cells in the line.
        clues : list[int]
            Filled block lengths required for the line.
        line_id : str
            Identifier used to generate unique variable names.

        Returns
        -------
        None
        """
        length = len(cells)
        if not clues:
            for cell in cells:
                self.solver.assert_true(self.solver.bool_not(cell))
            return

        starts = [
            self.solver.create_int_var(f"s_{line_id}_{i}", 0, length - clue)
            for i, clue in enumerate(clues)
        ]
        for i in range(len(starts) - 1):
            self.solver.constraint(starts[i + 1] >= starts[i] + clues[i] + 1)

        for j, cell in enumerate(cells):
            covered = []
            for i, (start, clue) in enumerate(zip(starts, clues)):
                ge = self.solver.reify(j >= start, j < start)
                lt = self.solver.reify(j < start + clue, j >= start + clue)
                covered.append(self.solver.bool_and(ge, lt))
            self.solver.assert_equiv(cell, self.solver.bool_or(*covered))

    def _build_constraints(self) -> None:
        """Build all row and column constraints.

        Adds constraints for every row and column according to the
        corresponding Picross clues.

        Returns
        -------
        None
        """
        for i, row in enumerate(self.grid):
            self._line_constraints(row, self.row_clues[i], f"row{i}")
        for j in range(self.n_cols):
            column = [self.grid[i][j] for i in range(self.n_rows)]
            self._line_constraints(column, self.col_clues[j], f"col{j}")

    def solve(self) -> list[list[bool]] | None:
        """Solve the Picross puzzle.

        Builds the constraint model, runs the configured solver, and
        converts the resulting Boolean assignments into a solved grid.

        Returns
        -------
        list[list[bool]] or None
            Solved puzzle grid where ``True`` represents a filled cell and
            ``False`` represents an empty cell. Returns ``None`` if the
            puzzle has no valid solution.
        """
        self._build_constraints()
        if not self.solver.solve():
            return None
        return [
            [bool(self.solver.get_value(cell)) for cell in row] for row in self.grid
        ]
