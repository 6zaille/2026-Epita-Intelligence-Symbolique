"""Interface commune à tous les joueurs artificiels.

Chaque agent implémente `.move(game) -> int` : il reçoit l'état courant du jeu
(`ConnectFour`) et renvoie la colonne qu'il décide de jouer. L'agent NE DOIT PAS
modifier l'état reçu (il peut le copier librement, par ex. pour MCTS).

On garde l'interface minimale pour que minimax, MCTS et DQN soient interchangeables
dans le tournoi round-robin.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from game.connect_four import ConnectFour


class Agent(ABC):
    """Joueur abstrait. Sous-classes : RandomAgent, AlphaBetaAgent, MCTSAgent, DQNAgent."""

    #: Nom lisible affiché dans les tournois et visualisations.
    name: str = "Agent"

    @abstractmethod
    def move(self, game: ConnectFour) -> int:
        """Renvoie la colonne à jouer pour la position `game`.

        La colonne renvoyée doit appartenir à `game.legal_moves()`.
        L'implémentation ne doit pas muter `game`.
        """
        raise NotImplementedError

    def reset(self) -> None:
        """Réinitialise l'état interne éventuel de l'agent entre deux parties.

        Par défaut sans effet ; surchargé par les agents qui gardent un cache
        (table de transposition, arbre MCTS réutilisé, etc.).
        """

    def __str__(self) -> str:
        return self.name
