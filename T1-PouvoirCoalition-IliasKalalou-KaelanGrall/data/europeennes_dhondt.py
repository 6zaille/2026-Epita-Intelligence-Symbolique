from __future__ import annotations

import math
from dataclasses import dataclass

from core.games import WeightedVotingGame, majority_game


@dataclass(frozen=True)
class PartyVotes:
    """Liste candidate : sigle, libelle et suffrages exprimes."""

    code: str
    label: str
    votes: int


# Europeennes du 9 juin 2024, listes au-dessus de 5 % (France entiere).
# Source : https://www.resultats-elections.interieur.gouv.fr/europeennes2024
EUROPEENNES_2024: tuple[PartyVotes, ...] = (
    PartyVotes("RN", "Rassemblement National (Bardella)", 7_765_936),
    PartyVotes("RE", "Besoin d'Europe / Renaissance (Hayer)", 3_612_419),
    PartyVotes("PS", "Reveiller l'Europe / PS-Place publique (Glucksmann)", 3_422_442),
    PartyVotes("LFI", "La France insoumise (Aubry)", 2_447_909),
    PartyVotes("LR", "Les Republicains (Bellamy)", 1_794_248),
    PartyVotes("ECO", "Europe Ecologie (Toussaint)", 1_361_776),
    PartyVotes("REC", "Reconquete (Marechal)", 1_353_246),
)

SEATS_2024 = 81
THRESHOLD = 0.05


def dhondt_allocation(
    votes: dict[str, int],
    seats: int,
    threshold: float = 0.0,
) -> dict[str, int]:
    """
    Methode D'Hondt (plus forte moyenne) : chaque siege va a la liste de plus
    fort quotient voix / (sieges deja obtenus + 1). Les listes sous le seuil
    (fraction des suffrages totaux) sont exclues.
    """
    total_votes = sum(votes.values())
    eligible = {code: v for code, v in votes.items() if v >= threshold * total_votes}

    allocation = {code: 0 for code in votes}
    if not eligible:
        return allocation

    for _ in range(seats):
        best = max(eligible, key=lambda code: eligible[code] / (allocation[code] + 1))
        allocation[best] += 1

    return allocation


def allocate_2024() -> dict[str, int]:
    """
    Repartition D'Hondt des 81 sieges francais de 2024. Les listes sous le
    seuil legal de 5 % des suffrages exprimes sont deja absentes des donnees ;
    le seuil reapplique ici est sans effet sur la repartition.
    """
    votes = {p.code: p.votes for p in EUROPEENNES_2024}
    return dhondt_allocation(votes, SEATS_2024, THRESHOLD)


def majority_game_europeennes_2024() -> WeightedVotingGame:
    """Jeu a la majorite absolue (41 sur 81) sur la delegation francaise."""
    allocation = allocate_2024()
    parties = [p for p in EUROPEENNES_2024 if allocation[p.code] > 0]
    weights = tuple(allocation[p.code] for p in parties)
    names = tuple(p.code for p in parties)
    return majority_game(weights, names)


def dhondt_marginal_votes(
    votes: dict[str, int],
    seats: int,
    threshold: float = 0.0,
) -> dict[str, object]:
    """
    Analyse des seuils strategiques de la methode D'Hondt. Le dernier siege
    attribue l'est au plus petit quotient gagnant : c'est le prix effectif d'un
    siege. Cette fonction renvoie ce quotient frontiere et, pour chaque liste, le
    nombre de suffrages supplementaires qu'il lui aurait fallu pour emporter un
    siege de plus, a repartition figee des autres listes. Elle rend visibles les
    discontinuites qui poussent aux fusions ou aux scissions de listes.
    """
    total_votes = sum(votes.values())
    eligible = {code: v for code, v in votes.items() if v >= threshold * total_votes}

    quotients: list[tuple[float, str]] = []
    for code, v in eligible.items():
        for k in range(1, seats + 2):
            quotients.append((v / k, code))
    quotients.sort(key=lambda q: q[0], reverse=True)

    allocation = {code: 0 for code in votes}
    for _, code in quotients[:seats]:
        allocation[code] += 1

    # Quotient du dernier siege attribue : prix d'un siege dans cette repartition.
    border_quotient = quotients[seats - 1][0] if seats > 0 else 0.0

    votes_for_next_seat = {}
    for code, v in eligible.items():
        needed = border_quotient * (allocation[code] + 1)
        votes_for_next_seat[code] = max(0, math.ceil(needed - v))

    return {
        "allocation": allocation,
        "quotient_frontiere": border_quotient,
        "voix_pour_un_siege_de_plus": votes_for_next_seat,
    }
