from ..core import Puzzle, Solver


class KnightsKnaves(Puzzle):
    """Constraint-based solver for Knights and Knaves logic puzzles.

    In Knights and Knaves puzzles, each person is either a knight who always
    tells the truth or a knave who always lies. This class models each person
    as a Boolean variable and creates equivalence constraints between each
    person's type and the truth value of their statement.

    Parameters
    ----------
    solver : Solver
        Solver backend used to create variables, add constraints, and find
        a solution.
    persons : list[str]
        Names of the people participating in the puzzle.
    statements : dict
        Mapping from person names to functions generating their statements.
        Each function receives the mapping of person variables and the solver,
        and returns a Boolean expression representing the truth value of the
        person's statement.
    """

    def __init__(self, solver: Solver, persons: list[str], statements: dict):
        """Initialize a Knights and Knaves puzzle instance.

        Parameters
        ----------
        solver : Solver
            Solver backend used to construct and solve the constraint model.
        persons : list[str]
            Names of all people in the puzzle.
        statements : dict
            Mapping between person names and statement-building functions.
            Each statement function must return a Boolean expression.
        """
        super().__init__(solver)
        self.persons = persons
        self.statements = statements
        self.is_knight = {name: solver.create_bool_var(name) for name in persons}

    def _build_constraints(self) -> None:
        """Build all logical constraints for the puzzle.

        For each person, creates an equivalence constraint between their
        knight status and the truth value of their statement:

        - Knights have true statements.
        - Knaves have false statements.

        Returns
        -------
        None
        """
        for name, statement_fn in self.statements.items():
            knight = self.is_knight[name]
            statement = statement_fn(self.is_knight, self.solver)
            # Knights tells truth and Knaves lies : is_knight <=> statement.
            self.solver.assert_equiv(knight, statement)

    def solve(self) -> dict[str, str] | None:
        """Solve the Knights and Knaves puzzle.

        Builds the logical constraints, invokes the configured solver,
        and converts the resulting assignments into person classifications.

        Returns
        -------
        dict[str, str] or None
            Mapping from person names to their roles. Each value is either
            ``"knight"`` or ``"knave"``. Returns ``None`` if no valid
            solution exists.
        """
        self._build_constraints()
        if not self.solver.solve():
            return None
        return {
            name: "knight" if self.solver.get_value(var) else "knave"
            for name, var in self.is_knight.items()
        }
