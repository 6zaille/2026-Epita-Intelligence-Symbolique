"""Agent aléatoire : baseline de référence.

Sert à (1) valider la boucle de jeu et le tournoi, (2) servir d'adversaire-étalon
pour mesurer si un agent « apprend » réellement (le DQN doit le battre nettement).
"""

from __future__ import annotations

import random
from typing import Optional

from agents.base import Agent
from game.connect_four import ConnectFour


class RandomAgent(Agent):
    """Choisit uniformément une colonne parmi les coups légaux.

    Une graine peut être fixée pour rendre les parties reproductibles.
    """

    name = "Random"

    def __init__(self, seed: Optional[int] = None) -> None:
        # Générateur dédié : ne perturbe pas l'état global de `random`.
        self._rng = random.Random(seed)

    def move(self, game: ConnectFour) -> int:
        return self._rng.choice(game.legal_moves())
