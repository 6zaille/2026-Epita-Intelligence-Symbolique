"""Joueur Monte Carlo Tree Search (MCTS) avec sélection UCB1.

MCTS construit incrémentalement un arbre de recherche par répétition de quatre
phases (Browne et al. 2012) :

    1. Sélection   : depuis la racine, descendre en choisissant l'enfant qui
                     maximise UCB1, jusqu'à un nœud non complètement développé.
    2. Expansion   : ajouter un nouvel enfant (un coup non encore essayé).
    3. Simulation  : jouer aléatoirement jusqu'à une position terminale (rollout).
    4. Rétropropagation : remonter le résultat le long du chemin parcouru.

Le coup finalement joué est l'enfant de la racine le PLUS VISITÉ (robuste), pas
celui de meilleure moyenne. Le budget est configurable : nombre de simulations
OU temps (en secondes). On expose le nombre de visites par coup pour la
visualisation « ce que pense l'agent ».

UCB1 : argmax_a  Q(a) + c * sqrt( ln(N_parent) / N(a) )
où Q(a) est le taux de victoire moyen du coup a DU POINT DE VUE du joueur au
trait dans le nœud parent, et c la constante d'exploration (sqrt(2) par défaut).
"""

from __future__ import annotations

import math
import random
import time
from typing import Dict, List, Optional

from agents.base import Agent
from game.connect_four import PLAYER1, PLAYER2, ConnectFour


class _Node:
    """Nœud de l'arbre MCTS.

    Représente un état de jeu atteint après `move` joué par l'adversaire du
    `player_to_move`. On stocke les statistiques agrégées (`visits`, `wins`).
    `wins` est compté du point de vue du joueur qui DOIT jouer dans le parent
    (c'est ce point de vue qui rend la comparaison UCB1 cohérente entre frères).
    """

    __slots__ = ("move", "parent", "children", "visits", "wins", "untried_moves", "player_to_move")

    def __init__(
        self,
        player_to_move: int,
        move: Optional[int] = None,
        parent: Optional["_Node"] = None,
        untried_moves: Optional[List[int]] = None,
    ) -> None:
        self.move = move                       # coup menant à ce nœud
        self.parent = parent
        self.children: List["_Node"] = []
        self.visits = 0
        self.wins = 0.0                        # somme des résultats (vue parent)
        self.untried_moves = untried_moves if untried_moves is not None else []
        self.player_to_move = player_to_move   # joueur au trait dans ce nœud

    def is_fully_expanded(self) -> bool:
        return len(self.untried_moves) == 0

    def ucb1(self, c: float) -> float:
        """Score UCB1 de ce nœud, évalué depuis le parent."""
        if self.visits == 0:
            return math.inf  # toujours explorer un coup jamais essayé
        exploitation = self.wins / self.visits
        exploration = c * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration

    def best_child(self, c: float) -> "_Node":
        return max(self.children, key=lambda child: child.ucb1(c))


class MCTSAgent(Agent):
    """Agent MCTS avec UCB1.

    Budget : préciser `n_simulations` (nombre de rollouts) OU `time_budget` (s).
    Si les deux sont fournis, on s'arrête au premier atteint. `c` est la constante
    d'exploration UCB1.
    """

    def __init__(
        self,
        n_simulations: Optional[int] = 1000,
        time_budget: Optional[float] = None,
        c: float = math.sqrt(2),
        seed: Optional[int] = None,
        name: Optional[str] = None,
    ) -> None:
        if n_simulations is None and time_budget is None:
            raise ValueError("Préciser au moins n_simulations ou time_budget.")
        self.n_simulations = n_simulations
        self.time_budget = time_budget
        self.c = c
        self._rng = random.Random(seed)
        if name:
            self.name = name
        elif time_budget is not None:
            self.name = f"MCTS({time_budget}s)"
        else:
            self.name = f"MCTS({n_simulations}sim)"

        # Visites par coup au dernier appel (pour la visualisation).
        self.last_visit_counts: Dict[int, int] = {}
        self.last_win_rates: Dict[int, float] = {}
        # Nombre réel de simulations effectuées au dernier coup.
        self.last_simulations = 0

    # ------------------------------------------------------------------ #
    # Phases MCTS
    # ------------------------------------------------------------------ #
    def _select_and_expand(self, root: _Node, game: ConnectFour) -> _Node:
        """Phases 1 et 2 : descend par UCB1 puis développe un nouveau coup.

        `game` est muté pour suivre le chemin ; il reflète l'état du nœud renvoyé.
        """
        node = root
        # 1. Sélection : tant que le nœud est développé et non terminal.
        while node.is_fully_expanded() and node.children:
            node = node.best_child(self.c)
            game.play_move(node.move)

        # 2. Expansion : si des coups restent à essayer et l'état n'est pas terminal.
        if node.untried_moves and not game.is_terminal():
            move = self._rng.choice(node.untried_moves)
            node.untried_moves.remove(move)
            game.play_move(move)
            child = _Node(
                player_to_move=game.current_player,
                move=move,
                parent=node,
                untried_moves=game.legal_moves(),
            )
            node.children.append(child)
            node = child
        return node

    def _simulate(self, game: ConnectFour) -> Optional[int]:
        """Phase 3 : rollout aléatoire jusqu'à un état terminal. Renvoie le gagnant (ou None)."""
        while not game.is_terminal():
            game.play_move(self._rng.choice(game.legal_moves()))
        return game.winner()

    def _backpropagate(self, node: Optional[_Node], winner: Optional[int]) -> None:
        """Phase 4 : remonte le résultat le long du chemin.

        Pour chaque nœud, on incrémente `wins` du point de vue du joueur au trait
        dans le PARENT (= l'adversaire du joueur au trait dans le nœud courant),
        car c'est ce parent qui « choisit » ce coup et compare ses frères.
        """
        while node is not None:
            node.visits += 1
            if winner is not None:
                # Joueur qui a joué le coup menant à `node` = adversaire de player_to_move.
                mover = PLAYER1 if node.player_to_move == PLAYER2 else PLAYER2
                if winner == mover:
                    node.wins += 1.0
            else:
                node.wins += 0.5  # match nul : demi-point
            node = node.parent

    # ------------------------------------------------------------------ #
    # Interface publique
    # ------------------------------------------------------------------ #
    def search(self, game: ConnectFour) -> int:
        """Lance MCTS sur la position et renvoie le coup le plus visité."""
        root = _Node(player_to_move=game.current_player, untried_moves=game.legal_moves())

        n_target = self.n_simulations if self.n_simulations is not None else math.inf
        deadline = (time.perf_counter() + self.time_budget) if self.time_budget else None

        sims = 0
        while sims < n_target:
            if deadline is not None and time.perf_counter() >= deadline:
                break
            sim_game = game.copy()
            leaf = self._select_and_expand(root, sim_game)
            winner = self._simulate(sim_game)
            self._backpropagate(leaf, winner)
            sims += 1

        self.last_simulations = sims
        # Statistiques par coup, pour la visualisation.
        self.last_visit_counts = {child.move: child.visits for child in root.children}
        self.last_win_rates = {
            child.move: (child.wins / child.visits if child.visits else 0.0)
            for child in root.children
        }

        # Coup le plus robuste : le plus visité.
        best = max(root.children, key=lambda child: child.visits)
        return best.move

    def move(self, game: ConnectFour) -> int:
        return self.search(game)
