"""Bibliotheque de jeux cooperatifs classiques.

Chaque constructeur renvoie un :class:`~shapley.game.CooperativeGame` pret a
etre analyse. Ces jeux servent de bancs d'essai a valeur de Shapley connue
(litterature) pour valider l'implementation.
"""

from __future__ import annotations

from typing import List, Sequence

from .game import CooperativeGame


# ----------------------------------------------------------------------
# Jeu des gants (Gloves game)
# ----------------------------------------------------------------------
def gloves_game(n_left: int, n_right: int) -> CooperativeGame:
    """Jeu des gants : ``v(S) = min(#gauches dans S, #droits dans S)``.

    Une paire (un gant gauche + un gant droit) vaut 1 ; un gant seul ne vaut
    rien. Exemple canonique de rarete : le cote minoritaire capte la valeur.
    Les joueurs ``0..n_left-1`` possedent un gant gauche, les suivants un droit.
    """
    n = n_left + n_right
    left = set(range(n_left))

    def v(S):
        nl = sum(1 for i in S if i in left)
        nr = len(S) - nl
        return float(min(nl, nr))

    names = [f"L{i+1}" for i in range(n_left)] + [f"R{j+1}" for j in range(n_right)]
    return CooperativeGame(n, v, names=names)


# ----------------------------------------------------------------------
# Jeu de l'aeroport (Airport cost game)
# ----------------------------------------------------------------------
def airport_game(costs: Sequence[float]) -> CooperativeGame:
    """Jeu de couts de l'aeroport.

    Chaque joueur ``i`` (un mouvement d'avion) requiert une piste dont le cout
    de construction est ``costs[i]``. Une coalition doit financer la piste la
    plus longue de ses membres : ``c(S) = max_{i in S} costs[i]`` (et
    ``c(emptyset) = 0``). C'est un *jeu de couts* : la valeur de Shapley donne
    la regle de partage des couts d'infrastructure de Littlechild & Owen (1973).
    """
    costs = [float(c) for c in costs]

    def c(S):
        return max((costs[i] for i in S), default=0.0)

    names = [f"A{i+1}(c={costs[i]:g})" for i in range(len(costs))]
    return CooperativeGame(len(costs), c, names=names, is_cost=True)


# ----------------------------------------------------------------------
# Jeux de vote ponderes / a majorite (simple games)
# ----------------------------------------------------------------------
def weighted_voting_game(
    weights: Sequence[float],
    quota: float,
    names: Sequence[str] = None,
) -> CooperativeGame:
    """Jeu de vote pondere : ``v(S) = 1`` si ``sum_{i in S} w_i >= quota``.

    Jeu *simple* (valeurs 0/1). La valeur de Shapley d'un tel jeu est l'indice
    de pouvoir de Shapley-Shubik.
    """
    weights = [float(w) for w in weights]

    def v(S):
        return 1.0 if sum(weights[i] for i in S) >= quota - 1e-9 else 0.0

    if names is None:
        names = [f"V{i+1}(w={weights[i]:g})" for i in range(len(weights))]
    return CooperativeGame(len(weights), v, names=list(names))


def un_security_council_game() -> CooperativeGame:
    """Conseil de securite de l'ONU (15 membres).

    5 membres permanents (droit de veto) et 10 non-permanents. Une resolution
    de fond passe ssi elle reunit >= 9 voix *dont* les 5 permanents. Une
    coalition est donc gagnante ssi elle contient les 5 permanents et au moins
    4 non-permanents. On l'encode comme jeu de vote pondere : chaque permanent
    a un poids 7, chaque non-permanent un poids 1, avec un quota de 39
    (5*7 + 4 = 39 ; retirer un permanent tombe a <= 38, retirer un non-permanent
    sous 4 tombe a <= 38).

    Resultat classique : chaque permanent detient ~19,6 % du pouvoir, chaque
    non-permanent ~0,19 % ; les 5 permanents cumulent ~98,2 %.
    """
    weights = [7] * 5 + [1] * 10
    quota = 39
    names = [f"P{i+1}" for i in range(5)] + [f"N{j+1}" for j in range(10)]
    return weighted_voting_game(weights, quota, names=names)


# ----------------------------------------------------------------------
# Jeux convexes / non convexes de demonstration
# ----------------------------------------------------------------------
def convex_example() -> CooperativeGame:
    """Jeu convexe a 3 joueurs (coeur non vide, Shapley au barycentre).

    Superadditif et supermodulaire ; le cout des synergies croit avec la taille
    des coalitions.
    """
    values = {
        frozenset(): 0,
        frozenset({0}): 0,
        frozenset({1}): 0,
        frozenset({2}): 0,
        frozenset({0, 1}): 1,
        frozenset({0, 2}): 1,
        frozenset({1, 2}): 1,
        frozenset({0, 1, 2}): 4,
    }
    return CooperativeGame(3, values, names=["A", "B", "C"])


def empty_core_example() -> CooperativeGame:
    """Jeu (a majorite simple, 3 joueurs) au coeur VIDE.

    Jeu de majorite ``v(S) = 1`` ssi ``|S| >= 2`` : toute paire peut se
    detourner du tiers, aucune allocation efficace ne resiste. Illustre que la
    valeur de Shapley (1/3, 1/3, 1/3) existe toujours meme sans coeur.
    """
    def v(S):
        return 1.0 if len(S) >= 2 else 0.0

    return CooperativeGame(3, v, names=["A", "B", "C"])


def all_classic_games() -> dict:
    """Catalogue nomme des jeux de demonstration."""
    return {
        "Gloves (1G, 2D)": gloves_game(1, 2),
        "Gloves (2G, 2D)": gloves_game(2, 2),
        "Airport [1,2,4]": airport_game([1, 2, 4]),
        "UN Security Council": un_security_council_game(),
        "Convexe (3 joueurs)": convex_example(),
        "Coeur vide (majorite)": empty_core_example(),
    }
