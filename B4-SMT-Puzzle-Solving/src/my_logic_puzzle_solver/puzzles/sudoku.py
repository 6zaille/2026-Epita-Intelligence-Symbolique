from ..core import Puzzle, Solver


class Sudoku(Puzzle):
    def __init__(self, grid: list[list[int]], solver: Solver):
        super().__init__(solver)
        self.grid = grid  # Hit the griddy

    def solve(self) -> list[list[int]] | None:
        return [[]]
