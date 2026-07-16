# B4 — Resolution de puzzles logiques par SMT

## Sujet

Les puzzles logiques (Einstein/Zebra, Knights and Knaves, Nonograms/Picross, Sudoku, Kakuro) sont des problemes de satisfaction de contraintes qui se pretent naturellement a un encodage SMT. Ce sujet compare differents encodages : booleen pur (chaque case = variable binaire), entier (chaque case = variable entiere avec contraintes de domaine), et mixte (contraintes globales comme AllDifferent). L'objectif est de comprendre les compromis entre compacite de l'encodage, temps de resolution, et expressivite. L'etudiant utilise Z3 comme solveur SMT et OR-Tools CP-SAT comme solveur CP, et compare les performances sur des instances de difficulte croissante.

### Objectifs
- Encoder le puzzle d'Einstein (Zebra puzzle) en SMT : 5 maisons, 5 attributs, 15 indices — variables entieres, contraintes d'egalite, de voisinage et d'ordre
- Encoder les puzzles Knights and Knaves en logique propositionnelle pure et en SMT, et analyser les differences de representation
- Implementer un solveur de Nonograms/Picross avec Z3 (contraintes sur les sequences de cases) et comparer avec un solveur CP-SAT (OR-Tools)
- Benchmarker les 3 encodages (booleen, entier, mixte) sur des instances de taille croissante et analyser l'impact sur le temps de resolution
- Etendre a un puzzle non traite (Kakuro, Fill-a-Pix, Slitherlink) et discuter la generalite de l'approche SMT pour les puzzles

### Notebooks CoursIA pertinents

| Notebook | Chemin | Pertinence |
|----------|--------|------------|
| Sudoku multi-solveurs | [Sudoku/](https://github.com/jsboige/CoursIA/tree/main/MyIA.AI.Notebooks/Sudoku) | 18 solveurs compares, Z3, SAT, CP |
| App-11 Picross | [Search/Applications/CSP/App-11-Picross.ipynb](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/Search/Applications/CSP/App-11-Picross.ipynb) | Nonograms/Picross par contraintes |
| CSP-3 Global Constraints | [Search/Part2-CSP/CSP-3-Advanced.ipynb](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/Search/Part2-CSP/CSP-3-Advanced.ipynb) | AllDifferent, contraintes globales |

### References externes
- de Moura, L. & Bjorner, N. (2008). "Z3: An Efficient SMT Solver." *TACAS*. [Springer](https://link.springer.com/chapter/10.1007/978-3-540-78800-3_24)
- Regin, J.-C. (1994). "A Filtering Algorithm for Constraints of Difference in CSPs." *AAAI*. [aaai.org](https://ojs.aaai.org/index.php/AAAI/article/view/9084)
- Bessi, C. et al. (2014). "Verifying Integer and Floating-Point Constraints in SMT." *TACAS*. [Springer](https://link.springer.com/chapter/10.1007/978-3-642-54862-8_20)
- Eiter, T. et al. (2023). "Answer Set Programming and SMT for Combinatorial Problem Solving." *Kuenstliche Intelligenz*. [springer.com](https://link.springer.com/article/10.1007/s13218-023-00816-5)

### Difficulte : 2/5

## Setup

### Installation

Si vous utilisez nix, vous pouvez simplement développer la flake pour avoir la bonne version de python et uv avec
```sh
nix --extra-experimental-features "nix-command flakes" develop
```

Puis, pour installer les dépendence, lancez
```sh
uv sync
```

Et pour lancer le notebook de démonstration, vous aurez besoin d'exécuter
```sh
uv sync --extra notebook
```

### Formattage

Le code est formatté avec Black. Pour le faire, lancez
```sh
uv run black src/
```

## Exécution

Un notebook de démonstration permet de tester le code. Vous le trouverez dans `notebooks/demo.ipynb`.

## Présentation

Vous pouvez retrouver nos transparents [ici](https://epitafr-my.sharepoint.com/:p:/g/personal/brendan_martin_epita_fr/IQC8_Q2_kYrJS7cCMlSQF_f1ASWOdmywN9PN82g_I7LjK8U?rtime=-m4djXHj3kg).
