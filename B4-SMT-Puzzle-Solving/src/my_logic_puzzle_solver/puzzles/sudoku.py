from ..core import Puzzle, Solver


class Sudoku(Puzzle):
    def __init__(self, solver: Solver, grid: list[list[int]]):
        super().__init__(solver)
        self.grid = grid

    def _givens(self):
        for x, row in enumerate(self.grid):
            for y, n in enumerate(row):
                if n != 0:
                    yield x, y, n

    def _groups(self) -> list[list[tuple[int, int]]]:
        rows = [[(x, y) for y in range(9)] for x in range(9)]
        cols = [[(x, y) for x in range(9)] for y in range(9)]
        boxes = [
            [(3 * bx + dx, 3 * by + dy) for dx in range(3) for dy in range(3)]
            for bx in range(3)
            for by in range(3)
        ]
        return rows + cols + boxes


class SudokuBoolean(Sudoku):
    def __init__(self, solver: Solver, grid: list[list[int]]):
        super().__init__(solver, grid)
        self.vars = [
            [
                [solver.create_bool_var(f"{x}_{y}_{n}") for n in range(9)]
                for y in range(9)
            ]
            for x in range(9)
        ]

    def _build_constraints(self):
        for x in range(9):
            for y in range(9):
                self.solver.exactly_one(self.vars[x][y])

        for group in self._groups():
            for n in range(9):
                self.solver.exactly_one([self.vars[x][y][n] for x, y in group])

        for x, y, n in self._givens():
            self.solver.assert_true(self.vars[x][y][n - 1])

    def solve(self):
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
    def __init__(self, solver: Solver, grid: list[list[int]]):
        super().__init__(solver, grid)
        self.vars = [
            [solver.create_int_var(f"{x}_{y}", 1, 9) for y in range(9)]
            for x in range(9)
        ]

    def _all_diff(self, group: list) -> None:
        raise NotImplementedError

    def _build_constraints(self):
        for group in self._groups():
            self._all_diff([self.vars[x][y] for x, y in group])
        for x, y, n in self._givens():
            self.solver.constraint(self.vars[x][y] == n)

    def solve(self):
        self._build_constraints()
        if not self.solver.solve():
            return None
        return [
            [self.solver.get_value(self.vars[x][y]) for y in range(9)] for x in range(9)
        ]


class SudokuInteger(_SudokuIntegerBase):
    def _all_diff(self, group: list) -> None:
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                self.solver.constraint(group[i] != group[j])


class SudokuMixed(_SudokuIntegerBase):
    def _all_diff(self, group: list) -> None:
        self.solver.all_different(group)
