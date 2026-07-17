# Puissance 4 — Minimax/α-β · MCTS · DQN

Projet L3 — *Résolution de jeux combinatoires par minimax et alpha-beta*.
Trois joueurs artificiels pour le Puissance 4 (Connect Four), comparés par un
tournoi round-robin. Le livrable est [`notebook.ipynb`](notebook.ipynb).

## Structure

```
game/connect_four.py     # plateau 6×7, gravité, victoire, hash Zobrist
agents/base.py           # interface Agent
agents/random_agent.py   # baseline aléatoire
agents/alphabeta.py      # minimax + α-β + table de transposition + move ordering
agents/mcts.py           # MCTS avec UCB1
agents/dqn.py            # CNN, self-play, replay buffer, cible negamax
tournament/runner.py     # round-robin, matrice de scores, temps de réflexion
viz/                     # visualisations réutilisables (pruning, tournoi, plateau)
tests/                   # pytest (moteur + agents + viz)
scripts/train_dqn.py     # entraîne et sauvegarde le DQN -> models/
scripts/build_notebook.py# régénère notebook.ipynb depuis les modules
scripts/build_slides.py  # régénère slides/soutenance.pptx (support ~10 min)
models/dqn.pt            # modèle DQN pré-entraîné
notebook.ipynb           # LIVRABLE : rapport visuel
slides/soutenance.pptx   # LIVRABLE : support de soutenance (avec notes)
```

## Installation

L'environnement réutilise les paquets système (numpy, matplotlib, jupyter,
ipywidgets) via un venv `--system-site-packages`, et **réutilise un PyTorch ROCm
déjà installé** ailleurs (pas de re-téléchargement) grâce à un fichier `.pth`.

```bash
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
pip install pytest ipykernel
# expose le torch existant (adapter le chemin) :
echo "/home/ested/kaggle-libre/.venv/lib/python3.12/site-packages" \
  > .venv/lib/python3.12/site-packages/kaggle_torch.pth
# enregistre le noyau Jupyter utilisé par le notebook :
python -m ipykernel install --user --name iasym --display-name "Python (IAsym .venv)"
```

> Le code utilise `device = "cuda" if torch.cuda.is_available() else "cpu"` ; ROCm
> s'expose comme CUDA. Si le GPU n'est pas détecté (fréquent sous WSL2 sans les
> variables `HSA_*`), l'entraînement bascule en CPU (~5 min, suffisant ici).

## Utilisation

```bash
. .venv/bin/activate
pytest                              # 58 tests : moteur + agents + viz
python scripts/train_dqn.py 2500    # (optionnel) ré-entraîner le DQN
python scripts/build_notebook.py    # régénérer le notebook
python scripts/build_slides.py      # régénérer les slides (slides/soutenance.pptx)
jupyter lab notebook.ipynb          # ouvrir le rapport (noyau « Python (IAsym .venv) »)
```

## Les trois visualisations clés

1. **Élagage α-β visible** — arbre de recherche avec branches coupées + nœuds
   explorés selon les optimisations (minimax → α-β → TT → move ordering).
2. **Heatmap du tournoi** — matrice agent×agent + compromis force/vitesse +
   courbe force vs budget de temps.
3. **Plateau interactif** (ipywidgets) — jouer contre un agent avec affichage de
   sa « pensée » (évaluation α-β / visites MCTS / Q-valeurs DQN).
