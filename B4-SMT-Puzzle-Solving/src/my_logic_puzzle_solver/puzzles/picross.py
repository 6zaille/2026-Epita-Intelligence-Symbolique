from ..core import Puzzle, Solver


class Picross(Puzzle):
    def __init__(
        self,
        solver: Solver,
        row_clues: list[list[int]],
        col_clues: list[list[int]],
    ):
        super().__init__(solver)
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.n_rows = len(row_clues)
        self.n_cols = len(col_clues)
        self.grid = [
            [
                solver.create_bool_var(f"cell_{i}_{j}")
                for j in range(self.n_cols)
            ]
            for i in range(self.n_rows)
        ]

    def _line_constraints(self, cells: list, clues: list[int], line_id: str):
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

    def _build_constraints(self):
        for i, row in enumerate(self.grid):
            self._line_constraints(row, self.row_clues[i], f"row{i}")
        for j in range(self.n_cols):
            column = [self.grid[i][j] for i in range(self.n_rows)]
            self._line_constraints(column, self.col_clues[j], f"col{j}")

    def solve(self):
        self._build_constraints()
        if not self.solver.solve():
            return None
        return [
            [bool(self.solver.get_value(cell)) for cell in row]
            for row in self.grid
        ]
