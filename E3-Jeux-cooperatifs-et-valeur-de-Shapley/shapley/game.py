"""Jeu cooperatif a utilite transferable (TU-game).

Un jeu cooperatif est une paire ``(N, v)`` ou ``N = {0, 1, ..., n-1}`` est
l'ensemble des joueurs et ``v : 2^N -> R`` la *fonction caracteristique*
(ou fonction de valeur) qui associe a chaque coalition ``S`` le gain
``v(S)`` que ses membres peuvent garantir en cooperant, avec ``v(emptyset) = 0``.

Les coalitions sont manipulees dans l'API publique comme des ensembles
d'entiers (``frozenset``/``set``/``tuple``), mais stockees en interne sous
forme de *masques de bits* (un entier dont le bit ``i`` vaut 1 ssi le joueur
``i`` est dans la coalition). Cela rend le cache de valeurs et les algorithmes
sur les ``2^n`` coalitions rapides et compacts.
"""

from __future__ import annotations

from itertools import combinations
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Union

Coalition = Iterable[int]


def coalition_to_mask(coalition: Coalition) -> int:
    """Convertit une coalition (iterable de joueurs) en masque de bits."""
    mask = 0
    for i in coalition:
        mask |= 1 << i
    return mask


def mask_to_coalition(mask: int) -> frozenset:
    """Convertit un masque de bits en ``frozenset`` de joueurs."""
    players = []
    i = 0
    while mask:
        if mask & 1:
            players.append(i)
        mask >>= 1
        i += 1
    return frozenset(players)


def mask_size(mask: int) -> int:
    """Nombre de joueurs dans une coalition donnee par son masque."""
    return bin(mask).count("1")


class CooperativeGame:
    """Jeu cooperatif TU defini par sa fonction caracteristique.

    Parameters
    ----------
    n:
        Nombre de joueurs.
    v:
        La fonction caracteristique, fournie sous l'une des formes :

        * ``Callable`` prenant un ``frozenset`` de joueurs et renvoyant un float ;
        * ``dict`` associant un ``frozenset`` (ou ``tuple`` trie) a sa valeur ;
        * ``Sequence`` de longueur ``2**n`` indexee par masque de bits.

        Dans tous les cas ``v(emptyset)`` est ramene a ``0`` par convention.
    names:
        Etiquettes lisibles des joueurs (par defaut ``P0, P1, ...``).
    is_cost:
        Si ``True``, ``v`` represente un *cout* a partager (jeu de couts) et non
        un gain. Le calcul de la valeur de Shapley est identique ; seul le sens
        change (part de cout imputee a chaque joueur).
    """

    def __init__(
        self,
        n: int,
        v: Union[Callable[[frozenset], float], Dict, Sequence[float]],
        names: Optional[Sequence[str]] = None,
        is_cost: bool = False,
    ) -> None:
        if n < 0:
            raise ValueError("le nombre de joueurs doit etre positif")
        self.n = n
        self.is_cost = is_cost
        self.names: List[str] = (
            list(names) if names is not None else [f"P{i}" for i in range(n)]
        )
        if len(self.names) != n:
            raise ValueError("names doit contenir exactement n etiquettes")

        self._cache: Dict[int, float] = {0: 0.0}  # v(emptyset) = 0

        if callable(v):
            self._raw: Optional[Callable[[frozenset], float]] = v
        elif isinstance(v, dict):
            self._raw = None
            for key, val in v.items():
                self._cache[coalition_to_mask(key)] = float(val)
            self._cache[0] = 0.0
        else:  # sequence indexee par masque
            seq = list(v)
            if len(seq) != (1 << n):
                raise ValueError(
                    f"la sequence doit avoir 2**n = {1 << n} valeurs, "
                    f"pas {len(seq)}"
                )
            self._raw = None
            for mask, val in enumerate(seq):
                self._cache[mask] = float(val)
            self._cache[0] = 0.0

    # ------------------------------------------------------------------
    # Acces aux valeurs de coalition
    # ------------------------------------------------------------------
    def value_mask(self, mask: int) -> float:
        """Valeur ``v(S)`` de la coalition donnee par son masque de bits."""
        cached = self._cache.get(mask)
        if cached is not None:
            return cached
        if self._raw is None:
            raise KeyError(
                f"valeur non definie pour la coalition {mask_to_coalition(mask)}"
            )
        val = float(self._raw(mask_to_coalition(mask)))
        self._cache[mask] = val
        return val

    def value(self, coalition: Coalition) -> float:
        """Valeur ``v(S)`` de la coalition (iterable de joueurs)."""
        return self.value_mask(coalition_to_mask(coalition))

    def grand_coalition_value(self) -> float:
        """Valeur ``v(N)`` de la grande coalition (tous les joueurs)."""
        return self.value_mask((1 << self.n) - 1)

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------
    def all_coalitions(self) -> Iterable[frozenset]:
        """Enumere les ``2^n`` coalitions (y compris vide et grande)."""
        players = range(self.n)
        for size in range(self.n + 1):
            for combo in combinations(players, size):
                yield frozenset(combo)

    def is_monotone(self) -> bool:
        """Teste la monotonie : ``S subset T => v(S) <= v(T)``."""
        full = 1 << self.n
        for mask in range(full):
            base = self.value_mask(mask)
            missing = ((full - 1) ^ mask)
            sub = missing
            while sub:  # sur-ensembles immediats (ajout d'un joueur)
                bit = sub & (-sub)
                if self.value_mask(mask | bit) < base - 1e-12:
                    return False
                sub ^= bit
        return True

    def label(self, values: Sequence[float]) -> Dict[str, float]:
        """Associe un vecteur de valeurs (indexe par joueur) aux etiquettes."""
        return {self.names[i]: values[i] for i in range(self.n)}

    def __repr__(self) -> str:
        kind = "cout" if self.is_cost else "gain"
        return f"CooperativeGame(n={self.n}, {kind}, joueurs={self.names})"
