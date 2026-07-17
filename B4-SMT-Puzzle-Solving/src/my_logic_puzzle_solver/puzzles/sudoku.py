from ..core import Puzzle, Solver


class Sudoku(Puzzle):
    """Base class for Sudoku puzzle implementations.

    This class provides common functionality shared by different Sudoku
    encodings, including storing the puzzle grid, extracting given values,
    and generating Sudoku constraint groups.

    Parameters
    ----------
    solver : Solver
        Solver backend used to create variables, add constraints, and
        compute a solution.
    grid : list[list[int]]
        Sudoku puzzle grid. Values from 1 to 9 represent fixed cells,
        while ``0`` represents an empty cell.
    """

    def __init__(self, solver: Solver, grid: list[list[int]]):
        """Initialize a Sudoku puzzle.

        Parameters
        ----------
        solver : Solver
            Solver backend used to construct and solve the constraint
            model.
        grid : list[list[int]]
            Initial Sudoku grid. Non-zero values are treated as fixed
            clues.
        """
        super().__init__(solver)
        self.grid = grid

    def _givens(self):
        """Return the fixed values from the input grid.

        Yields
        ------
        tuple[int, int, int]
            Tuple containing the row index, column index, and value of
            each fixed cell.
        """
        for x, row in enumerate(self.grid):
            for y, n in enumerate(row):
                if n != 0:
                    yield x, y, n

    def _groups(self) -> list[list[tuple[int, int]]]:
        """Return all Sudoku constraint groups.

        Generates the 27 groups that define Sudoku constraints:
        9 rows, 9 columns, and 9 3x3 boxes.

        Returns
        -------
        list[list[tuple[int, int]]]
            List of coordinate groups. Each group contains the cell
            coordinates that must contain distinct values.
        """
        rows = [[(x, y) for y in range(9)] for x in range(9)]
        cols = [[(x, y) for x in range(9)] for y in range(9)]
        boxes = [
            [(3 * bx + dx, 3 * by + dy) for dx in range(3) for dy in range(3)]
            for bx in range(3)
            for by in range(3)
        ]
        return rows + cols + boxes


class SudokuBoolean(Sudoku):
    """Boolean encoding of a Sudoku puzzle.

    Each possible value assignment is represented by a Boolean variable.
    The variable ``vars[x][y][n]`` indicates whether cell ``(x, y)``
    contains the value ``n + 1``.

    This encoding creates constraints ensuring that each cell contains
    exactly one value and that each Sudoku group contains each value
    exactly once.
    """

    def __init__(self, solver: Solver, grid: list[list[int]]):
        """Initialize a Boolean Sudoku model.

        Parameters
        ----------
        solver : Solver
            Solver backend used to construct and solve the model.
        grid : list[list[int]]
            Initial Sudoku grid containing fixed clues and empty cells.
        """
        super().__init__(solver, grid)
        self.vars = [
            [
                [solver.create_bool_var(f"{x}_{y}_{n}") for n in range(9)]
                for y in range(9)
            ]
            for x in range(9)
        ]

    def _build_constraints(self) -> None:
        """Build the Boolean Sudoku constraints.

        Adds constraints enforcing:

        - exactly one value per cell,
        - exactly one occurrence of each value in every row,
        - exactly one occurrence of each value in every column,
        - exactly one occurrence of each value in every box,
        - all predefined puzzle clues.

        Returns
        -------
        None
        """
        for x in range(9):
            for y in range(9):
                self.solver.exactly_one(self.vars[x][y])

        for group in self._groups():
            for n in range(9):
                self.solver.exactly_one([self.vars[x][y][n] for x, y in group])

        for x, y, n in self._givens():
            self.solver.assert_true(self.vars[x][y][n - 1])

    def solve(self) -> list[list[int]] | None:
        """Solve the Sudoku puzzle.

        Returns
        -------
        list[list[int]] or None
            Solved Sudoku grid containing values from 1 to 9.
            Returns ``None`` if no valid solution exists.
        """
        self._build_constraints()
        if not self.solver.solve():
            return None
        return [
            [
                next(
                    n + 1 for n in range(9) if self.solver.get_value(self.vars[x][y][n])
                )
                for y in range(9)
            ]
            for x in range(9)
        ]


class _SudokuIntegerBase(Sudoku):
    """Base class for integer-encoded Sudoku implementations.

    Each cell is represented directly as an integer variable in the range
    1 to 9. Subclasses provide the implementation of the all-different
    constraint.

    Parameters
    ----------
    solver : Solver
        Solver backend used to create and solve the model.
    grid : list[list[int]]
        Initial Sudoku grid containing clues and empty cells.
    """

    def __init__(self, solver: Solver, grid: list[list[int]]):
        """Initialize an integer Sudoku model.

        Parameters
        ----------
        solver : Solver
            Solver backend used to construct and solve the model.
        grid : list[list[int]]
            Initial Sudoku grid.
        """
        super().__init__(solver, grid)
        self.vars = [
            [solver.create_int_var(f"{x}_{y}", 1, 9) for y in range(9)]
            for x in range(9)
        ]

    def _all_diff(self, group: list) -> None:
        """Add an all-different constraint to a Sudoku group.

        Parameters
        ----------
        group : list
            List of integer variables that must contain distinct values.

        Raises
        ------
        NotImplementedError
            Always raised. Subclasses must provide the implementation.
        """
        raise NotImplementedError

    def _build_constraints(self) -> None:
        """Build the integer Sudoku constraints.

        Adds all-different constraints for rows, columns, and boxes,
        then applies all predefined puzzle clues.

        Returns
        -------
        None
        """
        for group in self._groups():
            self._all_diff([self.vars[x][y] for x, y in group])
        for x, y, n in self._givens():
            self.solver.constraint(self.vars[x][y] == n)

    def solve(self) -> list[list[int]] | None:
        """Solve the Sudoku puzzle.

        Returns
        -------
        list[list[int]] or None
            Solved Sudoku grid containing values from 1 to 9.
            Returns ``None`` if no valid solution exists.
        """
        self._build_constraints()
        if not self.solver.solve():
            return None
        return [
            [self.solver.get_value(self.vars[x][y]) for y in range(9)] for x in range(9)
        ]


class SudokuInteger(_SudokuIntegerBase):
    """Integer Sudoku implementation using pairwise inequality constraints.

    This implementation expands each all-different constraint into a set
    of pairwise inequality constraints between all variables in a group.
    """

    def _all_diff(self, group: list) -> None:
        """Add pairwise inequality constraints.

        Parameters
        ----------
        group : list
            Integer variables that must contain distinct values.

        Returns
        -------
        None
        """
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                self.solver.constraint(group[i] != group[j])


class SudokuMixed(_SudokuIntegerBase):
    """Integer Sudoku implementation using native all-different constraints.

    This implementation delegates all-different constraints directly to
    the solver backend when supported.
    """

    def _all_diff(self, group: list) -> None:
        """Add a native all-different constraint.

        Parameters
        ----------
        group : list
            Integer variables that must contain distinct values.

        Returns
        -------
        None
        """
        self.solver.all_different(group)
