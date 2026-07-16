from ..core.solvers.cpsat import CPSATSolver


class Fill_A_Pix:
    def __init__(
        self,
        solver: CPSATSolver,
        grid: list[list[int | None]],
    ):
        self.solver = solver

        self.grid = grid
        self.n_rows = len(grid)
        self.n_cols = len(grid[0])

        self.var_grid = [
            [solver.create_bool_var(f"cell_{i}_{j}") for j in range(self.n_cols)]
            for i in range(self.n_rows)
        ]

    def _add_constraint(self, x, y):
        neighbors = []
        for dx in range(x - 1, x + 2):
            if dx < 0 or dx >= self.n_rows:
                continue
            for dy in range(y - 1, y + 2):
                if dy < 0 or dy >= self.n_cols:
                    continue
                neighbors.append(self.var_grid[dx][dy])
        self.solver.model.add(sum(neighbors) == self.grid[x][y])

    def _build_constraints(self):
        for i in range(self.n_rows):
            for j in range(self.n_cols):
                if self.grid[i][j] != None:
                    self._add_constraint(i, j)

    def solve(self):
        self._build_constraints()
        if not self.solver.solve():
            return None
        return [
            [bool(self.solver.get_value(cell)) for cell in row] for row in self.var_grid
        ]
