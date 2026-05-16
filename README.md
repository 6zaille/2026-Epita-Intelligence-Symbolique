# EPITA 2026 — Intelligence Symbolique

## Liste des sujets de projet

Ce document presente les sujets de projet pour le cours d'Intelligence Symbolique (SCIA). Chaque sujet inclut une description detaillee, des references academiques et pratiques, des liens vers les notebooks CoursIA pertinents, et les technologies a utiliser.

> **Consignes de choix** : Chaque groupe doit forker ce depot et creer un dossier pour son projet contenant le code source, un notebook explicatif OU une UI/demo fonctionnelle (au choix), et les slides de soutenance. Les livraisons se font via des pull requests regulieres.

### Du cours de Programmation par Contraintes a l'Intelligence Symbolique

Ce cours d'Intelligence Symbolique **ne prolonge pas** le cours de Programmation par Contraintes. Il ouvre un espace conceptuel different :

| Aspect | Programmation par Contraintes | Intelligence Symbolique |
|--------|-------------------------------|------------------------|
| **Questions** | Comment resoudre un probleme combinatoire ? | Comment representer et raisonner sur des connaissances ? |
| **Paradigme** | Espaces de recherche, propagation, optimisation | Logiques, argumentation, ontologies, preuves formelles |
| **Solveur** | CP-SAT, SAT, SMT comme boites noires | Z3/Lean comme assistants de raisonnement |
| **Sortie** | Une solution optimale ou faisable | Une preuve, un argument, une ontologie, un plan |
| **Evaluation** | Performance (temps, optimalite) | Correction (validite logique, coherence) |

Les solveurs SAT/SMT (Z3, PySAT) apparaissent dans les deux cours, mais avec des usages differents : en PC, ce sont des moteurs d'optimisation ; en IS, ce sont des verificateurs de proprietes logiques, des outils de preuve, ou des backend pour le raisonnement formel. Les sujets de ce depot exploitent SAT/SMT comme couches de verification au service de taches symboliques de plus haut niveau (demonstration automatique, model checking, verification de smart contracts, encodage de theoremes d'impossibilite).

---

## Modalites du projet

### Taille des groupes

| Taille | Bonus/Malus |
|--------|-------------|
| 3 personnes | Standard |
| 2 personnes | +1 point |
| 1 personne (solo) | +3 points |
| 4 personnes | -1 point |

### Soutenance — Evaluation collegiale

La soutenance finale est evaluee de maniere **collegiale** (pairs + enseignants). Chaque groupe est note sur **4 criteres** (0-10 chacun) :

| Critere | Description |
|---------|-------------|
| **Qualite de la presentation** | Communication, clarte, pedagogie, qualite des slides, demonstrations |
| **Qualite theorique** | Principes utilises, classes d'algorithmes, contexte historique, explication des performances et limitations |
| **Qualite technique** | Livrables (code, notebook, UI), qualite du code, commits Git, demonstrations, resultats, perspectives |
| **Organisation** | Planning, repartition des taches, collaboration, activite Git, documentation |

**Note finale = somme des 4 criteres / 2 (echelle /20), ajustee du bonus/malus taille de groupe.**

### Livrables attendus

- **Code source** documente dans un sous-dossier dedie (`groupe-XX-nom-sujet/`)
- **Notebook Jupyter** explicatif avec analyse et visualisations **OU** **UI/demo fonctionnelle** (au choix — un notebook tres complet peut tenir lieu de demo, et inversement)
- **Slides de soutenance** (PDF ou lien)
- **Pull Request** soumise au plus tard **2 jours avant la soutenance**

### Echeances

- **Date de soutenance** : en cours de confirmation avec la scolarite
- **Deadline PR** : 2 jours avant la soutenance

---

## Ressources communes a tous les sujets

### Solveurs et outils
- **Z3 SMT Solver** : solveur SMT de reference pour verification formelle et raisonnement symbolique. [Documentation](https://z3prover.github.io/api/html/namespacez3py.html), [Tutoriel Python](https://ericpony.github.io/z3py-tutorial/guide-examples.htm)
- **Google OR-Tools CP-SAT** : solveur CP pour problemes combinatoires. [Documentation](https://developers.google.com/optimization/cp/cp_solver)
- **CVC5 SMT Solver** : solveur SMT alternatif. [Documentation](https://cvc5.github.io/)
- **TweetyProject** : librairie Java pour logique formelle, argumentation et raisonnement probabiliste. [Documentation](https://tweetyproject.org/)

### Frameworks et plateformes
- **Semantic Kernel** : orchestration d'agents IA avec plugins. [GitHub](https://github.com/microsoft/semantic-kernel)
- **Fast Downward** : planificateur PDDL de reference. [Site](https://www.fast-downward.org/)
- **Solidity / Foundry** : developpement et test de smart contracts. [Documentation](https://docs.soliditylang.org/)
- **PySAT** : interface Python pour solveurs SAT. [Documentation](https://pysathq.github.io/)

### Notebooks du cours CoursIA
Les notebooks suivants sont disponibles dans le depot CoursIA ([jsboige/CoursIA](https://github.com/jsboige/CoursIA)) et constituent des prerequis ou des points de depart pour les projets :

#### Demonstration automatique et typage dependant (Lean 4)
- **SymbolicAI/Lean/** : 12 notebooks — Lean-1 (Setup), Lean-2 (Dependent Types), Lean-3 (Propositions & Proofs), Lean-4 (Quantifiers), Lean-5 (Tactics), Lean-6 (Mathlib), Lean-7 (LLM Integration), Lean-8 (Agentic Proving), Lean-9 (Semantic Kernel Multi-Agents), Lean-10 (LeanDojo), Lean-11 (Neural Theorem Proving)

#### Logique formelle, SAT/SMT et solveurs
- **SymbolicAI/Linq2Z3.ipynb** : Z3 SMT Solver en C#
- **SymbolicAI/OR-tools-Stiegler.ipynb** : OR-Tools CP en C#
- **Sudoku/** : 18 notebooks couvrant Sudoku avec multiples solveurs (backtracking, DLX, GA, SA, PSO, Norvig, OR-Tools, Choco, Z3, BDD, neural, LLM)

#### TweetyProject — Logique et Argumentation
- **SymbolicAI/Tweety/** : 11 notebooks — Tweety-1 (Setup), Tweety-2 (Basic Logics), Tweety-3 (Advanced Logics), Tweety-4 (Belief Revision/AGM), Tweety-5 (Abstract Argumentation/Dung), Tweety-6 (Structured Argumentation/ASPIC+), Tweety-7a (Extended Frameworks), Tweety-7b (Ranking & Probabilistic), Tweety-8 (Agent Dialogues), Tweety-9 (Preferences)

#### Web Semantique et Graphes de Connaissances
- **SymbolicAI/SemanticWeb/** : 13 notebooks — SW-1 (Setup C#/Python), SW-2 (RDF), SW-3 (Graph Operations), SW-4 (SPARQL), SW-5 (Linked Data), SW-6 (RDFS), SW-7 (OWL), SW-8 (SHACL), SW-9 (JSON-LD), SW-10 (RDF*), SW-11 (Knowledge Graphs), SW-12 (GraphRAG), SW-13 (Reasoners)

#### Smart Contracts et Blockchain
- **SymbolicAI/SmartContracts/** : 27 notebooks (SC-0 a SC-26) — cypherpunk, Solidity, Foundry, ERC-20/721, DeFi, DAO Governance, Account Abstraction, LLM-assisted contracts, fuzz testing (SC-13), formal verification (SC-14), ZKP (SC-15), homomorphic encryption (SC-16), voting, Vyper, Bitcoin Script, Move/Sui, Solana/Anchor, cross-chain, deployment

#### Analyse d'Argumentation (Agentic)
- **SymbolicAI/Argument_Analysis/** : 7 notebooks — Agentic-0 (Init), Agentic-1 (Informal Argument Agent), Agentic-2 (Planning-Based Agent), Agentic-3 (Orchestration multi-agent)

#### Planification
- **SymbolicAI/Planners/** : 12 notebooks — Planners-1 (Intro), Planners-2 (PDDL), Planners-3 (State Space), Planners-4 (Fast Downward), Planners-5 (Heuristics), Planners-6 (Domains), Planners-7 (OR-Tools), Planners-8 (Temporal), Planners-9 (HTN), Planners-10 (LLM Planning), Planners-11 (Unified Planning), Planners-12 (LOOP)

#### Theorie des Jeux et Choix Social
- **GameTheory/** : 27 notebooks — forme normale, equilibres de Nash, zero-sum/minimax, evolution & trust, forme extensive, jeux combinatoires, induction, jeux bayesiens, reputation, information imparfaite/CFR, jeux cooperatifs/Shapley, mechanism design, choix social (Arrow SAT/Z3), multi-agent RL

#### Recherche et Metaheuristiques
- **Search/Part1-Foundations/** : 11 notebooks — StateSpace, uninformed, A*/heuristiques, local search, GA, adversarial/minimax, MCTS, Dancing Links, PL, automates symboliques, metaheuristiques

#### Programmation par Contraintes
- **Search/Part2-CSP/** : 9 notebooks — CSP-1 (Fondamentaux), CSP-2 (Consistency), CSP-3 (Advanced), CSP-4 (Scheduling), CSP-5 (Optimization), CSP-6 (Hybridation CP+SAT, LLM+CSP), CSP-7 (Soft Constraints), CSP-8 (Temporal CSP), CSP-9 (Distributed CSP)
- **Search/Applications/CSP/** : 11 notebooks — N-Queens, Graph Coloring, Nurse Scheduling, Job-Shop, Timetabling, Minesweeper, Wordle, MiniZinc, Picross, Sports Scheduling, Crossword
- **Search/Applications/Hybrid/** : 7 notebooks — Edge Detection, Portfolio Optimization, Connect Four, TSP Metaheuristics, VRP Logistics

#### Raisonnement Probabiliste et Decision

- **Research/** : 20 notebooks — Infer.NET (programmation probabiliste), melanges gaussiens, graphes de facteurs, reseaux bayesiens, modeles de Markov caches, LDA, crowdsourcing, recommandation, reseaux de decision, MDP/bandits/POMDP, TrueSkill, IRT

#### Reinforcement Learning

- **RL/** : 6 notebooks — MDP, Q-learning, DQN, policy gradient, multi-agent RL (NFSP, PSRO), Stable Baselines3, Gym wrappers, HER

---

## Index des Sujets

### Categorie A : Demonstration Automatique et Typage Dependant (Lean 4)

| # | Sujet | Difficulte |
|---|-------|------------|
| [A1](#a1---preuve-formelle-dalgorithme-par-lean-4) | Preuve formelle d'algorithme par Lean 4 | 3/5 |
| [A2](#a2---agent-llm-assiste-pour-la-preuve-formelle) | Agent LLM-assiste pour la preuve formelle | 4/5 |
| [A3](#a3---theoreme-darrow-par-preuve-automatisee-satz3lean) | Theoreme d'Arrow par preuve automatisee (SAT/Z3/Lean) | 4/5 |
| [A4](#a4---bibliotheque-de-preuves-mathlib-extensions) | Bibliotheque de preuves Mathlib — extensions | 3/5 |

### Categorie B : Logique Formelle, SAT et Demonstration Automatique

| # | Sujet | Difficulte |
|---|-------|------------|
| [B1](#b1---resolution-automatique-de-theoremes-par-sat) | Resolution automatique de theoremes par SAT | 3/5 |
| [B2](#b2---synthese-de-programmes-par-programming-by-sketching) | Synthese de programmes par Programming-by-Sketching | 4/5 |
| [B3](#b3---model-checking-de-protocoles-de-communication) | Model checking de protocoles de communication | 3/5 |
| [B4](#b4---resolution-de-puzzles-logiques-par-smt) | Resolution de puzzles logiques par SMT | 2/5 |
| [B5](#b5---demonstration-automatique-en-geometrie) | Demonstration automatique en geometrie | 4/5 |
| [B6](#b6---programmation-par-ensembles-de-reponses-asp-avec-clingo) | Programmation par ensembles de reponses (ASP) avec Clingo | 3/5 |
| [B7](#b7---resolution-de-problemes-pspace-par-qbf-quantified-booleans) | Resolution de problemes PSPACE par QBF (Quantified Booleans) | 3/5 |

### Categorie C : Verification Formelle et Surete des Logiciels

| # | Sujet | Difficulte |
|---|-------|------------|
| [B1](#b1---verification-formelle-de-smart-contracts-solidity-par-smt) | Verification formelle de smart contracts Solidity par SMT | 3/5 |
| [B2](#b2---fuzzing-guide-par-contraintes-constraint-based-fuzzing) | Fuzzing guide par contraintes (constraint-based fuzzing) | 4/5 |
| [B3](#b3---analyse-statique-et-detection-de-vulnerabilites-par-abstraction) | Analyse statique et detection de vulnerabilites par abstraction | 3/5 |
| [B4](#b4---preuves-de-correcteur-zero-knowledge-zk-snarks) | Preuves de correcteur Zero-Knowledge (zk-SNARKs) | 4/5 |

### Categorie D : Planification et Ordonnancement

| # | Sujet | Difficulte |
|---|-------|------------|
| [C1](#c1---planification-robotique-avec-pddl-et-integration-capteurs) | Planification robotique avec PDDL et integration capteurs | 3/5 |
| [C2](#c2---planification-htn-pour-jeux-video) | Planification HTN pour jeux video | 3/5 |
| [C3](#c3---ordonnancement-multi-agent-par-csp-distribue) | Ordonnancement multi-agent par CSP distribue | 4/5 |
| [C4](#c4---planification-temporelle-pour-systemes-cyber-physiques) | Planification temporelle pour systemes cyber-physiques | 4/5 |

### Categorie E : Theorie des Jeux et Mechanism Design

| # | Sujet | Difficulte |
|---|-------|------------|
| [D1](#d1---comptabilite-maximin-et-equilibres-de-nash-par-programmation-lineaire) | Comptabilite maximin et equilibres de Nash par programmation lineaire | 3/5 |
| [D2](#d2---encheres-combinatoires-et-allocation-de-biens-publics) | Encheres combinatoires et allocation de biens publics | 4/5 |
| [D3](#d3---jeux-cooperatifs-et-valeur-de-shapley) | Jeux cooperatifs et valeur de Shapley | 3/5 |
| [D4](#d4---conception-de-mecanismes-resistants-a-la-manipulation) | Conception de mecanismes resistants a la manipulation | 4/5 |

### Categorie F : Smart Contracts et Blockchain Symbolique

| # | Sujet | Difficulte |
|---|-------|------------|
| [E1](#e1---super-optimisation-de-gas-solidity-par-max-smt) | Super-optimisation de gas Solidity par Max-SMT | 4/5 |
| [E2](#e2---ordonnancement-mev-resistant-de-transactions-on-chain) | Ordonnancement MEV-resistant de transactions on-chain | 3/5 |
| [E3](#e3---circuits-zero-knowledge-sous-contraintes-arithmetiques) | Circuits Zero-Knowledge sous contraintes arithmetiques | 4/5 |
| [E4](#e4---governance-decentralisee-et-vote-quadratique) | Governance decentralisee et vote quadratique | 3/5 |
| [E5](#e5---choix-social-computationnel-simulation-et-manipulation-electorale) | Choix social computationnel — simulation et manipulation electorale | 3/5 |
| [E6](#e6---jeux-combinatoires-et-theorie-de-sprague-grundy) | Jeux combinatoires et theorie de Sprague-Grundy | 3/5 |

### Categorie G : Web Semantique et Graphes de Connaissances

| # | Sujet | Difficulte |
|---|-------|------------|
| [G1](#g1---construction-et-interrogation-dun-graphe-de-connaissances-par-sparql) | Construction et interrogation d'un graphe de connaissances par SPARQL | 3/5 |
| [G2](#g2---raisonnement-owl-et-verification-de-coherence-dontologie) | Raisonnement OWL et verification de coherence d'ontologie | 3/5 |
| [G3](#g3---graphrag-combine-knowledge-graphs-et-llm-pour-le-rag) | GraphRAG — combine Knowledge Graphs et LLM pour le RAG | 4/5 |
| [G4](#g4---validation-de-donnees-par-shacl-shapes-constraint-language) | Validation de donnees par SHACL (Shapes Constraint Language) | 3/5 |

### Categorie H : Representation des Connaissances et Raisonnement

| # | Sujet | Difficulte |
|---|-------|------------|
| [F1](#f1---systeme-de-maintenance-de-verite-jtms) | Systeme de maintenance de verite (JTMS) | 3/5 |
| [F2](#f2---ontologies-et-raisonnement-semantique-owl-reasoning) | Ontologies et raisonnement semantique (OWL Reasoning) | 3/5 |
| [F3](#f3---graphes de-connaissances-et-reponse-a-des-questions) | Graphes de connaissances et reponse a des questions | 3/5 |
| [F4](#f4---logique-description-et-raisonnement-sur-des-domaines-medicaux) | Logique de description et raisonnement sur des domaines medicaux | 4/5 |

### Categorie I : Argumentation et Raisonnement Debateur

| # | Sujet | Difficulte |
|---|-------|------------|
| [G1](#g1---analyse-et-detection-de-sophismes-par-apprentissage-symbolique) | Analyse et detection de sophismes par apprentissage symbolique | 3/5 |
| [G2](#g2---generation-de-contre-arguments-par-raisonnement-formel) | Generation de contre-arguments par raisonnement formel | 3/5 |
| [G3](#g3---argumentation-dialogique-multi-agents) | Argumentation dialogique multi-agents | 4/5 |
| [G4](#g4---evaluation-automatique-de-la-qualite-argumentative) | Evaluation automatique de la qualite argumentative | 3/5 |
| [I5](#i5---benchmarks-iccma-solveurs-dargumentation-de-dung) | Benchmarks ICCMA — solveurs d'argumentation de Dung | 2/5 |
| [I6](#i6---argumentation-structuree-aspic--logique-defaisable-delpaba) | Argumentation structuree ASPIC+ et logique defaisable (DeLP/ABA) | 3/5 |

### Categorie J : Agents Symboliques et Architecture Cognitive

| # | Sujet | Difficulte |
|---|-------|------------|
| [H1](#h1---systeme-multi-agents-de-resolution-de-problemes-par-planification) | Systeme multi-agents de resolution de problemes par planification | 3/5 |
| [H2](#h2---agent-cognitif-hybride-symbolique--subsymbolique) | Agent cognitif hybride (symbolique + subsymbolique) | 4/5 |
| [H3](#h3---serveur-mcp-doutils-danalyse-symbolique) | Serveur MCP d'outils d'analyse symbolique | 3/5 |
| [H4](#h4---integration-llm--solveurs-symboliques-llm-as-a-reasoner) | Integration LLM + solveurs symboliques (LLM-as-a-reasoner) | 4/5 |

### Categorie K : Cryptographie Symbolique et Securite

| # | Sujet | Difficulte |
|---|-------|------------|
| [I1](#i1---cryptanalyse-par-contraintes-de-chiffrements-classiques) | Cryptanalyse par contraintes de chiffrements classiques | 3/5 |
| [I2](#i2---verication-de-protocoles-cryptographiques-par-model-checking) | Verification de protocoles cryptographiques par model checking | 4/5 |
| [I3](#i3---chiffrement-homomorphe-et-calcul-sur-donnees-chiffrees) | Chiffrement homomorphe et calcul sur donnees chiffrees | 4/5 |

### Categorie L : Puzzles, Jeux et Problemes Combinatoires

| # | Sujet | Difficulte |
|---|-------|------------|
| [J1](#j1---resolution-de-sudoku-par-multiples-solveurs-sat-cp-lll) | Resolution de Sudoku par multiples solveurs (SAT, CP, LLL) | 2/5 |
| [J2](#j2---generation-procedurale-par-contraintes-de-niveaux-de-jeu) | Generation procedurale par contraintes de niveaux de jeu | 3/5 |
| [J3](#j3---resolution-de-jeux-combinatoires-par-minimax-et-alpha-beta-symbolique) | Resolution de jeux combinatoires par minimax et alpha-beta symbolique | 3/5 |

---

### Categorie M : IA Neuro-Symbolique

> L'IA neuro-symbolique combine le raisonnement formel (logique, contraintes) avec l'apprentissage profond (LLM, reseaux de neurones). Domaine en pleine expansion avec des applications en raisonnement verifiable, generation guidee par contraintes, et interpretabilite.

| # | Sujet | Difficulte |
|---|-------|------------|
| [M1](#m1---pipeline-llm--verificateur-symbolique-pour-la-generation-fiable) | Pipeline LLM + verificateur symbolique pour la generation fiable | 3/5 |
| [M2](#m2---reseau-de-neurones-logique-logical-neural-networks) | Reseau de neurones logique (Logical Neural Networks) | 4/5 |
| [M3](#m3---regression-symbolique-decouvrir-des-equations-a-partir-de-donnees) | Regression symbolique -- decouvrir des equations a partir de donnees | 3/5 |
| [M4](#m4---decouverte-scientifique-automatisee-par-regression-symbolique-et-llm) | Decouverte scientifique automatisee par regression symbolique et LLM | 4/5 |
| [M5](#m5---evaluation-comparee-llm-vs-approches-symboliques-sur-un-benchmark) | Evaluation comparee LLM vs. approches symboliques sur un benchmark | 2/5 |

### Categorie N : Raisonnement Causal et Decision

> Le raisonnement causal (Pearl, 2009) depasse la correlation pour raisonner sur les interventions et les contrefactuels. Fondamental pour la prise de decision dans les systemes IA, la medecine, et l'analyse de politiques.

| # | Sujet | Difficulte |
|---|-------|------------|
| [N1](#n1---decouverte-causale-a-partir-de-donnees-observationnelles) | Decouverte causale a partir de donnees observationnelles | 3/5 |
| [N2](#n2---raisonnement-causal-par-le-do-calculus-avec-dowhy) | Raisonnement causal par le do-calculus avec DoWhy | 3/5 |
| [N3](#n3---diagnostic-abductif-raisonnement-par-abduction) | Diagnostic abductif — raisonnement par abduction | 3/5 |
| [N4](#n4---evaluation-du-raisonnement-causal-des-llm) | Evaluation du raisonnement causal des LLM | 4/5 |

### Categorie O : Raisonnement Qualitatif et Bon Sens

> Le raisonnement qualitatif manipule des representations symboliques de l'espace, du temps, et du bon sens sans recourir a des modeles numeriques. Inclut les calculs relationnels spatiaux (RCC8), temporels (Allen), et le raisonnement de sens commun.

| # | Sujet | Difficulte |
|---|-------|------------|
| [O1](#o1---raisonnement-spatial-qualitatif-par-les-calculs-rcc8) | Raisonnement spatial qualitatif par les calculs RCC8 | 3/5 |
| [O2](#o2---raisonnement-temporel-qualitatif-algebres-dallen-et-stp) | Raisonnement temporel qualitatif — Algebres d'Allen et STP | 3/5 |
| [O3](#o3---raisonnement-de-bon-sens-par-graphe-de-connaissances-commonsense) | Raisonnement de bon sens par graphe de connaissances (Commonsense) | 3/5 |
| [O4](#o4---raisonnement-par-analogie-theorie-du-mapping-structurel) | Raisonnement par analogie — theorie du mapping structurel | 3/5 |

### Categorie P : Verification Formelle des Systemes IA

> La verification formelle des systemes d'IA est un domaine emergent critique pour la surete. Il s'agit de prouver formellement qu'un systeme d'IA (reseau de neurones, agent LLM, politique RL) satisfait des proprietes de surete, equite, ou robustesse.

| # | Sujet | Difficulte |
|---|-------|------------|
| [P1](#p1---verification-de-robustesse-de-reseaux-de-neurones-par-abstraction) | Verification de robustesse de reseaux de neurones par abstraction | 4/5 |
| [P2](#p2---verification-de-politiques-rl-par-contraintes-formelles) | Verification de politiques RL par contraintes formelles | 4/5 |
| [P3](#p3---specification-et-verification-de-securite-dagents-llm-par-logique-temporelle) | Specification et verification de securite d'agents LLM par logique temporelle | 4/5 |

### Categorie Q : Raisonnement Ethique et Normatif

> Le raisonnement ethique et normatif utilise la logique deontique (obligations, permissions, interdictions) et les cadres d'argumentation pour raisonner formellement sur les normes, les valeurs, et l'alignement des systemes d'IA.

| # | Sujet | Difficulte |
|---|-------|------------|
| [Q1](#q1---raisonneur-deontique-logique-des-normes-et-obligations) | Raisonneur deontique — logique des normes et obligations | 3/5 |
| [Q2](#q2---verification-dalignement-de-valeurs-par-methodes-formelles) | Verification d'alignement de valeurs par methodes formelles | 4/5 |
| [Q3](#q3---raisonnement-juridique-formel-par-argumentation-et-logique) | Raisonnement juridique formel par argumentation et logique | 3/5 |

### Categorie R : Raisonnement sous Incertitude et Revision des Croyances

> La revision des croyances et le raisonnement sous incertitude sont au coeur des systemes symboliques devant mettre a jour leurs connaissances face a de nouvelles informations contradictoires. Inclut les postulats AGM, les croyances probabilistes, et la programmation probabiliste.

| # | Sujet | Difficulte |
|---|-------|------------|
| [R1](#r1---revision-des-croyances-par-les-postulats-agm) | Revision des croyances par les postulats AGM | 3/5 |
| [R2](#r2---programmation-probabiliste-avec-infernet) | Programmation probabiliste avec Infer.NET | 3/5 |
| [R3](#r3---raisonnement-epistemique-et-logique-multi-agents) | Raisonnement epistemique et logique multi-agents | 4/5 |

---

> **Note** : Les descriptions detaillees de chaque sujet, les references academiques et les notebooks CoursIA associes seront enrichis progressivement. Cette premiere version est un draft soumis pour revue et enrichissement par l'equipe pedagogique.

---

## Descriptions detaillees des sujets

### Categorie A : Demonstration Automatique et Typage Dependant (Lean 4)

#### A1 — Preuve formelle d'algorithme par Lean 4

**Description :** Prouver formellement la correction d'un algorithme classique (tri, recherche, plus court chemin) en Lean 4 avec Mathlib. Definir les types inductifs, les proprietes fonctionnelles, et mener la preuve en mode tactique.

**Notebooks CoursIA :** Lean-1 a Lean-6

**Technologies :** Lean 4, Mathlib4, VS Code + lean4 extension

**References :**
- Avigad, J. et al., *Theorem Proving in Lean 4*, 2024
- Mathlib Community, *The Mathematical Library of Lean 4*, [GitHub](https://github.com/leanprover-community/mathlib4)

**Difficulte :** 3/5

#### A2 — Agent LLM-assiste pour la preuve formelle

**Description :** Construire un agent qui utilise un LLM (via Semantic Kernel ou API) pour suggerer des tactiques de preuve en Lean 4, en s'appuyant sur LeanCopilot et LeanDojo. L'agent analyse l'etat de la preuve, genere des candidats tactiques, et les valide.

**Notebooks CoursIA :** Lean-7, Lean-8, Lean-9, Lean-10

**Technologies :** Lean 4, LeanCopilot, LeanDojo, Semantic Kernel, OpenAI API

**References :**
- Song, D. et al., *Lean Copilot: LLMs as Copilots for Theorem Proving in Lean*, NeuS 2025 (PMLR v288)
- Yang, K. & Deng, J., *LeanDojo: Theorem Proving with Retrieval-Augmented Language Models*, NeurIPS 2023

**Difficulte :** 4/5

#### A3 — Theoreme d'Arrow par preuve automatisee (SAT/Z3/Lean)

**Description :** Demontrer le theoreme d'impossibilite d'Arrow par trois approches : (1) encodage SAT avec PySAT, (2) raisonnement SMT avec Z3, (3) preuve formelle en Lean 4. Comparer les approches en termes de expressivite, performance, et confiance.

**Notebooks CoursIA :** GameTheory/16d, GameTheory/16e, GameTheory/16f, Lean-2b, Lean-15b

**Technologies :** PySAT, Z3, Lean 4, Nashpy

**References :**
- Arrow, K.J., *Social Choice and Individual Values*, 1951 (2nd ed. 1963)
- Geist, C. & Endriss, U., *Automated Search for Impossibility Theorems in Social Choice*, JAIR 2011
- Peters, D., *SocialChoiceLean*, [GitHub](https://github.com/dominikpeters/SocialChoiceLean)

**Difficulte :** 4/5

#### A4 — Bibliotheque de preuves Mathlib — extensions

**Description :** Contribuer a Mathlib4 en ajoutant des resultats absents (identites trigonometriques, lemmes combinatoires, proprietes de graphes). Suivre le processus de contribution (lint, CI, review). Decouvrir l'ecosysteme Mathlib.

**Notebooks CoursIA :** Lean-4, Lean-5, Lean-6

**Technologies :** Lean 4, Mathlib4, git, CI (Lake)

**References :**
- Mathlib Community, *Maintaining Mathlib*, [docs](https://leanprover-community.github.io/contribute/index.html)
- Lean 4 documentation, [https://lean-lang.org/](https://lean-lang.org/)

**Difficulte :** 3/5

---

### Categorie B : Logique Formelle, SAT et Demonstration Automatique

#### B1 — Resolution automatique de theoremes par SAT

**Description :** Encoder des problemes mathematiques (coloriage de graphes, pigeonhole, Ramsey) en SAT, resoudre avec PySAT/glucose/CaDiCaL, et interpreter les modeles. Etudier les transformations CNF (Tseitin) et les heuristiques de branchement.

**Notebooks CoursIA :** Search/CSP-6, SymbolicAI/Linq2Z3

**Technologies :** PySAT, Z3, networkx

**References :**
- Biere, A. et al., *Handbook of Satisfiability*, 2nd ed., IOS Press, 2021
- Gomes, C.P. et al., *Model Counting*, Handbook of SAT, 2021

**Difficulte :** 3/5

#### B2 — Synthese de programmes par Programming-by-Sketching

**Description :** Utiliser un solveur SMT (Z3 ou CVC5) pour synthetiser des programmes a partir d'une "esquisse" (squelette incomplet avec trous). Appliquer a des exemples concrets : tri, transformation de donnees, optimisation de boucles.

**Notebooks CoursIA :** SymbolicAI/Linq2Z3

**Technologies :** Z3, CVC5, Python

**References :**
- Solar-Lezama, A., *Program Synthesis by Sketching*, PhD Thesis, UC Berkeley, 2008
- Gulwani, S. et al., *Program Synthesis*, Foundations and Trends in Programming Languages, 2017

**Difficulte :** 4/5

#### B3 — Model checking de protocoles de communication

**Description :** Modeliser un protocole (exclusion mutuelle, consensus Paxos/Raft, poignee de main TCP) comme une machine a etats finis et verifier des proprietes de surete (LTL/CTL) par model checking. Utiliser NuSMV ou SPIN.

**Notebooks CoursIA :** Search/Search-10 (Automates symboliques)

**Technologies :** NuSMV, SPIN, Z3, Python

**References :**
- Baier, C. & Katoen, J.-P., *Principles of Model Checking*, MIT Press, 2008
- Clarke, E.M. et al., *Model Checking*, MIT Press, 2nd ed., 2018

**Difficulte :** 3/5

#### B4 — Resolution de puzzles logiques par SMT

**Description :** Modeliser et resoudre des puzzles logiques (Einstein/Zebra, Knights and Knaves, Nonograms/Picross) comme des problemes SMT. Comparer les encodages (entiers vs. booleens, contraintes globales) et les performances.

**Notebooks CoursIA :** Sudoku/ (18 solveurs), Search/App-11-Picross

**Technologies :** Z3, OR-Tools CP-SAT, PySAT

**References :**
- de Moura, L. & Bjorner, N., *Z3: An Efficient SMT Solver*, TACAS 2008
- Regin, J.-C., *A Filtering Algorithm for Constraints of Difference in CSPs*, AAAI 1994

**Difficulte :** 2/5

#### B5 — Demonstration automatique en geometrie

**Description :** Implementer un demonstrateur automatique en geometrie elementaire (theoreme de Thales, Pythagore, points cocycliques) en utilisant le calcul de Wu ou l'encodage SMT sur les coordonnees. Comparer avec les demonstrations par construction geometrique.

**Technologies :** Z3, SymPy, matplotlib (visualisation)

**References :**
- Wu, W.-T., *Mechanical Theorem Proving in Geometries*, Springer, 1994
- Chou, S.-C. et al., *Machine Proofs in Geometry*, World Scientific, 1994

**Difficulte :** 4/5

#### B6 — Programmation par ensembles de reponses (ASP) avec Clingo

**Description :** Decouvrir la programmation par ensembles de reponses (Answer Set Programming), un paradigme declaratif different de SAT/CSP. Modeliser des problemes combinatoires (scheduling, planning, graph coloring) en logique ASP avec Clingo, et comprendre les semantiques de modeles stables (Gelfond-Lifschitz). Comparer ASP avec les approches SAT et CP sur les memes problemes. L'ASP est particulierement adapte aux problemes avec raisonnement par defaut et exceptions.

**Notebooks CoursIA :** Tweety-6 (ASP avec Clingo), Search/CSP-1 (comparaison CSP)

**Technologies :** Clingo (Potassco), Python (API clingo), DLV2 (optionnel)

**References :**
- Gelfond, M. & Lifschitz, V., *The Stable Model Semantics for Logic Programming*, ICLP 1988
- Gebser, M. et al., *Answer Set Solving in Practice*, Springer, 2012
- Coppolillo, E. et al., *LLASP: Fine-tuning LLMs for Answer Set Programming*, KR 2024

**Difficulte :** 3/5

#### B7 — Resolution de problemes PSPACE par QBF (Quantified Booleans)

**Description :** Explorer les formules booleennes quantifiees (QBF — PSPACE-complet), qui etendent SAT avec des quantificateurs existentiels et universels. Utiliser PyQBF pour resoudre des problemes de verification, de jeux a deux joueurs, et de planning conformant. Comparer les solveurs QBF (DepQBF, CAQE, Qute) sur des benchmarks QBFLib.

**Notebooks CoursIA :** Tweety-3 (QBF), SymbolicAI/Linq2Z3

**Technologies :** PyQBF, DepQBF, CAQE, Python

**References :**
- Peyrer, M. et al., *PyQBF: A Python Framework for Solving QBF*, ACM TOCL, 2025
- Shukla, A. et al., *The QBF Gallery 2023*, arXiv, 2026
- Biere, A. et al., *Handbook of Satisfiability*, Chapter on QBF, 2021

**Difficulte :** 3/5

---

### Categorie C : Verification Formelle et Surete des Logiciels

#### C1 — Verification formelle de smart contracts Solidity par SMT

**Description :** Utiliser le model checker Solidity (SMTChecker integre au compilateur) et des outils externes (Mythril, Slither) pour verifier formellement des proprietes de surete sur des smart contracts (absence de reentrancy, overflow, access control).

**Notebooks CoursIA :** SmartContracts/SC-13 (Fuzz), SC-14 (Formal Verification)

**Technologies :** Solidity, Foundry, solc SMTChecker, Z3

**References :**
- Hajdu, A. & Jovanovic, D., *SMT-Friendly Formalization of the Solidity Memory Model*, ESOP 2020
- Feist, J. et al., *Slither: A Static Analysis Framework for Smart Contracts*, IEEE S&B Workshop, 2019

**Difficulte :** 3/5

#### C2 — Fuzzing guide par contraintes (constraint-based fuzzing)

**Description :** Implementer un fuzzer symbolique qui utilise Z3 pour generer des entrees couvrant de nouveaux chemins d'execution dans un programme C ou Solidity. Comparer avec le fuzzing aleatoire (AFL) sur des benchmarks.

**Notebooks CoursIA :** SmartContracts/SC-13

**Technologies :** Z3, Foundry (Echidna), Angr (binary), Python

**References :**
- Stephens, N. et al., *Driller: Augmenting Fuzzing Through Selective Symbolic Execution*, NDSS 2016
- Bosman, E. et al., *Firmalice - Automatic Detection of Authentication Bypass Vulnerabilities*, USENIX 2015

**Difficulte :** 4/5

#### C3 — Analyse statique et detection de vulnerabilites par abstraction

**Description :** Implementer une analyse statique par interpretation abstraite (domaine des intervalles, signes, congruences) pour detecter des vulnerabilites dans du code source. Construire un treillis de domaine abstrait et calculer des points fixes.

**Technologies :** Python, Z3 (pour les contrexemples)

**References :**
- Cousot, P. & Cousot, R., *Abstract Interpretation: A Unified Lattice Model*, POPL 1977
- Miné, A., *Abstract Domains for the Analysis of C Programs*, 2004

**Difficulte :** 3/5

#### C4 — Preuves de correcteur Zero-Knowledge (zk-SNARKs)

**Description :** Etudier et implementer un circuit Zero-Knowledge simple (range proof, membership proof) avec Circom/SnarkJS ou un framework equivalent. Prouver la correction du circuit et verifier les preuves.

**Notebooks CoursIA :** SmartContracts/SC-15 (ZKP), SC-16 (HE)

**Technologies :** Circom, SnarkJS, Solidity, Python

**References :**
- Ben-Sasson, E. et al., *Scalable Zero Knowledge with No Trusted Setup*, CRYPTO 2019
- Gabizon, A. et al., *PLONK: Permutations over Lagrange-Bases*, ePrint 2019

**Difficulte :** 4/5

---

### Categorie D : Planification et Ordonnancement

#### D1 — Planification robotique avec PDDL et integration capteurs

**Description :** Modeliser un domaine de planification robotique (navigation en entrepot, manipulation d'objets) en PDDL, utiliser Fast Downward pour generer des plans, et simuler l'execution avec integration de capteurs (mise a jour de l'etat).

**Notebooks CoursIA :** Planners-1 a Planners-6

**Technologies :** PDDL, Fast Downward, Python (simulateur)

**References :**
- Helmert, M., *The Fast Downward Planning System*, JAIR 2006
- Fox, M. & Long, D., *PDDL2.1: An Extension to PDDL for Expressing Temporal Planning Domains*, JAIR 2003

**Difficulte :** 3/5

#### D2 — Planification HTN pour jeux video

**Description :** Implementer un planificateur HTN (Hierarchical Task Network) pour controler le comportement de PNJ dans un jeu video (quete, crafting, exploration). Comparer avec une approche GOAP (Goal-Oriented Action Planning).

**Notebooks CoursIA :** Planners-9 (HTN)

**Technologies :** Python, PDDL/HDDL, Unity (optionnel pour la demo)

**References :**
- Erol, K. et al., *Complexity of HTN Planning*, JAIR 1994
- Orkin, J., *Applying Goal-Oriented Action Planning to Games*, AI Game Programming Wisdom 2, 2004

**Difficulte :** 3/5

#### D3 — Ordonnancement multi-agent par CSP distribue

**Description :** Modeliser un probleme d'ordonnancement multi-agent (ex: fleet de drones, robots collaboratifs) comme un CSP distribue. Implementer un protocole ABT (Asynchronous Backtracking) ou AWC et etudier la convergence et la scalabilite.

**Notebooks CoursIA :** CSP-9 (Distributed CSP)

**Technologies :** Python (asyncio/multiprocessing), OR-Tools

**References :**
- Yokoo, M. et al., *The Distributed Constraint Satisfaction Problem*, IEEE TKDE 1998
- Petcu, A. & Faltings, B., *DPOP: A Scalable Method for Multiagent Constraint Optimization*, IJCAI 2005

**Difficulte :** 4/5

#### D4 — Planification temporelle pour systemes cyber-physiques

**Description :** Modeliser un systeme cyber-physique (gestion d'energie, controle de trafic) avec PDDL 2.1 (durées, continu) et resoudre avec un planificateur temporel. Integrer des contraintes de ressources et des fenetres temporelles.

**Notebooks CoursIA :** Planners-8 (Temporal), CSP-8 (Temporal CSP)

**Technologies :** PDDL 2.1, Fast Downward (temporal), OR-Tools

**References :**
- Fox, M. & Long, D., *PDDL2.1: An Extension to PDDL for Expressing Temporal Planning Domains*, JAIR 2003
- Cesta, A. et al., *Planning and Scheduling: The State of the Art*, 2022

**Difficulte :** 4/5

---

### Categorie E : Theorie des Jeux et Mechanism Design

#### E1 — Comptabilite maximin et equilibres de Nash par programmation lineaire

**Description :** Implementer le calcul des equilibres de Nash en strategies mixtes pour des jeux bi-matrice par programmation lineaire (Lemke-Howson). Etudier le theoreme minimax et les rapports primal-dual.

**Notebooks CoursIA :** GameTheory/4, GameTheory/5, GameTheory/4c

**Technologies :** Nashpy, PuLP, scipy

**References :**
- Nash, J., *Non-Cooperative Games*, Annals of Mathematics, 1951
- Lemke, C.E. & Howson, J.T., *Equilibrium Points of Bimatrix Games*, SIAM Journal, 1964

**Difficulte :** 3/5

#### E2 — Encheres combinatoires et allocation de biens publics

**Description :** Implementer un mecanisme d'encheres combinatoires (VCG — Vickrey-Clarke-Groves) avec determination du gagnant par programmation par contraintes. Etudier les proprietes d'incitations veridiques et d'efficacite allocative.

**Notebooks CoursIA :** GameTheory/16 (Mechanism Design)

**Technologies :** OR-Tools CP-SAT, Python

**References :**
- Vickrey, W., *Counterspeculation, Auctions, and Competitive Sealed Tenders*, Journal of Finance, 1961
- Cramton, P. et al., *Combinatorial Auctions*, MIT Press, 2006

**Difficulte :** 4/5

#### E3 — Jeux cooperatifs et valeur de Shapley

**Description :** Implementer le calcul de la valeur de Shapley pour des jeux cooperatifs. Appliquer a l'allocation de gains dans des coalitions (logistique, partage de couts d'infrastructure). Verifier les axiomes formellement.

**Notebooks CoursIA :** GameTheory/15, GameTheory/15b (Lean)

**Technologies :** Python, Lean 4 (optionnel)

**References :**
- Shapley, L.S., *A Value for n-Person Games*, Contributions to the Theory of Games, 1953
- Roth, A.E., *The Shapley Value: Essays in Honor of Lloyd S. Shapley*, Cambridge, 1988

**Difficulte :** 3/5

#### E4 — Conception de mecanismes resistants a la manipulation

**Description :** Etudier et implementer des mecanismes d'allocation resistants a la manipulation strategique. Prouver formellement les proprietes (veracite, optimalite de Pareto) par encodage SAT ou Lean 4.

**Notebooks CoursIA :** GameTheory/16, GameTheory/16b-f (Social Choice)

**Technologies :** Z3, Lean 4, Python

**References :**
- Nisan, N. et al., *Algorithmic Game Theory*, Cambridge, 2007
- Gibbard, A., *Manipulation of Voting Schemes: A General Result*, Econometrica, 1973

**Difficulte :** 4/5

---

### Categorie F : Smart Contracts et Blockchain Symbolique

#### F1 — Super-optimisation de gas Solidity par Max-SMT

**Description :** Modeliser la super-optimisation de sequences d'instructions Solidity comme un probleme Max-SMT : minimiser le gas tout en preservant la semantique. Utiliser Z3 avec des fonctions de cout.

**Notebooks CoursIA :** SmartContracts/SC-14

**Technologies :** Z3, Solidity, Foundry

**References :**
- Gast, D., *The Syntectic Framework for Smart Contract Super-Optimization*, 2021

**Difficulte :** 4/5

#### F2 — Ordonnancement MEV-resistant de transactions on-chain

**Description :** Modeliser le probleme d'ordonnancement de transactions (MEV — Maximal Extractable Value) comme un probleme d'optimisation sous contraintes. Proposer un mecanisme d'enchere ou de commit-reveal resistant a l'extraction.

**Notebooks CoursIA :** SmartContracts/SC-5 a SC-8 (DeFi)

**Technologies :** Solidity, Foundry, OR-Tools

**References :**
- Daian, P. et al., *Flash Boys 2.0: Frontrunning in Decentralized Exchanges*, IEEE S&P 2020
- Flashbots Research, [https://writings.flashbots.net/](https://writings.flashbots.net/)

**Difficulte :** 3/5

#### F3 — Circuits Zero-Knowledge sous contraintes arithmetiques

**Description :** Implementer des circuits ZK pour des preuves arithmetiques (range proofs, preuve de solvabilite) en R1CS ou Plonk. Optimiser le nombre de contraintes et etudier les compromis preuve-taille vs. temps de verification.

**Notebooks CoursIA :** SmartContracts/SC-15

**Technologies :** Circom, SnarkJS, Solidity

**References :**
- Ben-Sasson, E. et al., *SNARKs for C*, CRYPTO 2013
- Thaler, J., *Proofs, Arguments, and Zero-Knowledge*, 2022, [online](https://people.cs.georgetown.edu/jthaler/ProofsArgsAndZK.html)

**Difficulte :** 4/5

#### F4 — Governance decentralisee et vote quadratique

**Description :** Implementer un systeme de gouvernance DAO avec vote quadratique et allocation de credits de vote. Formaliser les proprietes du mecanisme (resistance a l'influence Sybil) et les verifier.

**Notebooks CoursIA :** SmartContracts/SC-9 (DAO), GameTheory/16c-d (Social Choice)

**Technologies :** Solidity, Foundry, GameTheory/Math

**References :**
- Lalley, S.P. & Weyl, E.G., *Quadratic Voting: How Mechanism Design Can Radicalize Democracy*, AEA Papers, 2018
- Buterin, V. et al., *Liberal Radicalism*, 2019

**Difficulte :** 3/5

#### E5 — Choix social computationnel — simulation et manipulation electorale

**Description :** Implementer un simulateur electoral avec plusieurs regles de vote (Pluralite, Borda, STV, Schulze, Condorcet, Copeland) en utilisant pref_voting. Analyser la susceptibilite a la manipulation strategique : une coalition peut-elle changer le resultat en mentant ? Visualiser les paradoxes de Condorcet et les manifestations du theoreme d'Arrow. Utiliser des donnees reelles de PrefLib.

**Notebooks CoursIA :** GameTheory/16b-f (Social Choice Lean/SAT/Z3), Tweety-9 (Preferences)

**Technologies :** pref_voting (Python), abcvoting, PrefLib, Z3

**References :**
- Brandt, F. et al., *Handbook of Computational Social Choice*, Cambridge, 2016
- COMSOC 2025, *10th Workshop on Computational Social Choice*, TU Wien
- Brederock, R. et al., *Computational Social Choice: Parameterized Complexity*, arXiv, 2025

**Difficulte :** 3/5

#### E6 — Jeux combinatoires et theorie de Sprague-Grundy

**Description :** Implementer un moteur de calcul des valeurs de Grundy (nimbers) pour des jeux combinatoires impartiaux (Nim, Dawson's Chess, Staircase Nim). Detecter les periodicites dans les sequences de Grundy. Connecter au formalisme PGame de Mathlib en Lean 4 pour la verification formelle. Comparer avec l'approche alpha-beta sur les memes jeux.

**Notebooks CoursIA :** GameTheory/8/8b/8c (Combinatorial Games, Lean-PGame)

**Technologies :** Python, Lean 4 (PGame), numpy

**References :**
- Sprague, R., *Uber mathematische Kampfspiele*, Tohoku Mathematical Journal, 1935
- Grundy, P.M., *Mathematics and Games*, Eureka, 1939
- Siegel, A.N., *Combinatorial Game Theory*, AMS, 2013

**Difficulte :** 3/5

---

### Categorie G : Web Semantique et Graphes de Connaissances

#### G1 — Construction et interrogation d'un graphe de connaissances par SPARQL

**Description :** Construire un graphe de connaissances (KG) sur un domaine choisi (films, sciences, jeux video) avec RDF, l'interroger avec SPARQL, et connecter a des sources Linked Data (DBpedia, Wikidata). Comparer les requetes federated vs. locales.

**Notebooks CoursIA :** SW-1 a SW-6

**Technologies :** rdflib (Python), dotNetRDF (C#), SPARQL, Apache Jena

**References :**
- Heath, T. & Bizer, C., *Linked Data: Evolving the Web into a Global Data Space*, Morgan & Claypool, 2011
- DBpedia, [https://dbpedia.org/](https://dbpedia.org/)

**Difficulte :** 3/5

#### G2 — Raisonnement OWL et verification de coherence d'ontologie

**Description :** Definir une ontologie OWL 2 sur un domaine (bio-informatique, IoT, musique), utiliser un reasoner (HermiT, Pellet) pour inferrer des connaissances implicites et detecter des incoherences. Etudier les profils OWL (EL, QL, RL).

**Notebooks CoursIA :** SW-7 (OWL), SW-13 (Reasoners)

**Technologies :** Owlready2, Apache Jena, Protégé

**References :**
- Hitzler, P. et al., *OWL 2 Web Ontology Language Primer*, W3C, 2012
- Horrocks, I. et al., *From SHIQ and RDF to OWL*, Journal of Web Semantics, 2003

**Difficulte :** 3/5

#### G3 — GraphRAG — combine Knowledge Graphs et LLM pour le RAG

**Description :** Implementer un systeme GraphRAG qui combine un graphe de connaissances avec un LLM pour le Retrieval-Augmented Generation. Comparer les performances avec un RAG vectoriel classique sur un jeu de donnees de reference.

**Notebooks CoursIA :** SW-11 (KG), SW-12 (GraphRAG)

**Technologies :** rdflib, Neo4j, LangChain, OpenAI API, kglab

**References :**
- Edge, D. et al., *From Local to Global: A Graph RAG Approach to Query-Focused Summarization*, Microsoft Research, 2024
- Wu, L. et al., *Neural-Symbolic Reasoning over Knowledge Graphs*, ACM 2025

**Difficulte :** 4/5

#### G4 — Validation de donnees par SHACL (Shapes Constraint Language)

**Description :** Definir des contraintes SHACL pour valider des donnees RDF (conformite de schema, contraintes de cardinalite, regles metier). Appliquer a la validation de donnees ouvertes (data.gouv.fr, OpenData) et generer des rapports de validation.

**Notebooks CoursIA :** SW-8 (SHACL)

**Technologies :** pySHACL, rdflib, Apache Jena

**References :**
- W3C, *SHACL Shapes Constraint Language*, 2017, [https://www.w3.org/TR/shacl/](https://www.w3.org/TR/shacl/)
- Knublauch, H. & Kontokostas, D., *Shapes Constraint Language (SHACL)*, W3C Recommendation

**Difficulte :** 3/5

---

### Categorie H : Representation des Connaissances et Raisonnement

#### H1 — Systeme de maintenance de verite (JTMS)

**Description :** Implementer un systeme de maintenance de verite (Justification-based Truth Maintenance System) qui gere les dependances entre croyances et propage les mises a jour quand une croyance est retractee. Appliquer a un systeme expert simple.

**Notebooks CoursIA :** Tweety-4 (Belief Revision/AGM)

**Technologies :** Python, TweetyProject (JPype)

**References :**
- Doyle, J., *A Truth Maintenance System*, Artificial Intelligence, 1979
- de Kleer, J., *A Comparison of ATMS and CSP Techniques*, IJCAI 1989

**Difficulte :** 3/5

#### H2 — Ontologies et raisonnement semantique (OWL Reasoning)

**Description :** Construire une ontologie formelle en OWL 2 avec des classes, proprietes et axiomes. Utiliser un reasoner pour effectuer des inferences automatiques (classification, detection d'inconsistance). Comparer OWL avec les logiques de description ALC.

**Notebooks CoursIA :** SW-7 (OWL), SW-13 (Reasoners)

**Technologies :** Owlready2, Protégé, HermiT reasoner

**References :**
- Baader, F. et al., *The Description Logic Handbook*, Cambridge, 2nd ed., 2007

**Difficulte :** 3/5

#### H3 — Graphes de connaissances et reponse a des questions

**Description :** Implementer un systeme de reponse a des questions (QA) sur un graphe de connaissances. Traduire des questions en langage naturel en requetes SPARQL ou en chemins de raisonnement. Evaluer sur un benchmark KGQA.

**Notebooks CoursIA :** SW-11, SW-12, Argument_Analysis/

**Technologies :** rdflib, LLM (pour le parsing), SPARQL

**References :**
- Lan, Y. et al., *KG-based Question Answering*, ACM Computing Surveys, 2023
- Unger, C. et al., *Template-Based Question Answering over RDF Data*, WWW 2012

**Difficulte :** 3/5

#### H4 — Logique de description et raisonnement sur des domaines medicaux

**Description :** Modeliser un domaine medical (diagnostic, interactions medicamenteuses) en logique de description (OWL 2 EL). Utiliser un reasoner pour detecter des interactions ou des contre-indications. Evaluer la complexite du raisonnement.

**Notebooks CoursIA :** SW-7, SW-13, Tweety-3

**Technologies :** Owlready2, ELK reasoner, SNOMED CT (optionnel)

**References :**
- Baader, F. et al., *The Description Logic Handbook*, Cambridge, 2007
- Rector, A. et al., *OWL Ontologies and Clinical Data*, JRSM, 2009

**Difficulte :** 4/5

---

### Categorie I : Argumentation et Raisonnement Debateur

#### I1 — Analyse et detection de sophismes par apprentissage symbolique

**Description :** Construire un pipeline qui detecte les sophismes (ad hominem, paille, faux dilemme) dans des textes argumentatifs. Utiliser un LLM pour l'extraction initiale, puis valider formellement avec TweetyProject (argumentation frameworks de Dung).

**Notebooks CoursIA :** Argument_Analysis/Agentic-1, Tweety-5

**Technologies :** Semantic Kernel, TweetyProject, OpenAI API

**References :**
- Habernal, I. et al., *Argumentation Mining*, User Modeling and User-Adapted Interaction, 2017
- Dung, P.M., *On the Acceptability of Arguments and its Fundamental Role in Nonmonotonic Reasoning*, AI, 1995

**Difficulte :** 3/5

#### I2 — Generation de contre-arguments par raisonnement formel

**Description :** Implementer un systeme qui, etant donne un argument formalise en ASPIC+, genere automatiquement des contre-arguments et evalue les extensions de l'argumentation resultante. Utiliser les semantiques de Dung (grounded, preferred, stable).

**Notebooks CoursIA :** Tweety-6 (ASPIC+), Tweety-7a (Extended Frameworks)

**Technologies :** TweetyProject, Python

**References :**
- Prakken, H., *An Abstract Framework for Argumentation with Structured Arguments*, Argument & Computation, 2010
- Besnard, P. & Hunter, A., *Elements of Argumentation*, MIT Press, 2008

**Difficulte :** 3/5

#### I3 — Argumentation dialogique multi-agents

**Description :** Simuler un dialogue argumentatif entre plusieurs agents (chaque agent defendant une position) avec des regles formelles d'echange. Implementer les protocols de Parsons et McBurney. Evaluer la qualite du consensus atteint.

**Notebooks CoursIA :** Tweety-8 (Agent Dialogues), Argument_Analysis/

**Technologies :** TweetyProject, Semantic Kernel, LLM API

**References :**
- McBurney, P. et al., *The eightfold way of argumentation*, Argument & Computation, 2021
- ICCMA 2023, *International Competition on Computational Models of Argumentation*, AI Journal, 2025

**Difficulte :** 4/5

#### I4 — Evaluation automatique de la qualite argumentative

**Description :** Developper un systeme d'evaluation automatique de la qualite argumentative d'un texte ou d'un discours, en utilisant des criteres formels (coherence logique, completude des premisses, force des inférences) et un LLM pour l'analyse de surface.

**Notebooks CoursIA :** Argument_Analysis/Agentic-1 a Agentic-3

**Technologies :** Semantic Kernel, TweetyProject, NLP

**References :**
- Wachsmuth, H. et al., *Computational Argumentation Quality Assessment in Natural Language*, EACL 2017
- Persing, I. & Ng, V., *End-to-End Argumentation Evaluation*, EMNLP 2017

**Difficulte :** 3/5

#### I5 — Benchmarks ICCMA — solveurs d'argumentation de Dung

**Description :** Telecharger les benchmarks de la competition ICCMA (International Competition on Computational Models of Argumentation) et implementer un solveur d'argumentation de Dung calculant les extensions sous differentes semantiques (grounded, preferred, stable, complete). Comparer les performances avec les solveurs de la competition (Crustabri, etc.). Visualiser les graphes d'attaque et les extensions. Sujet d'entree ideal dans l'argumentation formelle.

**Notebooks CoursIA :** Tweety-5 (Abstract Argumentation, Dung)

**Technologies :** Python, networkx (visualisation), TweetyProject

**References :**
- Jarvisalo, M. et al., *ICCMA 2023: 5th International Competition on Computational Models of Argumentation*, AI Journal, 2025
- Dung, P.M., *On the Acceptability of Arguments*, AI, 1995

**Difficulte :** 2/5

#### I6 — Argumentation structuree ASPIC+ et logique defaisable (DeLP/ABA)

**Description :** Implementer un systeme d'argumentation structuree en utilisant ASPIC+ (regles strictes vs. defaisables) ou DeLP (Defeasible Logic Programming) via TweetyProject. Modeliser un debat avec arguments, contre-arguments, et attaques (rebutting, undercutting, undermining). Comparer les extensions sous differentes semantiques. Appliquer a un domaine concret (recommandation de films, diagnostic medical simplifie).

**Notebooks CoursIA :** Tweety-6 (ASPIC+, DeLP, ABA, ASP/Clingo), Tweety-7a (Extended Frameworks)

**Technologies :** TweetyProject, py-aspic, Clingo

**References :**
- Prakken, H., *An Abstract Framework for Argumentation with Structured Arguments*, Argument & Computation, 2010
- Rienstra, T. et al., *Argumentative Reasoning in ASPIC+ under Incomplete Information*, JAIR, 2025
- Garcia, A. & Simari, G., *Defeasible Logic Programming: DeLP*, 2004

**Difficulte :** 3/5

---

### Categorie J : Agents Symboliques et Architecture Cognitive

#### J1 — Systeme multi-agents de resolution de problemes par planification

**Description :** Concevoir un systeme multi-agents ou chaque agent possede un role (planificateur, executeur, moniteur) et communique par des messages symboliques. Utiliser un planificateur PDDL ou CP-SAT pour generer des plans distribues.

**Notebooks CoursIA :** Planners-12 (LOOP), CSP-9 (Distributed)

**Technologies :** OR-Tools, Semantic Kernel, Python (asyncio)

**References :**
- Wooldridge, M., *An Introduction to MultiAgent Systems*, Wiley, 2nd ed., 2009
- Durfee, E.H., *Distributed Problem Solving and Planning*, ECSL 1999

**Difficulte :** 3/5

#### J2 — Agent cognitif hybride (symbolique + subsymbolique)

**Description :** Implementer un agent cognitif qui combine un module symbolique (regles, logique) avec un module subsymbolique (reseau de neurones, LLM) dans une architecture SOAR ou ACT-R simplifiee. Evaluer sur des taches de raisonnement mixtes.

**Notebooks CoursIA :** Lean-7 a Lean-9 (LLM+Symbolique), Argument_Analysis/

**Technologies :** Semantic Kernel, Z3, Python

**References :**
- Garcez, A. d'Avila et al., *Neurosymbolic AI: The 3rd Wave*, AI Review, 2024
- Kautz, H., *The Third AI Debate*, KR 2022

**Difficulte :** 4/5

#### J3 — Serveur MCP d'outils d'analyse symbolique

**Description :** Creer un serveur MCP (Model Context Protocol) exposant des outils symboliques (solveur SAT/SMT, verificateur de preuves, reasoner OWL) comme plugins utilisables par un LLM. L'agent LLM appelle les outils via le protocole MCP.

**Notebooks CoursIA :** Lean-9 (SK Multi-Agents), CSP-6 (LLM+CSP)

**Technologies :** MCP SDK, Z3, PySAT, Python

**References :**
- Anthropic, *Model Context Protocol*, 2024, [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- Microsoft, *Semantic Kernel*, [https://github.com/microsoft/semantic-kernel](https://github.com/microsoft/semantic-kernel)

**Difficulte :** 3/5

#### J4 — Integration LLM + solveurs symboliques (LLM-as-a-reasoner)

**Description :** Implementer un pipeline ou un LLM traduit des problemes en langage naturel en modeles symboliques (SAT, SMT, CSP), appelle un solveur, et interprete les resultats en langage naturel. Etudier les erreurs de traduction et les strategies de correction.

**Notebooks CoursIA :** CSP-6 (LLM+CSP), Planners-10 (LLM Planning), Planners-12 (LOOP)

**Technologies :** OpenAI API, OR-Tools CP-SAT, Z3, Python

**References :**
- Pan, L. et al., *Logic-LM: Faithful Logical Reasoning with LLMs*, EMNLP 2023
- Katz, M. et al., *Duality in LLM-assisted Planning*, ICAPS 2024

**Difficulte :** 4/5

---

### Categorie K : Cryptographie Symbolique et Securite

#### K1 — Cryptanalyse par contraintes de chiffrements classiques

**Description :** Modeliser le cassage de chiffrements classiques (Vigenere, Enigma simplifie, Playfair) comme un probleme SAT/SMT. Comparer les performances avec les attaques par force brute et par analyse de frequence.

**Notebooks CoursIA :** SymbolicAI/Linq2Z3

**Technologies :** Z3, PySAT, Python

**References :**
- Moliere, M., *SAT-based Cryptanalysis of Stream Ciphers*, 2021
- Bard, G.V., *Algebraic Cryptanalysis*, Springer, 2009

**Difficulte :** 3/5

#### K2 — Verification de protocoles cryptographiques par model checking

**Description :** Modeliser un protocole cryptographique (Needham-Schroeder, Diffie-Hellman, TLS handshake) comme un systeme de transition et verifier des proprietes de confidentialite et d'authenticite par model checking (Tamarin, ProVerif).

**Technologies :** Tamarin Prover, ProVerif, Python

**References :**
- Blanchet, B., *Modeling and Verifying Security Protocols with the Applied Pi Calculus and ProVerif*, Foundations and Trends in Privacy and Security, 2016
- Meier, S. et al., *TAMARIN: A Tool for Symbolic Analysis of Security Protocols*, CSF 2013

**Difficulte :** 4/5

#### K3 — Chiffrement homomorphe et calcul sur donnees chiffrees

**Description :** Implementer des operations arithmetiques de base (addition, multiplication) sur des donnees chiffrees avec un schema homomorphe (BFV, CKKS via TenSEAL ou Microsoft SEAL). Evaluer les performances et les limitations (bruit, profondeur de circuit).

**Notebooks CoursIA :** SmartContracts/SC-16

**Technologies :** TenSEAL, Microsoft SEAL, Python

**References :**
- Gentry, C., *A Fully Homomorphic Encryption Scheme*, PhD Thesis, Stanford, 2009
- Brakerski, Z., *Fully Homomorphic Encryption without Modulus Switching*, CRYPTO 2012

**Difficulte :** 4/5

---

### Categorie L : Puzzles, Jeux et Problemes Combinatoires

#### L1 — Resolution de Sudoku par multiples solveurs (SAT, CP, LLL)

**Description :** Implementer et comparer au moins 5 approches de resolution de Sudoku (backtracking, Dancing Links, OR-Tools CP-SAT, Z3 SMT, algorithme genetique). Benchmark sur des grilles de difficulte croissante et analyser les complexites theoriques.

**Notebooks CoursIA :** Sudoku/ (18 solveurs, 32 notebooks)

**Technologies :** OR-Tools, Z3, PySAT, DEAP/PyGAD

**References :**
- Knuth, D.E., *Dancing Links*, Millennial Perspectives in CS, 2000
- Yato, T. & Seta, T., *Complexity and Completeness of Finding Another Solution*, AAAI 2002

**Difficulte :** 2/5

#### L2 — Generation procedurale par contraintes de niveaux de jeu

**Description :** Implementer un generateur procedural de niveaux (plateformes, donjons, cartes) base sur des contraintes CP-SAT ou Wave Function Collapse. Definir des contraintes de jouabilite (accessibilite, difficulte progressive) et esthetiques.

**Notebooks CoursIA :** CSP-3 (Global Constraints), Sudoku/

**Technologies :** OR-Tools CP-SAT, Python, pygame (visualisation)

**References :**
- Karth, I. & Smith, A.M., *WaveFunctionCollapse is Constraint Solving in the Wild*, FDG 2017
- Togelius, J. et al., *Search-Based Procedural Content Generation*, TCIAIG, 2011

**Difficulte :** 3/5

#### L3 — Resolution de jeux combinatoires par minimax et alpha-beta symbolique

**Description :** Implementer un joueur pour un jeu combinatoire (Connect Four, Othello, Hex) avec minimax, elagage alpha-beta, tables de transposition. Comparer avec MCTS et un joueur DQN. Organiser un tournoi entre les approches.

**Notebooks CoursIA :** Search/Search-6 (Adversarial), Search/Search-7 (MCTS), App-12/App-14 (Connect Four)

**Technologies :** Python, OpenSpiel, numpy

**References :**
- Knuth, D.E. & Moore, R.W., *An Analysis of Alpha-Beta Pruning*, Artificial Intelligence, 1975
- Browne, C. et al., *A Survey of Monte Carlo Tree Search Methods*, IEEE TCIAG, 2012

**Difficulte :** 3/5

---

### Categorie M : IA Neuro-Symbolique

#### M1 — Pipeline LLM + verificateur symbolique pour la generation fiable

**Description :** Construire un pipeline en deux etapes : (1) un LLM genere des solutions candidates (plans, preuves, modeles) en langage naturel ou JSON, (2) un verificateur symbolique (Z3, Lean, CP-SAT) valide formellement la correction. Etudier le taux de rejet et les strategies de re-prompting. Ce sujet est au coeur de la tendance "LLM-as-a-reasoner" et de la verification neuro-symbolique.

**Notebooks CoursIA :** CSP-6 (LLM+CSP), Lean-7/8/9 (LLM+Lean), Planners-12 (LOOP)

**Technologies :** OpenAI API / Semantic Kernel, Z3, OR-Tools CP-SAT, Python

**References :**
- Pan, L. et al., *Logic-LM: Faithful Logical Reasoning with LLMs*, EMNLP 2023
- Garcez, A. d'Avila et al., *Neurosymbolic AI: The 3rd Wave*, AI Review, 2024
- Katz, M. et al., *Duality in LLM-assisted Planning*, ICAPS 2024

**Difficulte :** 3/5

#### M2 — Reseau de neurones logique (Logical Neural Networks)

**Description :** Implementer ou utiliser des reseaux de neurones logiques (LNN — IBM) ou des Logic Tensor Networks (LTN) qui integrent des contraintes logiques directement dans la fonction de perte d'un reseau de neurones. Appliquer a une tache de classification avec garantie de coherence logique.

**Notebooks CoursIA :** Tweety-2/3 (Logiques), CSP-7 (Soft Constraints)

**Technologies :** PyTorch, LNN (IBM), Logic Tensor Networks, Python

**References :**
- Riegel, R. et al., *Logical Neural Networks*, IBM Research, 2020
- Badreddine, S. et al., *Logic Tensor Networks for Semantic Image Interpretation*, KR 2022
- Garcez, A. d'Avila et al., *Neurosymbolic AI: The 3rd Wave*, AI Review, 2024

**Difficulte :** 4/5

#### M3 — Regression symbolique — decouvrir des equations a partir de donnees

**Description :** Utiliser PySR (PySymbolicRegression) pour decouvrir automatiquement des equations mathematiques a partir de donnees experimentales. Tester sur des datasets de reference (lois physiques, equations dynamiques) et evaluer la precision, la parcimonie et l'interpretabilité des equations decouvertes par rapport aux solutions connues.

**Notebooks CoursIA :** Search/Search-5 (GA), Search/Search-11 (Metaheuristiques)

**Technologies :** PySR, Python, numpy, matplotlib

**References :**
- Cranmer, M., *Interpretable Machine Learning for Science with PySR*, 2023, [GitHub](https://github.com/MilesCranmer/PySR)
- Schmidt, M. & Lipson, H., *Distilling Free-Form Natural Laws from Experimental Data*, Science, 2009
- Udrescu, S.M. & Tegmark, M., *AI Feynman: A Physics-Inspired Method for Symbolic Regression*, Science Advances, 2020

**Difficulte :** 3/5

#### M4 — Decouverte scientifique automatisee par regression symbolique et LLM

**Description :** Construire un agent "AI scientist" qui (1) charge un dataset physique/chimique, (2) utilise un LLM pour proposer des formes fonctionnelles candidates inspirees de theories existantes, (3) affine avec PySR, (4) valide les decouvertes contre les lois connues. Ce sujet combine LLM, regression symbolique et raisonnement symbolique.

**Notebooks CoursIA :** Search/Search-11 (Metaheuristiques), CSP-6 (Hybridation)

**Technologies :** PySR, OpenAI API, Python, SymPy

**References :**
- Shojaee, P. et al., *Automated Scientific Discovery: From Equation Discovery to Autonomous Discovery Systems*, Machine Learning, Springer, 2026
- Wang, H. et al., *Scientific Discovery in the Age of Artificial Intelligence*, Nature, 2023

**Difficulte :** 4/5

#### M5 — Evaluation comparee LLM vs. approches symboliques sur un benchmark

**Description :** Choisir un benchmark de raisonnement logique (LogicGrid, bAbI, ProofWriter, FLD) et comparer les performances d'un LLM brut (zero-shot, few-shot) avec celles d'un pipeline symbolique (Z3, PySAT). Analyser les types d'erreurs de chaque approche et identifier les points forts complementaires. Sujet ideal pour decouvrir la complementarite neural/symbolique sans implementer de pipeline complexe.

**Notebooks CoursIA :** SymbolicAI/Linq2Z3, Sudoku/ (comparaison multi-solveurs), Argument_Analysis/

**Technologies :** OpenAI API, Z3, PySAT, Python

**References :**
- Pan, L. et al., *Logic-LM: Faithful Logical Reasoning with LLMs*, EMNLP 2023
- Tafjord, O. et al., *ProofWriter: Generating Implications, Proofs, and Abductive Statements*, EMNLP 2021

**Difficulte :** 2/5

---

### Categorie N : Raisonnement Causal et Decision

#### N1 — Decouverte causale a partir de donnees observationnelles

**Description :** Implementer un algorithme de decouverte causale (PC, FCI, ou GES) qui construit un graphe causal a partir de donnees observationnelles. Comparer les resultats avec la structure causale veridique sur des datasets synthetiques et des datasets de reference.

**Notebooks CoursIA :** Research/ (reseaux bayesiens, graphes de facteurs)

**Technologies :** DoWhy, CausalML, Python, networkx

**References :**
- Spirtes, P. et al., *Causation, Prediction, and Search*, MIT Press, 2nd ed., 2000
- Pearl, J., *Causality: Models, Reasoning, and Inference*, Cambridge, 2nd ed., 2009
- Chickering, D.M., *Optimal Structure Identification with Greedy Search*, JMLR, 2002

**Difficulte :** 3/5

#### N2 — Raisonnement causal par le do-calculus avec DoWhy

**Description :** Utiliser le framework DoWhy (Microsoft) pour realiser des analyses causales completes : modelisation, identification (do-calculus), estimation (propensity score, IV, double machine learning), et refutation. Appliquer a un dataset reel (sante, education, economie).

**Notebooks CoursIA :** Research/ (reseaux bayesiens)

**Technologies :** DoWhy, CausalML, pandas, scipy

**References :**
- Pearl, J. & Mackenzie, D., *The Book of Why*, Basic Books, 2018
- Sharma, A. & Kiciman, E., *DoWhy: A Python Library for Causal Inference*, Microsoft Research, 2020
- Huntington, D., *The Causal Inference Playbook*, [causalml-book.org](https://causalml-book.org)

**Difficulte :** 3/5

#### N3 — Diagnostic abductif — raisonnement par abduction

**Description :** Implementer un systeme de diagnostic abductif : etant donne des observations (symptomes, erreurs, anomalies), trouver l'ensemble minimal d'hypotheses (maladies, pannes, causes) qui les expliquent. Utiliser l'abduction par couverture d'ensemble ou la programmation logique abductive (ALP). Appliquer au diagnostic medical ou au diagnostic de pannes.

**Notebooks CoursIA :** Tweety-5/6 (Argumentation), Research/ (reseaux bayesiens)

**Technologies :** Python, Z3 (pour la resolution), Prolog (optionnel)

**References :**
- Pearl, J., *Causality*, Cambridge, 2009 (chapitre sur l'abduction)
- Bylander, T. et al., *The Computational Complexity of Abduction*, Artificial Intelligence, 1991
- Kakas, A.C. et al., *Abductive Logic Programming*, JLC, 1992

**Difficulte :** 3/5

#### N4 — Evaluation du raisonnement causal des LLM

**Description :** Evaluer si les LLM peuvent raisonner causalement de maniere valide ou s'ils confondent correlation et causation. Construire un benchmark de questions causales (association, intervention, contrefactuel — la hierarchie de Pearl) et comparer les performances des LLM avec des methodes causales formelles.

**Notebooks CoursIA :** CSP-6 (LLM+CSP), Argument_Analysis/

**Technologies :** OpenAI API, DoWhy, Python

**References :**
- Zecevic, M. et al., *Causal Parrots: LLMs Talk About Causality*, JAIR, 2023
- Jin, Z. et al., *CLADDER: A Benchmark for Causal Reasoning in Language Models*, NeurIPS 2023
- Pearl, J., *The Seven Tools of Causal Inference*, CACM, 2018

**Difficulte :** 4/5

---

### Categorie O : Raisonnement Qualitatif et Bon Sens

#### O1 — Raisonnement spatial qualitatif par les calculs RCC8

**Description :** Implementer le calcul relationnel spatial RCC8 (Region Connection Calculus — 8 relations : disconnected, externally connected, overlapping, tangential proper part, non-tangential proper part, et leurs inverses, equal). Construire un raisonneur par contraintes qui infer les relations spatiales implicites et detecte les inconsistances.

**Notebooks CoursIA :** CSP-8 (Temporal CSP), Search/Search-10 (Automates symboliques)

**Technologies :** Python, Z3 (contraintes relationnelles), networkx

**References :**
- Randell, D.A. et al., *A Spatial Logic Based on Regions and Connection*, KR 1992
- Renz, J. & Nebel, B., *Qualitative Spatial Reasoning with Constraint Calculi*, 2004
- Cohn, A.G. & Renz, J., *Qualitative Spatial Reasoning*, Handbook of KR, 2008

**Difficulte :** 3/5

#### O2 — Raisonnement temporel qualitatif — Algebres d'Allen et STP

**Description :** Implementer le raisonnement temporel qualitatif base sur l'algebre d'Allen (13 relations d'intervalles : before, after, meets, met-by, overlaps, etc.) et le Simple Temporal Problem (STP). Construire un propagateur de contraintes temporelles et l'appliquer a la planification ou a la narration.

**Notebooks CoursIA :** CSP-8 (Temporal CSP), Planners-8 (Temporal Planning)

**Technologies :** Python, OR-Tools, networkx

**References :**
- Allen, J.F., *Maintaining Knowledge about Temporal Intervals*, CACM, 1983
- Dechter, R. et al., *Temporal Constraint Networks*, Artificial Intelligence, 1991

**Difficulte :** 3/5

#### O3 — Raisonnement de bon sens par graphe de connaissances (Commonsense)

**Description :** Utiliser ConceptNet et/ou ATOMIC comme base de connaissances de bon sens. Construire un systeme qui repond a des questions de sens commun (PIQA, CommonsenseQA) en combinant le graphe de connaissances avec un LLM pour le raisonnement. Evaluer la contribution du graphe vs. le LLM seul.

**Notebooks CoursIA :** SW-11 (Knowledge Graphs), SW-12 (GraphRAG)

**Technologies :** ConceptNet, ATOMIC, rdflib, OpenAI API

**References :**
- Liu, H. & Singh, P., *ConceptNet: A Practical Commonsense Reasoning Tool*, AAAI 2004
- Sap, M. et al., *ATOMIC: An Atlas of Machine Commonsense*, AAAI 2019
- Bisk, Y. et al., *PIQA: Reasoning about Physical Commonsense*, AAAI 2020

**Difficulte :** 3/5

#### O4 — Raisonnement par analogie — theorie du mapping structurel

**Description :** Implementer un modele computationnel de la Structure-Mapping Theory (Gentner, 1983) qui trouve des analogies entre representations structurees (graphes d'entites et de relations). Comparer les analogies trouvees par l'algorithme symbolique avec celles generees par un LLM.

**Technologies :** Python, networkx, OpenAI API

**References :**
- Gentner, D., *Structure-Mapping: A Theoretical Framework for Analogy*, Cognitive Science, 1983
- Forbus, K. et al., *Structure Mapping Engine (SME)*, 2017
- Webb, T. et al., *Emergent Analogical Reasoning in LLMs*, Nature, 2023

**Difficulte :** 3/5

---

### Categorie P : Verification Formelle des Systemes IA

#### P1 — Verification de robustesse de reseaux de neurones par abstraction

**Description :** Implementer un verificateur de robustesse pour un petit reseau de neurones (classifieur MNIST ou CIFAR) en utilisant l'interpretation abstraite ou le solving SMT. Prouver que le reseau est robuste a des perturbations bornees (L-infinity) autour d'images de test.

**Technologies :** Z3, Marabou, ERAN, PyTorch

**References :**
- Katz, G. et al., *Reluplex: An Efficient SMT Solver for Verifying Deep Neural Networks*, CAV 2017
- Singh, G. et al., *An Abstract Domain for Certifying Neural Networks*, POPL 2019
- Huang, X. et al., *A Survey of Safety and Trustworthiness of Deep Neural Networks*, 2020

**Difficulte :** 4/5

#### P2 — Verification de politiques RL par contraintes formelles

**Description :** Formaliser des proprietes de surete pour une politique RL (ex: "l'agent ne visite jamais un etat interdit", "la recompense cumulative reste positive") comme des contraintes logiques. Utiliser Z3 pour verifier que la politique satisfait ces proprietes sur un espace d'etats discret ou abstrait.

**Notebooks CoursIA :** RL/ (6 notebooks), CSP-1 a CSP-3

**Technologies :** Z3, Stable Baselines3, Gymnasium

**References :**
- Fulton, L. & Platzer, A., *Verifiably Safe Off-Model Reinforcement Learning*, TACAS 2018
- Anderson, G. et al., *Verification of Neural Networks*, 2024 survey

**Difficulte :** 4/5

#### P3 — Specification et verification de securite d'agents LLM par logique temporelle

**Description :** Specifier des proprietes de securite pour un agent LLM (ex: "l'agent ne revele jamais d'informations privees", "l'agent respecte toujours le protocole de communication") en logique temporelle LTL ou CTL. Implementer un model checker simplifie pour verifier ces proprietes sur des traces d'execution.

**Technologies :** NuSMV, Python, LLM API

**References :**
- AgentVerify: Compositional Formal Verification of AI Agent Safety, arXiv, 2026
- Baier, C. & Katoen, J.-P., *Principles of Model Checking*, MIT Press, 2008
- Formal Methods in the Agentic AI Era: A Strategic Agenda, arXiv, 2026

**Difficulte :** 4/5

---

### Categorie Q : Raisonnement Ethique et Normatif

#### Q1 — Raisonneur deontique — logique des normes et obligations

**Description :** Implementer un raisonneur en logique deontique (obligations O, permissions P, interdictions F) capable de verifier si un plan d'action satisfait un ensemble de normes. Detecter les conflicts normatifs et proposer des resolutions. Utiliser Z3 ou TweetyProject pour le solving.

**Notebooks CoursIA :** Tweety-2/3 (Logiques avancees), Tweety-9 (Preferences)

**Technologies :** TweetyProject, Z3, Python

**References :**
- von Wright, G.H., *Deontic Logic*, Mind, 1951
- McNamara, P., *Deontic Logic*, Stanford Encyclopedia of Philosophy, 2023
- Governatori, G. & Rotolo, A., *Logic of Violations*, DEON 2006

**Difficulte :** 3/5

#### Q2 — Verification d'alignement de valeurs par methodes formelles

**Description :** Formaliser des valeurs ethiques (equite, non-discrimination, minimisation du dommage) comme des contraintes formelles et verifier qu'un systeme d'IA (classifieur, politique RL) les satisfait. Utiliser Z3 pour le contre-exemple et le testing symbolique.

**Technologies :** Z3, Python, Fairlearn (pour les metriques d'equite)

**References :**
- Gabriel, I., *Artificial Intelligence, Values, and Alignment*, Minds and Machines, 2020
- EuGenAI: Ethics-Guided AI, 2025
- NIST AI Risk Management Framework, 2023

**Difficulte :** 4/5

#### Q3 — Raisonnement juridique formel par argumentation et logique

**Description :** Modeliser un corpus de regles juridiques (ex: droit du travail, droit de la consommation) en logique et utiliser les frameworks d'argumentation (Dung, ASPIC+) pour raisonnement sur des cas juridiques. Gerer les conflicts de normes et les exceptions.

**Notebooks CoursIA :** Tweety-5/6 (Argumentation), SW-7 (OWL)

**Technologies :** TweetyProject, Z3, Python

**References :**
- Prakken, H. & Sartor, G., *Law and Logic: A Review from an Argumentation Perspective*, Artificial Intelligence, 2015
- Wyner, A. & Bench-Capon, T., *Argumentation and Legal Text*, 2020

**Difficulte :** 3/5

---

### Categorie R : Raisonnement sous Incertitude et Revision des Croyances

#### R1 — Revision des croyances par les postulats AGM

**Description :** Implementer un systeme de revision des croyances conforme aux postulats AGM (Alchourron-Gardenfors-Makinson). Gerer l'incorporation de nouvelles informations potentiellement contradictoires avec les croyances existantes. Comparer les strategies de revision (lexicographique, Dalal, distance-based).

**Notebooks CoursIA :** Tweety-4 (Belief Revision/AGM)

**Technologies :** TweetyProject, Python, Z3

**References :**
- Alchourron, C.E. et al., *On the Logic of Theory Change*, Journal of Symbolic Logic, 1985
- Gardenfors, P., *Knowledge in Flux*, MIT Press, 1988
- Hansson, S.O., *A Textbook of Belief Dynamics*, Springer, 1999

**Difficulte :** 3/5

#### R2 — Programmation probabiliste avec Infer.NET

**Description :** Utiliser Infer.NET (Microsoft) pour modeliser des problemes de raisonnement sous incertitude : inference bayesienne, melange de modeles, prediction avec intervalles de confiance. Comparer avec l'approche symbolique classique (logique monotone).

**Notebooks CoursIA :** Research/ (Infer.NET, reseaux bayesiens)

**Technologies :** Infer.NET (.NET), PyMC (Python), numpy

**References :**
- Minka, T. et al., *Infer.NET 2*, Microsoft Research, 2018
- Ghahramani, Z., *Probabilistic Machine Learning and Artificial Intelligence*, Nature, 2015

**Difficulte :** 3/5

#### R3 — Raisonnement epistemique et logique multi-agents

**Description :** Implementer un systeme de raisonnement epistemique (logique de la connaissance et de la croyance) pour un systeme multi-agents. Modeliser des scenarios classiques (puzzle des menteurs, puzzle de muddy children, encheres avec information privee) et raisonner formellement sur ce que chaque agent sait ou croit.

**Notebooks CoursIA :** Tweety-3 (Modal Logic), GameTheory/11 (Bayesian Games)

**Technologies :** Python, TweetyProject, Z3

**References :**
- Fagin, R. et al., *Reasoning About Knowledge*, MIT Press, 1995
- Ditmarsch, H. van et al., *Dynamic Epistemic Logic*, Springer, 2007
- Meyer, J.-J.Ch. & Hoek, W. van der, *Epistemic Logic for AI and Computer Science*, Cambridge, 1995

**Difficulte :** 4/5
