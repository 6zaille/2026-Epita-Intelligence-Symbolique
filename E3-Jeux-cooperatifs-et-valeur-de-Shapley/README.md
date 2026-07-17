# E3 — Jeux coopératifs et valeur de Shapley

Projet IA Symbolique (SCIA, EPITA 2026). On implémente en **Python pur** la
théorie des jeux coopératifs à utilité transférable : calcul **exact** de la
valeur de Shapley, **approximation Monte Carlo**, **vérification des quatre
axiomes**, étude du **cœur** et des **jeux convexes**, et deux **applications
concrètes** (partage de coûts d'infrastructure et explicabilité de modèles de
ML via les valeurs SHAP).

## Idée

Quand des agents coopèrent, le gain collectif `v(N)` dépasse la somme de ce que
chacun obtiendrait seul. **Comment le partager équitablement ?** Lloyd Shapley
(1953) répond par une formule unique : la moyenne, sur tous les ordres
d'arrivée possibles, de la **contribution marginale** de chaque joueur.

> La valeur de Shapley est l'**unique** règle de partage vérifiant simultanément
> **efficacité**, **symétrie**, **joueur nul** et **additivité**.

Son coût exact est en `O(2^n)` (voire `O(n!)`), ce qui motive un estimateur
Monte Carlo. Le même concept, appliqué aux *features* d'un modèle de ML, donne
les valeurs **SHAP** aujourd'hui omniprésentes en IA explicable.

## Contenu

```
shapley/                moteur de théorie des jeux coopératifs (Python pur)
  game.py               CooperativeGame : fonction caractéristique, cache par masques de bits
  exact.py              valeur de Shapley exacte (formule des coalitions O(2^n) + permutations O(n!))
  monte_carlo.py        estimateur Monte Carlo (Castro et al. 2009) + courbe de convergence
  axioms.py             vérification des 4 axiomes (efficacité, symétrie, joueur nul, additivité)
  core.py               cœur, convexité/supermodularité, théorème « Shapley ∈ cœur »
  power_index.py        indices de pouvoir Shapley-Shubik et Banzhaf (jeux de vote)
  games.py              jeux classiques : Gloves, Airport, Conseil de sécurité ONU, convexes
  viz.py                visualisation du cœur sur le simplexe barycentrique (n = 3)
applications/
  airport_cost.py       partage de coûts d'infrastructure (règle de Littlechild-Owen)
  shap_ml.py            valeurs SHAP = valeur de Shapley des features d'un modèle
scripts/                démonstrations exécutables (impriment les résultats + génèrent les figures)
  demo_games.py         Shapley + axiomes sur les jeux classiques
  demo_convergence.py   convergence Monte Carlo (log-log, pente O(1/√m))
  demo_core.py          cœur convexe vs cœur vide sur le simplexe
  demo_airport.py       partage de coûts de l'aéroport
  demo_power.py         pouvoir réel au Conseil de sécurité de l'ONU
  demo_shap.py          décomposition SHAP d'une prédiction (waterfall)
  run_all.py            lance tout et régénère toutes les figures
tests/                  suite pytest (correction, axiomes, convergence, cœur, applications)
figures/                figures générées
docs/REPORT.md          rapport détaillé
```

## Utilisation

```bash
pip install -r requirements.txt

# toutes les démonstrations + régénération des figures
python scripts/run_all.py

# ou une démonstration ciblée
python scripts/demo_games.py         # valeur de Shapley et axiomes
python scripts/demo_convergence.py   # convergence Monte Carlo
python scripts/demo_core.py          # cœur, convexité, stabilité
python scripts/demo_airport.py       # partage de coûts d'infrastructure
python scripts/demo_power.py         # indices de pouvoir (ONU)
python scripts/demo_shap.py          # explicabilité ML (SHAP)

python -m pytest tests/              # tests
```

### Exemple minimal

```python
from shapley import CooperativeGame, shapley_exact, verify_all_axioms

# jeu des gants : 1 gant gauche (rare), 2 gants droits ; une paire vaut 1
from shapley.games import gloves_game
g = gloves_game(1, 2)

phi = shapley_exact(g)          # -> [0.667, 0.167, 0.167]  (L1, R1, R2)
print(g.label(phi))             # le côté rare capte la valeur
print(verify_all_axioms(g))     # {'efficacite': True, 'symetrie': True, 'joueur_nul': True}
```

## Concepts implémentés

| Concept | Fichier | Résultat vérifié |
|---------|---------|------------------|
| Valeur de Shapley exacte (2 formulations) | `exact.py` | Gloves = (2/3, 1/6, 1/6), Airport [1,2,4] = (1/3, 5/6, 17/6) |
| Approximation Monte Carlo | `monte_carlo.py` | erreur en `O(1/√m)`, estimateur sans biais |
| Les 4 axiomes | `axioms.py` | efficacité, symétrie, joueur nul, additivité |
| Cœur & convexité | `core.py` | jeu convexe ⟹ Shapley ∈ cœur (Shapley 1971) |
| Indices de pouvoir | `power_index.py` | ONU : permanent ≈ 19,6 %, non-permanent ≈ 0,19 % |
| Partage de coûts | `airport_cost.py` | forme close (Littlechild-Owen) = Shapley exact |
| Explicabilité ML (SHAP) | `shap_ml.py` | *local accuracy* : Σ SHAP = f(x*) − E[f] |

## Références

- Shapley, L.S. (1953). *A Value for n-Person Games*. Contributions to the Theory of Games, II.
- Shapley, L.S. (1971). *Cores of Convex Games*. International Journal of Game Theory.
- Castro, Gómez & Tejada (2009). *Polynomial Calculation of the Shapley Value Based on Sampling*.
- Littlechild & Owen (1973). *A Simple Expression for the Shapley Value in a Special Case*.
- Lundberg & Lee (2017). *A Unified Approach to Interpreting Model Predictions* (SHAP), NeurIPS.
- Shapley & Shubik (1954). *A Method for Evaluating the Distribution of Power in a Committee System*.
