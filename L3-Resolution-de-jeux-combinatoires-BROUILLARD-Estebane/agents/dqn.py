"""Joueur par apprentissage par renforcement profond (DQN).

Approche : Deep Q-Network entraîné par self-play sur Puissance 4.

Choix de conception importants (documentés car ils conditionnent la stabilité) :

1. ÉTAT CANONIQUE À 2 CANAUX. On encode le plateau du point de vue du JOUEUR AU
   TRAIT : canal 0 = ses jetons, canal 1 = ceux de l'adversaire. Ainsi le réseau
   apprend une seule fonction « valeur pour le joueur au trait » au lieu de deux
   politiques séparées — c'est plus efficace et symétrique.

2. CIBLE NEGAMAX (jeu à somme nulle à 2 joueurs). Après le coup du joueur, c'est
   l'adversaire qui joue ; la valeur de l'état suivant POUR NOUS est l'OPPOSÉ de
   la meilleure valeur de l'adversaire :
       target = r                              si l'état est terminal
       target = -gamma * max_{a'} Q_cible(s', a')   sinon
   où s' est l'état suivant encodé du point de vue de l'adversaire. C'est la
   formulation correcte du minimax appris (cf. self-play AlphaZero, Silver 2016).

3. RÉCOMPENSE. +1 si le coup gagne immédiatement, 0 sinon (les défaites sont
   apprises par bootstrap : si après notre coup l'adversaire peut gagner, alors
   -max Q(s') ≈ -1, donc notre coup est pénalisé).

4. MASQUAGE DES COUPS ILLÉGAUX à la sélection et au calcul du max.

Objectif minimal (filet de sécurité du sujet) : battre NETTEMENT l'agent aléatoire.
On journalise la courbe de loss et le taux de victoire vs Random au fil de
l'entraînement (`history`).
"""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from agents.base import Agent
from game.connect_four import COLS, PLAYER1, PLAYER2, ROWS, ConnectFour

# ROCm s'expose comme CUDA : aucun code spécifique GPU n'est nécessaire.
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def set_seed(seed: int) -> None:
    """Fixe les graines (Python, NumPy, Torch) pour la reproductibilité."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def encode_state(game: ConnectFour) -> np.ndarray:
    """Encode le plateau en tenseur (2, ROWS, COLS) du point de vue du joueur au trait.

    Canal 0 : jetons du joueur au trait. Canal 1 : jetons de l'adversaire.
    """
    me = game.current_player
    opp = PLAYER2 if me == PLAYER1 else PLAYER1
    board = np.asarray(game.board, dtype=np.float32)  # (ROWS, COLS)
    planes = np.zeros((2, ROWS, COLS), dtype=np.float32)
    planes[0] = (board == me).astype(np.float32)
    planes[1] = (board == opp).astype(np.float32)
    return planes


class QNetwork(nn.Module):
    """Petit CNN : 2 couches convolutives puis 2 couches denses -> 7 Q-valeurs."""

    def __init__(self, channels: int = 64) -> None:
        super().__init__()
        self.conv1 = nn.Conv2d(2, channels, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(channels * ROWS * COLS, 128)
        self.fc2 = nn.Linear(128, COLS)  # une Q-valeur par colonne

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = x.reshape(x.size(0), -1)
        x = F.relu(self.fc1(x))
        return self.fc2(x)


@dataclass
class Transition:
    """Transition stockée dans le replay buffer.

    state/next_state sont encodés CHACUN du point de vue du joueur au trait
    correspondant (next_state : point de vue de l'adversaire). `next_legal` est
    le masque des coups légaux dans next_state.
    """

    state: np.ndarray
    action: int
    reward: float
    next_state: Optional[np.ndarray]
    done: bool
    next_legal: Tuple[int, ...]


@dataclass
class TrainHistory:
    """Historique d'entraînement pour les visualisations."""

    steps: List[int] = field(default_factory=list)          # n° d'épisode
    losses: List[float] = field(default_factory=list)        # loss moyenne
    eval_episodes: List[int] = field(default_factory=list)   # épisodes d'évaluation
    winrate_vs_random: List[float] = field(default_factory=list)


class DQNAgent(Agent):
    """Agent jouant gloutonnement selon le Q-network appris.

    L'entraînement est piloté par `DQNTrainer` ; cet agent encapsule le réseau et
    la sélection du coup. `last_q_values` expose les Q-valeurs par colonne (viz).
    """

    name = "DQN"

    def __init__(self, network: Optional[QNetwork] = None, name: Optional[str] = None) -> None:
        self.net = (network or QNetwork()).to(DEVICE)
        if name:
            self.name = name
        self.last_q_values: Dict[int, float] = {}

    @torch.no_grad()
    def q_values(self, game: ConnectFour) -> np.ndarray:
        """Q-valeurs brutes (7) pour la position, sans masquage."""
        self.net.eval()
        state = torch.from_numpy(encode_state(game)).unsqueeze(0).to(DEVICE)
        return self.net(state).cpu().numpy()[0]

    def move(self, game: ConnectFour) -> int:
        q = self.q_values(game)
        legal = game.legal_moves()
        # Masque : on ne choisit que parmi les coups légaux.
        self.last_q_values = {c: float(q[c]) for c in legal}
        return max(legal, key=lambda c: q[c])

    def save(self, path: str) -> None:
        torch.save(self.net.state_dict(), path)

    def load(self, path: str) -> None:
        self.net.load_state_dict(torch.load(path, map_location=DEVICE))
        self.net.to(DEVICE)


class DQNTrainer:
    """Entraîne un QNetwork par self-play avec replay buffer et réseau cible.

    Paramètres principaux : gamma (escompte), epsilon (exploration, décroissant),
    taille du buffer, batch, fréquence de mise à jour du réseau cible.
    """

    def __init__(
        self,
        gamma: float = 0.95,
        lr: float = 1e-3,
        buffer_size: int = 50_000,
        batch_size: int = 128,
        epsilon_start: float = 1.0,
        epsilon_end: float = 0.05,
        epsilon_decay_episodes: int = 3000,
        target_update_every: int = 200,
        train_steps_per_episode: int = 8,
        seed: int = 0,
        channels: int = 64,
    ) -> None:
        set_seed(seed)
        self.gamma = gamma
        self.batch_size = batch_size
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay_episodes = epsilon_decay_episodes
        self.target_update_every = target_update_every
        self.train_steps_per_episode = train_steps_per_episode
        self._rng = random.Random(seed)

        self.policy_net = QNetwork(channels).to(DEVICE)
        self.target_net = QNetwork(channels).to(DEVICE)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.optimizer = torch.optim.Adam(self.policy_net.parameters(), lr=lr)

        self.buffer: Deque[Transition] = deque(maxlen=buffer_size)
        self.history = TrainHistory()

    # ------------------------------------------------------------------ #
    # Sélection de coup pendant le self-play (epsilon-greedy masqué)
    # ------------------------------------------------------------------ #
    def _epsilon(self, episode: int) -> float:
        """Décroissance linéaire d'epsilon."""
        frac = min(1.0, episode / self.epsilon_decay_episodes)
        return self.epsilon_start + frac * (self.epsilon_end - self.epsilon_start)

    @torch.no_grad()
    def _select_action(self, game: ConnectFour, epsilon: float) -> int:
        legal = game.legal_moves()
        if self._rng.random() < epsilon:
            return self._rng.choice(legal)
        self.policy_net.eval()
        state = torch.from_numpy(encode_state(game)).unsqueeze(0).to(DEVICE)
        q = self.policy_net(state).cpu().numpy()[0]
        return max(legal, key=lambda c: q[c])

    # ------------------------------------------------------------------ #
    # Self-play : génère des transitions
    # ------------------------------------------------------------------ #
    def _play_episode(self, epsilon: float) -> None:
        """Joue une partie de self-play et stocke les transitions dans le buffer."""
        game = ConnectFour()
        while not game.is_terminal():
            state = encode_state(game)
            action = self._select_action(game, epsilon)
            game.play_move(action)

            if game.is_terminal():
                winner = game.winner()
                # +1 si le coup que l'on vient de jouer a gagné, 0 si nul.
                reward = 1.0 if winner is not None else 0.0
                self.buffer.append(
                    Transition(state, action, reward, None, True, ())
                )
            else:
                # État suivant : point de vue de l'adversaire (joueur au trait).
                next_state = encode_state(game)
                next_legal = tuple(game.legal_moves())
                self.buffer.append(
                    Transition(state, action, 0.0, next_state, False, next_legal)
                )

    # ------------------------------------------------------------------ #
    # Optimisation : un pas de descente de gradient sur un batch
    # ------------------------------------------------------------------ #
    def _optimize(self) -> Optional[float]:
        if len(self.buffer) < self.batch_size:
            return None
        batch = self._rng.sample(self.buffer, self.batch_size)

        states = torch.from_numpy(np.stack([t.state for t in batch])).to(DEVICE)
        actions = torch.tensor([t.action for t in batch], dtype=torch.long, device=DEVICE)
        rewards = torch.tensor([t.reward for t in batch], dtype=torch.float32, device=DEVICE)
        dones = torch.tensor([t.done for t in batch], dtype=torch.bool, device=DEVICE)

        # Q(s, a) prédit par le réseau policy.
        self.policy_net.train()
        q_sa = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        # Cible negamax : -gamma * max_{a' légal} Q_cible(s', a'), 0 si terminal.
        targets = rewards.clone()
        non_final = [i for i, t in enumerate(batch) if not t.done]
        if non_final:
            next_states = torch.from_numpy(
                np.stack([batch[i].next_state for i in non_final])
            ).to(DEVICE)
            with torch.no_grad():
                q_next = self.target_net(next_states)  # (B', 7)
                # Masque des coups illégaux : -inf pour qu'ils ne soient pas choisis.
                mask = torch.full_like(q_next, float("-inf"))
                for row, i in enumerate(non_final):
                    for c in batch[i].next_legal:
                        mask[row, c] = 0.0
                q_next = q_next + mask
                best_next = q_next.max(dim=1).values  # valeur pour l'ADVERSAIRE
            # Opposé : valeur pour nous = -valeur adversaire.
            for row, i in enumerate(non_final):
                targets[i] = -self.gamma * best_next[row]

        loss = F.smooth_l1_loss(q_sa, targets)  # Huber : robuste aux outliers
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.policy_net.parameters(), 10.0)
        self.optimizer.step()
        return float(loss.item())

    # ------------------------------------------------------------------ #
    # Boucle d'entraînement principale
    # ------------------------------------------------------------------ #
    def train(
        self,
        episodes: int = 4000,
        eval_every: int = 250,
        eval_games: int = 100,
        eval_seed: int = 12345,
        verbose: bool = True,
    ) -> TrainHistory:
        """Entraîne le réseau et journalise loss + taux de victoire vs Random."""
        from agents.random_agent import RandomAgent
        from tournament.runner import play_match

        for episode in range(1, episodes + 1):
            eps = self._epsilon(episode)
            self._play_episode(eps)

            losses = [self._optimize() for _ in range(self.train_steps_per_episode)]
            losses = [l for l in losses if l is not None]
            if losses:
                self.history.steps.append(episode)
                self.history.losses.append(float(np.mean(losses)))

            if episode % self.target_update_every == 0:
                self.target_net.load_state_dict(self.policy_net.state_dict())

            if episode % eval_every == 0:
                agent = DQNAgent(self.policy_net)
                out = play_match(agent, RandomAgent(seed=eval_seed), n_games=eval_games)
                winrate = out["wins_a"] / eval_games
                self.history.eval_episodes.append(episode)
                self.history.winrate_vs_random.append(winrate)
                if verbose:
                    last_loss = self.history.losses[-1] if self.history.losses else float("nan")
                    print(
                        f"Épisode {episode:>5} | eps={eps:.2f} | "
                        f"loss={last_loss:.4f} | winrate vs Random={winrate:.2%}"
                    )

        return self.history

    def agent(self, name: Optional[str] = None) -> DQNAgent:
        """Renvoie un DQNAgent jouable utilisant le réseau policy entraîné."""
        return DQNAgent(self.policy_net, name=name)
