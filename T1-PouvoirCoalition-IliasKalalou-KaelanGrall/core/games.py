from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import Iterator


@dataclass(frozen=True)
class WeightedVotingGame:
    """
    Jeu de vote pondere [q ; w_1, ..., w_n] : une coalition gagne si la somme
    de ses poids atteint le quota q. Noms par defaut P0, P1, ...
    """

    weights: tuple[int, ...]
    quota: int
    names: tuple[str, ...] = field(default=())

    def __post_init__(self) -> None:
        if self.quota <= 0:
            raise ValueError(f"Le quota doit etre strictement positif (recu {self.quota}).")
        if any(w < 0 for w in self.weights):
            raise ValueError("Les poids doivent etre positifs ou nuls.")
        if not self.weights:
            raise ValueError("Le jeu doit comporter au moins un joueur.")
        if self.quota > self.total_weight:
            raise ValueError(
                f"Quota {self.quota} superieur au poids total {self.total_weight} : "
                "aucune coalition ne peut gagner."
            )
        if not self.names:
            object.__setattr__(
                self, "names", tuple(f"P{i}" for i in range(len(self.weights)))
            )
        elif len(self.names) != len(self.weights):
            raise ValueError("Le nombre de noms doit egaler le nombre de poids.")

    @property
    def n_players(self) -> int:
        return len(self.weights)

    @property
    def players(self) -> tuple[int, ...]:
        return tuple(range(self.n_players))

    @property
    def total_weight(self) -> int:
        return sum(self.weights)

    def coalition_weight(self, coalition: frozenset[int]) -> int:
        return sum(self.weights[i] for i in coalition)

    def is_winning(self, coalition: frozenset[int]) -> bool:
        return self.coalition_weight(coalition) >= self.quota

    def value(self, coalition: frozenset[int]) -> int:
        return 1 if self.is_winning(coalition) else 0

    def all_coalitions(self) -> Iterator[frozenset[int]]:
        for size in range(self.n_players + 1):
            for combo in combinations(self.players, size):
                yield frozenset(combo)

    def winning_coalitions(self) -> list[frozenset[int]]:
        return [c for c in self.all_coalitions() if self.is_winning(c)]

    def is_critical(self, player: int, coalition: frozenset[int]) -> bool:
        """Vrai si la coalition gagne mais perd sans le joueur (swing)."""
        if player not in coalition or not self.is_winning(coalition):
            return False
        return not self.is_winning(coalition - {player})

    def is_minimal_winning(self, coalition: frozenset[int]) -> bool:
        """Vrai si la coalition gagne et que chacun de ses membres est critique."""
        if not self.is_winning(coalition):
            return False
        return all(not self.is_winning(coalition - {i}) for i in coalition)

    def minimal_winning_coalitions(self) -> list[frozenset[int]]:
        return [c for c in self.all_coalitions() if self.is_minimal_winning(c)]

    def is_veto(self, player: int) -> bool:
        """Vrai si aucune coalition ne gagne sans le joueur."""
        others = frozenset(p for p in self.players if p != player)
        return not self.is_winning(others)

    def is_dummy(self, player: int) -> bool:
        """Vrai si le joueur n'est jamais critique."""
        others = [p for p in self.players if p != player]
        for size in range(len(others) + 1):
            for combo in combinations(others, size):
                base = frozenset(combo)
                if self.is_winning(base | {player}) and not self.is_winning(base):
                    return False
        return True

    def is_dictator(self, player: int) -> bool:
        """Vrai si le joueur gagne seul et qu'aucune coalition ne gagne sans lui."""
        return self.is_winning(frozenset({player})) and self.is_veto(player)

    def is_proper(self) -> bool:
        """Vrai si deux coalitions disjointes ne peuvent pas gagner toutes les deux."""
        return 2 * self.quota > self.total_weight

    def __repr__(self) -> str:
        body = "; ".join(str(w) for w in self.weights)
        return f"WeightedVotingGame([{self.quota} | {body}])"


def majority_game(weights: tuple[int, ...], names: tuple[str, ...] = ()) -> WeightedVotingGame:
    """Jeu a la majorite absolue : quota = poids total // 2 + 1."""
    return WeightedVotingGame(weights=weights, quota=sum(weights) // 2 + 1, names=names)
