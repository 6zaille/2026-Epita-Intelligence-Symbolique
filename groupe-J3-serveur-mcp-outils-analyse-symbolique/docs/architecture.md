# Architecture — Serveur MCP d'outils d'analyse symbolique (J3)

## Vue d'ensemble

Le systeme suit le pattern **tool-augmented generation** : un LLM ne raisonne
pas « de tete » mais **delegue** chaque deduction a un outil symbolique exact,
via le protocole standardise **MCP (Model Context Protocol)**.

```
   Langage naturel                                          Langage naturel
        │  probleme                                            ▲  reponse
        ▼                                                      │
┌───────────────────┐   JSON-RPC (MCP, stdio)   ┌──────────────────────────────┐
│   Hote LLM         │ ────────────────────────▶ │   Serveur MCP                │
│   (Gemini / autre  │   tools/list              │   « symbolic-analysis »      │
│   hote MCP / ...)  │   tools/call              │                              │
│                    │ ◀──────────────────────── │  ┌────────────────────────┐  │
│  - traduit NL→forme│   resultat structure      │  │ Gestion de session /   │  │
│    symbolique      │                           │  │ contexte               │  │
│  - choisit l'outil │                           │  └────────────────────────┘  │
│  - reformule le    │                           │  ┌──────┐ ┌──────┐ ┌──────┐  │
│    resultat        │                           │  │ SAT  │ │ SMT  │ │ OWL  │  │
└───────────────────┘                           │  │PySAT │ │  Z3  │ │Herm.│  │
                                                 │  └──────┘ └──────┘ └──────┘  │
                                                 └──────────────────────────────┘
```

## Couches

| Couche | Fichier | Role |
|--------|---------|------|
| **Outils symboliques** | `src/symbolic_mcp/tools/*.py` | Fonctions pures, sans dependance MCP : `solve_sat` (PySAT), `solve_smt` (Z3), `owl_reason` (owlready2 + HermiT). Entrees/sorties JSON-serialisables. |
| **Session / contexte** | `src/symbolic_mcp/session.py` | `SessionManager` thread-safe : journal des appels (tracabilite de la chaine) et magasin d'artefacts nommes. |
| **Serveur MCP** | `src/symbolic_mcp/server.py` | `FastMCP` : enregistre les outils et la gestion de session, publie leurs schemas JSON-RPC, transport stdio. |
| **Hote LLM** | `src/symbolic_mcp/host/gemini_host.py` | Pont Gemini ↔ MCP : boucle agentique manuelle, conversion de schema, trace des appels. Le serveur reste agnostique du LLM. |
| **Evaluation** | `eval/` | Benchmark de raisonnement + scoring a 3 niveaux (selection d'outil, correction symbolique, reponse finale). |

## Flux d'une requete (chaine complete)

1. L'utilisateur pose un probleme en langage naturel a l'hote LLM.
2. Le LLM **traduit** le probleme vers la representation formelle de l'outil
   pertinent (CNF DIMACS, SMT-LIB2, ou OWL) — c'est la traduction NL→symbolique.
3. Le LLM emet un appel `tools/call` MCP ; le serveur execute le solveur/reasoner.
4. Le serveur renvoie un **resultat structure** + un `summary` en langage naturel
   (traduction symbolique→NL).
5. Le LLM fonde sa reponse finale sur ce resultat exact et, en cas d'erreur de
   formalisation, se corrige et reessaie (re-prompting).

## Decisions de conception

- **Separation stricte LLM / noyau symbolique.** Le serveur ne contient aucun
  appel LLM : il est reutilisable par n'importe quel hote MCP. La « traduction
  bidirectionnelle » est portee par (a) les schemas + descriptions d'outils pour
  NL→symbolique et (b) le champ `summary` pour symbolique→NL.
- **Fonctions pures testables.** Les outils sont des fonctions Python isolees,
  couvertes par des tests unitaires, puis simplement *enregistrees* comme outils
  MCP. La couche protocole est testee separement via un client MCP en memoire.
- **Isolation par requete pour OWL.** Chaque appel `owl_reason` cree un `World`
  owlready2 neuf → pas d'etat partage entre requetes concurrentes.
- **Robustesse d'entree.** owlready2 ne lit pas le Turtle nativement : on
  normalise via rdflib. HermiT ecrivant parfois sur stdout, on le redirige pour
  ne pas corrompre le transport MCP (qui utilise stdout pour le JSON-RPC).

## Correspondance avec les objectifs du sujet J3

| Objectif J3 | Realisation |
|-------------|-------------|
| Serveur MCP conforme | `FastMCP`, transport stdio, `tools/list` + `tools/call` (SDK officiel). |
| ≥ 3 outils symboliques | SAT (PySAT), SMT (Z3), OWL (owlready2/HermiT). |
| Sessions, contexte, traduction bidirectionnelle | `SessionManager` + schemas/descriptions (NL→sym) + `summary` (sym→NL). |
| Evaluation sur benchmarks | `eval/` : 11 problemes, precision a 3 niveaux, sortie `results.json`. |
| Documentation + exemples | `README.md`, `docs/`, `examples/`, docstrings = descriptions d'outils MCP. |
