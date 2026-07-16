"""Boucle de jeu et tournoi round-robin.

`play_game` fait jouer deux agents l'un contre l'autre et renvoie le résultat
ainsi que le temps de réflexion par coup. `round_robin` oppose tous les agents
deux à deux, sur plusieurs parties, en alternant qui commence (pour neutraliser
l'avantage du premier joueur, important au Puissance 4).

Version incrémentale : suffisante pour valider la boucle dès l'étape 2 ; enrichie
ensuite (étape 6) pour la collecte de statistiques du tournoi.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from itertools import combinations
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from agents.base import Agent
from game.connect_four import PLAYER1, PLAYER2, ConnectFour


@dataclass
class GameResult:
    """Résultat d'une partie unique.

    winner : 1, 2 ou None (nul).
    moves : liste des colonnes jouées dans l'ordre.
    move_times : temps de réflexion (s) par coup, dans l'ordre des coups.
    move_times_by_player : temps agrégés par joueur (1 et 2), pour les stats.
    """

    winner: Optional[int]
    moves: List[int]
    move_times: List[float]
    move_times_by_player: Dict[int, List[float]] = field(default_factory=dict)


def play_game(
    agent1: Agent,
    agent2: Agent,
    max_moves: int = 6 * 7,
    verbose: bool = False,
) -> GameResult:
    """Fait jouer agent1 (joueur 1) contre agent2 (joueur 2).

    Mesure le temps de chaque coup. Vérifie la légalité des coups renvoyés par
    les agents (un agent buggé qui joue illégalement lève une erreur explicite).
    """
    game = ConnectFour()
    agent1.reset()
    agent2.reset()
    agents = {PLAYER1: agent1, PLAYER2: agent2}

    moves: List[int] = []
    move_times: List[float] = []
    times_by_player: Dict[int, List[float]] = {PLAYER1: [], PLAYER2: []}

    for _ in range(max_moves):
        if game.is_terminal():
            break
        player = game.current_player
        agent = agents[player]

        t0 = time.perf_counter()
        col = agent.move(game)
        dt = time.perf_counter() - t0

        if col not in game.legal_moves():
            raise ValueError(
                f"L'agent {agent} (joueur {player}) a renvoyé un coup illégal : {col}"
            )

        game.play_move(col)
        moves.append(col)
        move_times.append(dt)
        times_by_player[player].append(dt)

        if verbose:
            print(f"Joueur {player} ({agent}) joue colonne {col} en {dt*1000:.1f} ms")
            print(game.render())
            print()

    return GameResult(
        winner=game.winner(),
        moves=moves,
        move_times=move_times,
        move_times_by_player=times_by_player,
    )


def play_match(
    agent_a: Agent,
    agent_b: Agent,
    n_games: int = 10,
) -> Dict[str, int]:
    """Oppose agent_a et agent_b sur n_games parties en alternant qui commence.

    Renvoie un décompte du point de vue de agent_a : victoires, défaites, nuls.
    """
    wins_a = wins_b = draws = 0
    for i in range(n_games):
        # Alterne le joueur qui commence à chaque partie.
        if i % 2 == 0:
            res = play_game(agent_a, agent_b)
            winner_agent = "a" if res.winner == PLAYER1 else ("b" if res.winner == PLAYER2 else None)
        else:
            res = play_game(agent_b, agent_a)
            winner_agent = "b" if res.winner == PLAYER1 else ("a" if res.winner == PLAYER2 else None)

        if winner_agent == "a":
            wins_a += 1
        elif winner_agent == "b":
            wins_b += 1
        else:
            draws += 1

    return {"wins_a": wins_a, "wins_b": wins_b, "draws": draws}


def round_robin(
    agents: List[Agent],
    n_games: int = 10,
    verbose: bool = True,
) -> List[Tuple[str, str, Dict[str, int]]]:
    """Tournoi round-robin : chaque paire d'agents s'affronte sur n_games parties.

    Renvoie une liste (nom_a, nom_b, résultats). Version minimale pour l'étape 2 ;
    les statistiques détaillées (temps, heatmap) sont ajoutées à l'étape 6.
    """
    results: List[Tuple[str, str, Dict[str, int]]] = []
    for a, b in combinations(agents, 2):
        outcome = play_match(a, b, n_games=n_games)
        results.append((a.name, b.name, outcome))
        if verbose:
            print(
                f"{a.name} vs {b.name} : "
                f"{outcome['wins_a']} - {outcome['wins_b']} "
                f"(nuls {outcome['draws']})"
            )
    return results


# --------------------------------------------------------------------------- #
# Tournoi complet instrumenté (étape 6) : matrice de scores + temps de réflexion
# --------------------------------------------------------------------------- #
@dataclass
class TournamentResult:
    """Résultats agrégés d'un tournoi round-robin complet.

    - names : ordre des agents (lignes/colonnes des matrices).
    - score_matrix[i, j] : score de l'agent i contre l'agent j, dans [0, 1]
      (victoire = 1, nul = 0.5, défaite = 0, moyenné sur les parties). Diagonale = nan.
    - wins/draws/losses_matrix[i, j] : décomptes bruts de i contre j.
    - avg_move_time[name] : temps de réflexion moyen par coup (s), tous adversaires.
    - total_score[name] : score total (somme des points marqués) -> classement.
    """

    names: List[str]
    score_matrix: np.ndarray
    wins_matrix: np.ndarray
    draws_matrix: np.ndarray
    losses_matrix: np.ndarray
    avg_move_time: Dict[str, float]
    total_score: Dict[str, float]


def run_tournament(
    agents: List[Agent],
    n_games: int = 20,
    verbose: bool = True,
) -> TournamentResult:
    """Round-robin complet : remplit la matrice de scores et mesure les temps.

    Chaque paire joue n_games parties en alternant qui commence. On collecte le
    temps de réflexion par coup pour chaque agent (toutes parties confondues),
    afin d'alimenter la heatmap et l'analyse vitesse/force.
    """
    n = len(agents)
    names = [a.name for a in agents]
    wins = np.zeros((n, n))
    draws = np.zeros((n, n))
    losses = np.zeros((n, n))
    move_times: Dict[str, List[float]] = {a.name: [] for a in agents}

    for i, j in combinations(range(n), 2):
        a, b = agents[i], agents[j]
        for k in range(n_games):
            # Alterne le premier joueur pour neutraliser l'avantage de J1.
            if k % 2 == 0:
                res = play_game(a, b)
                first, second = a, b
            else:
                res = play_game(b, a)
                first, second = b, a

            # Attribue le résultat aux bons agents (i, j).
            if res.winner == PLAYER1:
                winner_name = first.name
            elif res.winner == PLAYER2:
                winner_name = second.name
            else:
                winner_name = None

            if winner_name == a.name:
                wins[i, j] += 1; losses[j, i] += 1
            elif winner_name == b.name:
                wins[j, i] += 1; losses[i, j] += 1
            else:
                draws[i, j] += 1; draws[j, i] += 1

            # Temps de réflexion : J1 = `first`, J2 = `second`.
            move_times[first.name].extend(res.move_times_by_player[PLAYER1])
            move_times[second.name].extend(res.move_times_by_player[PLAYER2])

        if verbose:
            print(
                f"{a.name} vs {b.name} : "
                f"{int(wins[i, j])} - {int(wins[j, i])} (nuls {int(draws[i, j])})"
            )

    # Matrice de score dans [0, 1] (nul = 0.5), diagonale = nan.
    score = np.full((n, n), np.nan)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            played = wins[i, j] + losses[i, j] + draws[i, j]
            score[i, j] = (wins[i, j] + 0.5 * draws[i, j]) / played if played else np.nan

    total_score = {
        names[i]: float(np.nansum(wins[i, :] + 0.5 * draws[i, :])) for i in range(n)
    }
    avg_move_time = {
        name: (float(np.mean(times)) if times else 0.0) for name, times in move_times.items()
    }

    return TournamentResult(
        names=names,
        score_matrix=score,
        wins_matrix=wins,
        draws_matrix=draws,
        losses_matrix=losses,
        avg_move_time=avg_move_time,
        total_score=total_score,
    )


def strength_vs_budget(
    agent_factory: Callable[[float], Agent],
    opponent: Agent,
    budgets: List[float],
    n_games: int = 20,
) -> List[float]:
    """Mesure le taux de victoire d'un agent contre un adversaire fixe, par budget.

    `agent_factory(budget)` construit l'agent pour un budget donné (temps ou
    profondeur). Renvoie la liste des taux de victoire (dans [0, 1]) alignée sur
    `budgets`. Sert à la courbe « force vs budget de temps alloué ».
    """
    winrates: List[float] = []
    for budget in budgets:
        agent = agent_factory(budget)
        out = play_match(agent, opponent, n_games=n_games)
        winrates.append((out["wins_a"] + 0.5 * out["draws"]) / n_games)
    return winrates
