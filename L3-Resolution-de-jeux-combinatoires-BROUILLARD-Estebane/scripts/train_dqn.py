"""Entraîne le DQN par self-play et sauvegarde le modèle + l'historique.

Usage :
    python scripts/train_dqn.py [episodes]

Produit :
    models/dqn.pt            : poids du réseau entraîné
    models/dqn_history.npz   : courbes (loss, taux de victoire vs Random)

Le notebook charge ces artefacts pour éviter de réentraîner (~5 min en CPU).
Reproductible : graine fixe.
"""

from __future__ import annotations

import os
import sys

import numpy as np

# Permet de lancer le script depuis la racine du projet sans installation.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.dqn import DQNTrainer, DEVICE  # noqa: E402

MODEL_PATH = os.path.join("models", "dqn.pt")
HISTORY_PATH = os.path.join("models", "dqn_history.npz")


def main(episodes: int = 2500) -> None:
    print(f"Entraînement DQN sur {episodes} épisodes (device={DEVICE})...")
    trainer = DQNTrainer(
        seed=0,
        epsilon_decay_episodes=2000,
        target_update_every=200,
        train_steps_per_episode=8,
        batch_size=128,
    )
    hist = trainer.train(episodes=episodes, eval_every=250, eval_games=100, verbose=True)

    os.makedirs("models", exist_ok=True)
    trainer.agent().save(MODEL_PATH)
    np.savez(
        HISTORY_PATH,
        steps=np.array(hist.steps),
        losses=np.array(hist.losses),
        eval_episodes=np.array(hist.eval_episodes),
        winrate_vs_random=np.array(hist.winrate_vs_random),
    )
    print(f"\nModèle sauvegardé   -> {MODEL_PATH}")
    print(f"Historique sauvegardé -> {HISTORY_PATH}")
    print(f"Taux de victoire final vs Random : {hist.winrate_vs_random[-1]:.1%}")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2500
    main(n)
