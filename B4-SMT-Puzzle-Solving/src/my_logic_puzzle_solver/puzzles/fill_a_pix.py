from ..core import Puzzle, Solver


class FillAPix(Puzzle):
    """Constraint-based solver for Fill-a-Pix puzzles.

    Fill-a-Pix is a grid puzzle where each clue indicates the number of
    filled cells in its surrounding 3x3 neighborhood, including the cell
    itself. This class models each cell as a Boolean decision variable and
    uses a constraint solver to find a valid grid configuration.

    Parameters
    ----------
    solver : Solver
        Solver backend used to create variables, add constraints, and
        compute a solution.
    grid : list[list[int | None]]
        Puzzle grid containing clue values. Cells with integer values
        define constraints, while ``None`` represents cells without clues.
    """

    def __init__(
        self,
        solver: Solver,
        grid: list[list[int | None]],
    ):
        """Initialize a Fill-a-Pix puzzle instance.

        Parameters
        ----------
        solver : Solver
            Solver backend used to construct and solve the constraint
            model.
        grid : list[list[int | None]]
            Input puzzle grid. Integer values represent clues and
            ``None`` values represent cells without clues.
        """
        super().__init__(solver)

        self.grid = grid
        self.n_rows = len(grid)
        self.n_cols = len(grid[0])

        self.var_grid = [
            [solver.create_bool_var(f"cell_{i}_{j}") for j in range(self.n_cols)]
            for i in range(self.n_rows)
        ]

    def _add_constraint(self, x, y) -> None:
        """Add the constraint associated with a clue cell.

        The constraint enforces that the number of filled cells in the
        3x3 neighborhood centered at ``(x, y)`` matches the clue value
        stored in the puzzle grid.

        Parameters
        ----------
        x : int
            Row index of the clue cell.
        y : int
            Column index of the clue cell.

        Returns
        -------
        None
        """
        neighbors = []
        for dx in range(x - 1, x + 2):
            if dx < 0 or dx >= self.n_rows:
                continue
            for dy in range(y - 1, y + 2):
                if dy < 0 or dy >= self.n_cols:
                    continue
                neighbors.append(self.var_grid[dx][dy])
        self.solver.constraint(sum(neighbors) == self.grid[x][y])

    def _build_constraints(self) -> None:
        """Build all constraints required to solve the puzzle.

        Creates one neighborhood constraint for every clue cell in the
        input grid. Cells containing ``None`` values are ignored.

        Returns
        -------
        None
        """
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.grid[i][j] != None:
                    self._add_constraint(i, j)

    def solve(self) -> list[list[bool]] | None:
        """Solve the Fill-a-Pix puzzle.

        Builds the constraint model, runs the configured solver, and
        converts the resulting variable assignments into a Boolean grid.

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
            [bool(self.solver.get_value(cell)) for cell in row] for row in self.var_grid
        ]
