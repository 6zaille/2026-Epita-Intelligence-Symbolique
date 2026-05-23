# SUJET O1 — Raisonnement spatial qualitatif par les calculs RCC8

## Rappel des consignes

Implementer le calcul relationnel spatial RCC8 (Region Connection Calculus) qui definit huit relations de base entre regions spatiales : disconnected (DC), externally connected (EC), partially overlapping (PO), tangential proper part (TPP), non-tangential proper part (NTPP), et leurs inverses (TPPi, NTPPi), plus equal (EQ). Le raisonneur par contraintes propage les relations connues pour inferer les relations implicites et detecter les inconsistances dans les configurations spatiales. L'application porte sur la verification de coherence de descriptions spatiales en langage naturel ou la planification robotique.

### Objectifs
- Implementer les huit relations RCC8 et leur table de composition
- Construire un raisonneur par contraintes propageant les relations spatiales implicites
- Implementer la detection d'inconsistances dans les configurations spatiales
- Appliquer le raisonneur a la verification de descriptions spatiales ou a la planification robotique
- Evaluer la complexite et la scalabilite du raisonneur sur des configurations de taille croissante
---


# Définition de RCC8

RCC8 (Region Connection Calculus 8) est un modèle de raisonnement spatial qualitatif utilisé en IA pour décrire comment des régions de l’espace sont liées entre elles, sans utiliser de coordonnées géométriques précises.

Dans RCC8, les “zones” (ou “régions”) sont juste des objets abstraits qui représentent des portions de l’espace.

RCC8 décrit 8 relations possibles entre deux régions A et B:

1. DC — Disconnected : A et B ne se touchent pas du tout.
2. EC — Externally Connected : A et B se touchent juste sur le bord (contact sans chevauchement).
3. PO — Partial Overlap : A et B se chevauchent partiellement.
4. EQ — Equal : A et B sont exactement la même région.
5. TPP — Tangential Proper Part : A est entièrement dans B et touche le bord.
6. NTPP — Non-Tangential Proper Part : A est complètement à l’intérieur de B sans toucher le bord.
7. TPPi — inverse de TPP : B est TPP de A.
8. NTPPi — inverse de NTPP : B est NTPP de A.

Ces relations sont suffisantes pour représenter toute relation topologique de base entre zones.


### Implémentation

Le système implémente un raisonneur spatial basé sur le calcul relationnel RCC8, utilisant l’algorithme de path-consistency (PC-2) pour assurer la propagation des contraintes entre toutes les paires de variables. L’objectif est de maintenir un réseau de contraintes globalement cohérent en raffinant progressivement les relations possibles entre régions jusqu’à atteindre un point fixe. À chaque itération, le solveur réduit l’ensemble des relations entre deux régions en fonction de la composition RCC8 via une troisième région intermédiaire, ce qui permet de propager indirectement les contraintes dans tout le graphe.

Contrairement à une approche locale, qui ne considère que des vérifications directes entre paires de régions, l’approche globale adoptée ici garantit la cohérence structurelle de l’ensemble du réseau. Une incohérence peut en effet n’apparaître qu’après plusieurs étapes de propagation (effet de chaîne), ce qui justifie l’utilisation d’un raisonnement global plutôt que pairwise. Le choix de PC-2 plutôt que PC-3 est motivé par un compromis entre expressivité et coût calculatoire : PC-2, basé sur des triplets (i, j, k), suffit à assurer la cohérence path-consistante dans RCC8 tout en restant polynomial en O(n³), tandis que PC-3, qui étend la propagation aux quadruplets, améliore la précision mais augmente fortement la complexité sans être requis dans un cadre standard de vérification ou de planification spatiale.

Ainsi, le solveur garantit à la fois la détection d’incohérences structurelles et la convergence vers un réseau stable de contraintes, ce qui le rend adapté à des applications de vérification de descriptions spatiales ou de planification robotique à petite et moyenne échelle.



# RCC8 Spatial Reasoning Solver (PC-2)

## Overview

This project implements a qualitative spatial reasoning system based on the **Region Connection Calculus (RCC8)**. RCC8 defines eight base relations between spatial regions:

- DC (Disconnected)
- EC (Externally Connected)
- PO (Partially Overlapping)
- TPP (Tangential Proper Part)
- NTPP (Non-Tangential Proper Part)
- TPPI (inverse of TPP)
- NTPPI (inverse of NTPP)
- EQ (Equal)

The goal of the solver is to propagate spatial constraints, infer implicit relations, and detect inconsistencies in spatial configurations.

---

## Path Consistency (Core Concept)

The solver is based on **path consistency**, a fundamental property in binary constraint networks.

A network is path-consistent if, for any three variables \(X, Y, Z\), the direct relation between \(X\) and \(Z\) is compatible with the composition of relations through \(Y\):

$$
R(X,Z) \subseteq R(X,Y) \circ R(Y,Z)
$$

### Intuition

If:
- X is related to Y
- Y is related to Z

Then the relation between X and Z must be consistent with what is implied through Y.

This prevents hidden contradictions that are not visible at the pairwise level.

---

## Why Path Consistency is needed

In RCC8 reasoning:

- relations are symbolic (not numeric)
- constraints interact transitively
- inconsistencies can appear only through intermediate regions

Without path consistency:
- local constraints may seem valid
- but global contradictions can remain undetected

Path consistency ensures **global coherence** of the spatial network.

---

## PC-2 Algorithm

This solver uses **PC-2 (Path Consistency algorithm)**, which enforces path consistency over all triples of variables.

### Principle

For every triple \((i, j, k)\):

1. Compute composition:
   $$
   R(i,j) \circ R(j,k)
   $$

2. Refine constraint:
   $$
   R(i,k) \leftarrow R(i,k) \cap (R(i,j) \circ R(j,k))
   $$

3. Repeat until no changes occur (fixed point)

---

## Why PC-2

PC-2 is used because:

- It ensures full path consistency
- It works on triples of variables
- It is sufficient for RCC8 reasoning
- It has polynomial complexity: **O(n³)**

### Comparison

| Algorithm | Scope | Complexity | Use |
|----------|------|------------|-----|
| AC-3 | Pairwise consistency | O(e³) | CSP basics |
| PC-2 | Triplet consistency | O(n³) | RCC8 reasoning |
| PC-3 | Quadruplets | O(n⁴) | advanced research |

---

## Complexity

- Time complexity: **O(n³)** (triples of variables)
- Space complexity: **O(n²)** (relation matrix)

---

## Applications

This solver can be used for:

- Spatial description verification (natural language interpretation)
- Robot navigation and spatial planning
- Consistency checking in GIS systems
- Qualitative spatial reasoning tasks

---

## Key Features

- RCC8 relation algebra implementation
- Composition table-based reasoning
- Global propagation of constraints
- Detection of hidden inconsistencies
- Convergence to a stable constraint network

---

## Conclusion

This system implements a **PC-2-based RCC8 reasoner** ensuring that spatial constraints are globally consistent. It propagates relational information across all regions until a fixed point is reached, enabling robust detection of inconsistencies in qualitative spatial descriptions.



# Notebooks

## 1) 01_relations.ipynb

    Présentation :

    RCC8

    signification géométrique

    exemples visuels

    afficher des cercles avec matplotlib.
---
## 2) 02_composition_table.ipynb

    Montrer :

    R(A,B) ∘ R(B,C)

    Visualiser la table RCC8.


## 3) 03_constraint_propagation.ipynb

    propagation étape par étape,
    réduction des domaines,
    fermeture transitive.

## 4) 04_inconsistency_detection.ipynb

    Tu montres des contradictions.

## 5) 05_robot_planning.ipynb

    Très bon pour impressionner.

    Exemple :

    zones interdites,
    objectif,
    obstacles,
    contraintes spatiales.


## 5) 06_scalability.ipynb

    Benchmarks.

    Tu génères :

    10 régions
    100 régions
    1000 régions

    Puis tu mesures :

    temps propagation,
    mémoire,
    densité du graphe.






















### Notebooks CoursIA pertinents

| Notebook | Chemin | Pertinence |
|----------|--------|------------|
| CSP-8 Temporal CSP | [Search/Part2-CSP/CSP-8-TemporalCSP.ipynb](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/Search/Part2-CSP/CSP-8-TemporalCSP.ipynb) | CSP qualitatifs, propagation de contraintes |
| Search-10 Automates | [Search/Part1-Foundations/Search-10-AutomatesSymboliques.ipynb](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/Search/Part1-Foundations/Search-10-AutomatesSymboliques.ipynb) | Automates symboliques, raisonnement formel |
| CSP-3 Global Constraints | [Search/Part2-CSP/CSP-3-GlobalConstraints.ipynb](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/Search/Part2-CSP/CSP-3-GlobalConstraints.ipynb) | Contraintes globales, tables de compatibilite |
| CSP-1 Fundamentals | [Search/Part2-CSP/CSP-1-Fundamentals.ipynb](https://github.com/jsboige/CoursIA/blob/main/MyIA.AI.Notebooks/Search/Part2-CSP/CSP-1-Fundamentals.ipynb) | Modelisation CSP, propagation |

### References externes
- Randell, D.A. et al. (1992). "A Spatial Logic Based on Regions and Connection." *KR 1992*. [KR](https://kr.org/KR92/)
- Renz, J. & Nebel, B. (2004). "Qualitative Spatial Reasoning with Constraint Calculi." *Handbook of Spatial Logics*. [Springer](https://link.springer.com/chapter/10.1007/978-3-540-74761-1_4)
- Cohn, A.G. & Renz, J. (2008). "Qualitative Spatial Reasoning." *Handbook of Knowledge Representation*. [Elsevier](https://www.sciencedirect.com/science/article/pii/S1574652607030079)
- Ligozat, G. (2011). *Qualitative Spatial and Temporal Reasoning*. ISTE/Wiley. [Wiley](https://www.wiley.com/en-us/Qualitative+Spatial+and+Temporal+Reasoning-9781848212527)

### Difficulte : 3/5

---

### References externes supplémentaires

- https://en.wikipedia.org/wiki/Region_connection_calculus
- https://univ-cotedazur.hal.science/hal-02271390v1/file/JFPC-CRIL.pdf