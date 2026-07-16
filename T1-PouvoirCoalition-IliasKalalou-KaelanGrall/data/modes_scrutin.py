from __future__ import annotations

from typing import Callable

from core.games import WeightedVotingGame, majority_game
from data.europeennes_dhondt import EUROPEENNES_2024, SEATS_2024, dhondt_allocation
from indices.shapley_shubik import shapley_shubik_exact

# Objectif 5 : evaluer l'impact d'un changement de mode de scrutin sur les indices
# de pouvoir. On garde les MEMES suffrages (europeennes 2024) et on fait varier la
# seule regle d'attribution des sieges. C'est le contrefactuel controle : tout ce
# qui change entre deux lignes est la regle, pas l'electorat.

Divisor = Callable[[int], float]


def highest_averages_allocation(
    votes: dict[str, int],
    seats: int,
    divisor: Divisor,
    threshold: float = 0.0,
) -> dict[str, int]:
    """
    Methode de la plus forte moyenne generique. Le quotient d'une liste ayant deja
    s sieges est voix / divisor(s). D'Hondt correspond a divisor(s) = s + 1,
    Sainte-Lague a divisor(s) = 2s + 1 (favorable aux petites listes).
    """
    total_votes = sum(votes.values())
    eligible = {code: v for code, v in votes.items() if v >= threshold * total_votes}

    allocation = {code: 0 for code in votes}
    if not eligible:
        return allocation

    for _ in range(seats):
        best = max(eligible, key=lambda code: eligible[code] / divisor(allocation[code]))
        allocation[best] += 1

    return allocation


def sainte_lague_allocation(
    votes: dict[str, int],
    seats: int,
    threshold: float = 0.0,
) -> dict[str, int]:
    """Methode Sainte-Lague (diviseurs impairs), plus proportionnelle que D'Hondt."""
    return highest_averages_allocation(votes, seats, lambda s: 2 * s + 1, threshold)


def winner_take_all_allocation(votes: dict[str, int], seats: int) -> dict[str, int]:
    """Scrutin majoritaire integral : la liste arrivee en tete rafle tous les sieges."""
    allocation = {code: 0 for code in votes}
    if votes:
        winner = max(votes, key=lambda code: votes[code])
        allocation[winner] = seats
    return allocation


def _game_from_allocation(allocation: dict[str, int]) -> WeightedVotingGame:
    parties = [code for code, s in allocation.items() if s > 0]
    weights = tuple(allocation[code] for code in parties)
    return majority_game(weights, tuple(parties))


def compare_scrutin_modes_2024() -> list[dict[str, object]]:
    """
    Applique trois modes de scrutin aux memes suffrages des europeennes 2024 et
    calcule, pour chacun, la repartition des 81 sieges et le pouvoir de pivot
    (Shapley-Shubik) de la liste arrivee en tete (RN). Met en evidence que la
    regle de scrutin, a voix constantes, deplace le pouvoir de pivot.
    """
    votes = {p.code: p.votes for p in EUROPEENNES_2024}
    leader = max(votes, key=lambda code: votes[code])

    modes: dict[str, dict[str, int]] = {
        "D'Hondt (proportionnelle)": dhondt_allocation(votes, SEATS_2024),
        "Sainte-Lague (proportionnelle)": sainte_lague_allocation(votes, SEATS_2024),
        "Majoritaire integral": winner_take_all_allocation(votes, SEATS_2024),
    }

    rows: list[dict[str, object]] = []
    for mode, allocation in modes.items():
        game = _game_from_allocation(allocation)
        names = list(game.names)
        ss = shapley_shubik_exact(game)
        leader_idx = names.index(leader) if leader in names else None

        leader_seats = allocation[leader]
        leader_seat_share = leader_seats / SEATS_2024
        leader_power = ss[leader_idx] if leader_idx is not None else 0.0

        rows.append(
            {
                "Mode": mode,
                "Listes en sieges": sum(1 for s in allocation.values() if s > 0),
                f"Sieges {leader}": leader_seats,
                f"Part sieges {leader} %": round(leader_seat_share * 100, 1),
                f"Pouvoir {leader} (Shapley) %": round(leader_power * 100, 1),
                f"Ecart pouvoir-sieges {leader} (pts)": round(
                    (leader_power - leader_seat_share) * 100, 1
                ),
            }
        )

    return rows
