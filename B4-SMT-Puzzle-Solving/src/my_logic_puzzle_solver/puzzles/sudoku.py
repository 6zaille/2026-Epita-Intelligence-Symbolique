from ..core import Puzzle, Solver

from time import perf_counter

class Sudoku(Puzzle):
    def __init__(self, grid: list[list[int]], solver: Solver):
        super().__init__(solver)
        self.grid = grid

class SudokuBinary(Sudoku):
    def __init__(self, grid: list[list[int]], solver: Solver):
        super().__init__(grid, solver)

        self.solution = None
        self.variables: list[list[list]] = []

        for x in range(9):
            self.variables.append([])

            for y in range(9):
                self.variables[x].append([])

                for n in range(9):
                    self.variables[x][y].append(
                        self.solver.create_bool_var(f"{x}_{y}_{n}")
                    )
                
        # For all cell assure only one digit is selected
        for x in range(9):
            for y in range(9):
                self.solver.constraint(
                    self.variables[x][y][0]
                    + self.variables[x][y][1]
                    + self.variables[x][y][2]
                    + self.variables[x][y][3]
                    + self.variables[x][y][4]
                    + self.variables[x][y][5]
                    + self.variables[x][y][6]
                    + self.variables[x][y][7]
                    + self.variables[x][y][8]
                    == 1
                )

        # For all columns assure uniqueness of all digits
        for x in range(9):
            for n in range(9):
                self.solver.constraint(
                    self.variables[x][0][n]
                    + self.variables[x][1][n]
                    + self.variables[x][2][n]
                    + self.variables[x][3][n]
                    + self.variables[x][4][n]
                    + self.variables[x][5][n]
                    + self.variables[x][6][n]
                    + self.variables[x][7][n]
                    + self.variables[x][8][n]
                    == 1
                )

        # For all rows assure uniqueness of all digits
        for y in range(9):
            for n in range(9):
                self.solver.constraint(
                    self.variables[0][y][n]
                    + self.variables[1][y][n]
                    + self.variables[2][y][n]
                    + self.variables[3][y][n]
                    + self.variables[4][y][n]
                    + self.variables[5][y][n]
                    + self.variables[6][y][n]
                    + self.variables[7][y][n]
                    + self.variables[8][y][n]
                    == 1
                )
        
        # For all 3x3 assure uniqueness of all digits
        for x in range(3):
            for y in range(3):
                for n in range(9):
                    self.solver.constraint(
                        self.variables[3 * x + 0][3 * y + 0][n]
                        + self.variables[3 * x + 1][3 * y + 0][n]
                        + self.variables[3 * x + 2][3 * y + 0][n]
                        + self.variables[3 * x + 0][3 * y + 1][n]
                        + self.variables[3 * x + 1][3 * y + 1][n]
                        + self.variables[3 * x + 2][3 * y + 1][n]
                        + self.variables[3 * x + 0][3 * y + 2][n]
                        + self.variables[3 * x + 1][3 * y + 2][n]
                        + self.variables[3 * x + 2][3 * y + 2][n]
                        == 1
                    )
        
        # For all known element assure it stays that way
        for x, row in enumerate(grid):
            for y, n in enumerate(row):
                if n != 0:
                    self.solver.constraint(
                        self.variables[x][y][n - 1] + 0 == 1
                    )

    def solve(self) -> list[list[int]] | None:
        if self.solution != None:
            return self.solution

        start = perf_counter()
        success = self.solver.solve()
        end = perf_counter()

        print(f"Solved in {end - start}s - Succeeded: {success}")
        
        if not success:
            return None

        res: list[list[int]] = []

        for x in range(9):
            res.append([])
            for y in range(9):
                res[x].append(0)
                for n in range(9):
                    if self.solver.get_value(self.variables[x][y][n]):
                        res[x][y] = n + 1
                        break
        
        self.solution = res
        return res
