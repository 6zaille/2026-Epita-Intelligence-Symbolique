"""Tests de l'agent DQN (étape 5).

Tests rapides (pas d'entraînement long ici) : encodage canonique, forme du
réseau, légalité des coups, exposition des Q-valeurs, et un mini-entraînement
qui vérifie seulement que la mécanique tourne (transitions, optimisation, loss).
L'évaluation « bat nettement le hasard » se fait dans le notebook / un script
dédié, car elle demande quelques milliers d'épisodes.
"""

import numpy as np
import torch

from agents.dqn import DQNAgent, DQNTrainer, QNetwork, encode_state, set_seed
from game.connect_four import COLS, ROWS, ConnectFour


def test_encode_state_shape_and_canonical():
    g = ConnectFour()
    g.play_move(3)  # J1 en (0,3) ; c'est maintenant à J2 de jouer
    planes = encode_state(g)
    assert planes.shape == (2, ROWS, COLS)
    # Canal 0 = joueur au trait (J2) -> aucun jeton encore ; canal 1 = J1 -> 1 jeton.
    assert planes[0].sum() == 0
    assert planes[1].sum() == 1
    assert planes[1, 0, 3] == 1.0


def test_network_output_shape():
    net = QNetwork()
    x = torch.zeros(4, 2, ROWS, COLS)
    out = net(x)
    assert out.shape == (4, COLS)


def test_dqn_agent_plays_legal_and_exposes_q():
    set_seed(0)
    agent = DQNAgent(QNetwork())
    g = ConnectFour()
    col = agent.move(g)
    assert col in g.legal_moves()
    # Q-valeurs exposées pour chaque coup légal (pour la visualisation).
    assert set(agent.last_q_values) == set(g.legal_moves())


def test_dqn_agent_respects_full_columns():
    set_seed(0)
    agent = DQNAgent(QNetwork())
    g = ConnectFour()
    for _ in range(ROWS):  # remplit la colonne 0
        g.play_move(0)
    col = agent.move(g)
    assert col != 0
    assert col in g.legal_moves()


def test_trainer_smoke_runs_and_logs():
    # Mini-entraînement : on vérifie que la mécanique tourne et journalise.
    trainer = DQNTrainer(
        buffer_size=2000,
        batch_size=32,
        epsilon_decay_episodes=50,
        target_update_every=20,
        train_steps_per_episode=2,
        seed=0,
    )
    hist = trainer.train(episodes=60, eval_every=30, eval_games=10, verbose=False)
    # Des pertes ont été enregistrées et l'évaluation a tourné deux fois.
    assert len(hist.losses) > 0
    assert len(hist.winrate_vs_random) == 2
    # Les taux de victoire sont des proportions valides.
    assert all(0.0 <= w <= 1.0 for w in hist.winrate_vs_random)
    # L'agent produit toujours un coup légal après entraînement.
    agent = trainer.agent()
    assert agent.move(ConnectFour()) in range(COLS)
