# Rapport — E3 : Jeux coopératifs et valeur de Shapley

## 1. Contexte et problème

La **théorie des jeux coopératifs** modélise des situations où des agents
peuvent former des **coalitions** et se partager un gain collectif. Un jeu à
utilité transférable (TU-game) est une paire `(N, v)` où `N = {0, …, n-1}` est
l'ensemble des joueurs et `v : 2^N → ℝ` la **fonction caractéristique**, avec
`v(∅) = 0` : `v(S)` est la valeur que la coalition `S` peut garantir.

La question centrale est **normative** : une fois la grande coalition `N`
formée et le gain `v(N)` produit, *comment le répartir équitablement* entre les
joueurs ? Une allocation est un vecteur `x ∈ ℝ^n` avec, idéalement,
`Σ x_i = v(N)` (efficacité).

## 2. La valeur de Shapley

### 2.1 Définition

Shapley (1953) propose de payer chaque joueur selon sa **contribution
marginale moyenne**, en considérant tous les ordres d'arrivée possibles :

```
φ_i(v) = (1/n!) · Σ_π [ v(P_i^π ∪ {i}) − v(P_i^π) ]
```

où `P_i^π` est l'ensemble des joueurs précédant `i` dans la permutation `π`.
En regroupant les permutations par la coalition `S = P_i^π`, on obtient la
**formule par coalitions**, bien plus efficace (`O(2^n)` au lieu de `O(n!)`) :

```
φ_i(v) = Σ_{S ⊆ N\{i}}  [ |S|! (n−|S|−1)! / n! ] · ( v(S ∪ {i}) − v(S) )
```

Le poids `ω(s) = s!(n−s−1)!/n!` est exactement la probabilité que la coalition
`S` (de taille `s`) soit l'ensemble des prédécesseurs de `i` dans une
permutation uniforme.

### 2.2 Implémentation

Les deux formulations sont dans `shapley/exact.py` :

- `shapley_by_permutations` — définition directe, `O(n!)`, limitée à `n ≤ 11`,
  utile en pédagogie et comme test croisé ;
- `shapley_exact` — formule par coalitions, `O(2^n)`, praticable jusqu'à `n ≈ 20`.
  Une seule passe sur les `2^n` coalitions distribue la contribution de chaque
  `v(S)` à tous les joueurs, ce qui évite de réévaluer `v(S)`.

Les coalitions sont représentées par des **masques de bits** (`shapley/game.py`)
et les valeurs `v(S)` sont **mémoïsées**, ce qui rend les parcours efficaces et
compatibles avec des fonctions caractéristiques coûteuses (comme SHAP).

### 2.3 Validation sur jeux classiques

| Jeu | Valeur de Shapley | Interprétation |
|-----|-------------------|----------------|
| **Gloves** (1 gauche, 2 droits) | L = 2/3, R = 1/6 chacun | le bien **rare** capte la valeur |
| **Airport** [1, 2, 4] | 1/3, 5/6, 17/6 | partage par segments de piste |
| **ONU** (5 permanents, 10 non-perm.) | 0,1963 / 0,00186 | le veto vaut ~105× un siège tournant |

Les deux formulations coïncident (test `test_coalition_vs_permutation_agree`) et
l'efficacité `Σφ_i = v(N)` est toujours respectée.

## 3. Les quatre axiomes (unicité)

Shapley démontre que sa valeur est l'**unique** application vérifiant :

1. **Efficacité** — `Σ_i φ_i(v) = v(N)` : tout le gain est réparti.
2. **Symétrie** — deux joueurs interchangeables reçoivent la même part.
3. **Joueur nul** — un joueur sans contribution reçoit zéro.
4. **Additivité** — `φ(v + w) = φ(v) + φ(w)` : linéarité sur les jeux.

`shapley/axioms.py` fournit des prédicats testables : détection des joueurs
nuls et des paires symétriques par balayage des `2^n` coalitions, puis
vérification que la valeur calculée respecte chaque axiome. C'est une
**illustration** numérique de la caractérisation (non une preuve formelle) qui
sert aussi de garde-fou de correction. Tous les axiomes sont validés sur les
jeux du catalogue (`tests/test_axioms.py`).

## 4. Approximation Monte Carlo

Puisque `φ_i = E_π[ contribution marginale de i ]`, on l'estime en tirant `m`
permutations aléatoires (algorithme de **Castro, Gómez & Tejada, 2009**). Une
subtilité d'efficacité : **chaque permutation tirée fournit en une seule passe
une contribution marginale pour les `n` joueurs**, d'où seulement `m(n+1)`
évaluations de `v` au lieu de `2^n`.

- L'estimateur est **sans biais** ; l'efficacité `Σφ̂_i = v(N)` est même
  préservée exactement à chaque tirage.
- L'erreur décroît en `O(1/√m)` (théorème central limite). La figure
  `figures/convergence_mc.png` confirme la pente `−1/2` en échelle log-log.
- `shapley/monte_carlo.py` calcule aussi l'**erreur-type** par joueur (mise à
  jour en ligne de Welford), utile pour un critère d'arrêt.

C'est ce qui rend Shapley **applicable en pratique** quand `n` est grand (SHAP
sur des modèles à des dizaines de features).

## 5. Cœur, convexité et stabilité

L'efficacité ne dit rien de la **stabilité** : une coalition `S` acceptera-t-elle
l'allocation, ou aura-t-elle intérêt à faire sécession ? Le **cœur** est
l'ensemble des allocations efficaces et *stables* :

```
Core(v) = { x : Σ x_i = v(N),  Σ_{i∈S} x_i ≥ v(S)  ∀ S }
```

C'est un polytope possiblement **vide**. Un jeu est **convexe**
(supermodulaire) si `v(S) + v(T) ≤ v(S∪T) + v(S∩T)`, ce qui équivaut à des
contributions marginales croissantes.

**Théorème (Shapley, 1971)** : pour un jeu convexe, le cœur est non vide, ses
sommets sont les `n!` vecteurs marginaux, et **la valeur de Shapley — leur
barycentre — appartient au cœur**.

`shapley/core.py` teste la convexité, l'appartenance au cœur et calcule les
sommets ; `shapley/viz.py` trace le cœur sur le **simplexe barycentrique**
(`figures/core_simplex.png`) :

- **jeu convexe** : cœur = hexagone bleu, Shapley (étoile) en son barycentre ✔ ;
- **jeu de majorité** (`v(S)=1 ssi |S|≥2`) : cœur **vide** ; la valeur de
  Shapley `(1/3, 1/3, 1/3)` existe toujours mais n'est stabilisée par aucune
  allocation (déficit maximal `1/3`).

## 6. Indices de pouvoir : le Conseil de sécurité de l'ONU

Un **jeu simple** est un jeu `0/1` (coalitions gagnantes / perdantes). La valeur
de Shapley y devient l'**indice de Shapley-Shubik**, mesurant la fréquence à
laquelle un joueur est **pivot**. On l'oppose à l'**indice de Banzhaf** (nombre
de coalitions où le joueur est décisif).

On modélise le Conseil de sécurité (5 permanents à veto, 10 non-permanents ;
une résolution passe avec ≥ 9 voix dont les 5 permanents) comme un jeu de vote
pondéré et on calcule les indices exactement via `2^15` coalitions :

| Membre | Shapley-Shubik | Banzhaf | Poids naïf |
|--------|---------------|---------|-----------|
| Permanent | **0,1963** | 0,167 | 1/15 = 0,067 |
| Non-permanent | **0,00186** | 0,0165 | 1/15 = 0,067 |

Résultat frappant (`figures/unsc_power.png`) : les 5 permanents cumulent **98 %**
du pouvoir réel, un permanent pèse ~**105×** un non-permanent. Le pouvoir ne se
lit pas dans le « poids » apparent.

## 7. Applications

### 7.1 Partage de coûts d'infrastructure (aéroport)

Des avions aux exigences croissantes partagent une piste ; le coût d'une
coalition est le coût de son membre le plus exigeant : `c(S) = max_{i∈S} c_i`.
La valeur de Shapley donne la règle historique de **Littlechild & Owen (1973)** :
découper la piste en **segments** et partager le coût de chaque segment à parts
égales entre les usagers qui en ont besoin.

`applications/airport_cost.py` calcule cette répartition par la forme close
`O(n log n)` **et** par `shapley_exact` `O(2^n)`, et vérifie qu'elles coïncident
(`figures/airport_cost.png`). C'est l'illustration qu'une **forme close** peut
remplacer l'énumération exponentielle sur des jeux structurés.

### 7.2 Explicabilité ML : les valeurs SHAP

Pour expliquer une prédiction `f(x*)`, on prend les **features comme joueurs** et
on définit la valeur d'une coalition `S` comme la prédiction moyenne quand on
connaît `x*_S` et qu'on marginalise le reste sur un jeu de données de référence
(formulation interventionnelle de **Lundberg & Lee, 2017**) :

```
v(S) = E_b[ f(x*_S, b_{-S}) ] − E_b[ f(b) ]
```

Les valeurs de Shapley de ce jeu sont les **valeurs SHAP**. L'axiome
d'**efficacité** devient la propriété de *local accuracy* :

```
Σ_i φ_i = f(x*) − E[f]
```

`applications/shap_ml.py` calcule les SHAP **exactes** (énumération des `2^n`
coalitions de features) et les recoupe avec l'estimateur Monte Carlo. Sur un
`GradientBoostingRegressor`, la *local accuracy* est vérifiée exactement et les
features informatives captent la contribution (`figures/shap_waterfall.png`).
C'est le **pont** entre un concept de théorie des jeux de 1953 et l'IA
explicable contemporaine.

## 8. Complexité et limites

| Méthode | Complexité | Domaine praticable |
|---------|-----------|--------------------|
| Permutations | `O(n! · n)` | `n ≤ 11` |
| Coalitions | `O(2^n · n)` | `n ≤ 20` |
| Monte Carlo | `O(m · n)`, erreur `O(1/√m)` | `n` grand |
| Forme close (aéroport) | `O(n log n)` | jeux structurés uniquement |

Le calcul exact de la valeur de Shapley est **#P-difficile** dans le cas
général ; l'échantillonnage et l'exploitation de structures (jeux de vote, jeux
de coûts, jeux convexes) sont les deux voies de passage à l'échelle.

## 9. Perspectives

- Vérification **formelle** des axiomes en Lean 4 (PGame/Mathlib) — objectif
  optionnel du sujet.
- Estimateurs Monte Carlo à **variance réduite** (stratification, échantillonnage
  par strates de taille de coalition).
- Autres valeurs (Banzhaf, τ-value, nucléole) et comparaison de leurs propriétés.
- SHAP sur des modèles à plus grand nombre de features avec l'estimation par
  échantillonnage.

## 10. Reproductibilité

```bash
pip install -r requirements.txt
python scripts/run_all.py     # résultats + figures
python -m pytest tests/       # 27 tests
```
