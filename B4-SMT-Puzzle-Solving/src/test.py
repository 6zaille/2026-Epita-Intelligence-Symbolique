from my_logic_puzzle_solver.puzzles.sudoku import SudokuBinary
from my_logic_puzzle_solver.core.solvers.cpsat import CPSATSolver
from my_logic_puzzle_solver.core.solvers.z3 import Z3Solver

test = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,7,0,5],
    [0,0,0,0,8,0,0,7,9],
]

def show_grid(grid: list[list[int]]):
    if grid == None:
        return
    print(" -------+-------+-------")
    for x in range(3):
        for dx in range(3):
            print("|", end = " ")
            for y in range(3):
                for dy in range(3):
                    print(grid[3 * x + dx][3 * y + dy], end = " ")
                print("|", end = " ")
            print()
        print(" -------+-------+-------")
    print()

s = SudokuBinary(test, CPSATSolver())
s2 = SudokuBinary(test, Z3Solver())
show_grid(s.solve())
print()
show_grid(s2.solve())