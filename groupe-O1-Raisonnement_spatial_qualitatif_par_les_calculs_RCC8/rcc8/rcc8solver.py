from collections import deque
from rcc8.composition_table import COMPOSE
from rcc8.relations import inverse_relation


class RCC8Solver:

    def __init__(self, vars, R, inverse_relation):
        self.vars = vars
        self.R = R
        self.COMPOSE = COMPOSE
        self.inverse_relation = inverse_relation

    # -----------------------------
    # REVISE (PC-2 core)
    # -----------------------------
    def revise(self, i, j, k):
        """
        R(i,k) ← R(i,k) ∩ (R(i,j) ∘ R(j,k))
        """

        old = self.R[(i, k)]
        possible = set()

        for rij in self.R[(i, j)]:
            comp_table = self.COMPOSE.get(rij)
            if comp_table is None:
                continue

            for rjk in self.R[(j, k)]:
                possible |= comp_table.get(rjk, set())

        new = old & possible

        # incohérence globale
        if not new:
            raise ValueError(f"Inconsistency detected between {i} and {k}")

        if new != old:
            self.R[(i, k)] = new

            # maintenir cohérence inverse
            inv = {self.inverse_relation(r) for r in new}
            self.R[(k, i)] = self.R[(k, i)] & inv

            return True

        return False

    # -----------------------------
    # PC-2 (path consistency global)
    # -----------------------------
    def pc2(self):
        """
        PC-2 classique :
        boucle jusqu'à point fixe sur tous les triplets
        """

        changed = True

        while changed:
            changed = False

            for i in self.vars:
                for j in self.vars:
                    if i == j:
                        continue

                    for k in self.vars:
                        if k in (i, j):
                            continue

                        # propagation i -> k via j
                        if self.revise(i, j, k):
                            changed = True

        return self.R