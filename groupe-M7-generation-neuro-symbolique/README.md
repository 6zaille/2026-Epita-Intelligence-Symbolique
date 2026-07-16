# M7 - Generation de contenu neuro-symbolique par Semantic Kernel + validation CSP

Emile Jouannet - EPITA SCIA 2026 - Intelligence Symbolique (projet solo)

## Le probleme

Un LLM produit un plan de cours qui se lit bien : titres pertinents, progression plausible.
Mais il oublie des objectifs quand le syllabus grandit, et se trompe sur l'ordre des prerequis
sans jamais le signaler.

Un solveur CSP garantit ces proprietes, mais produit "Session 1, Session 2" et des
regroupements arbitraires.

Ce projet combine les deux : le LLM propose, CP-SAT verifie, et les violations repartent dans
le prompt sous forme de consignes de correction.

## Le domaine

Generer un plan de cours couvrant un syllabus, sous quatre contraintes dures :

| Contrainte | Ce que le LLM rate |
|---|---|
| Couverture : chaque objectif apparait au moins une fois | Il en oublie silencieusement |
| Prerequis : un objectif vient apres tous ses prerequis | Les chaines transitives |
| Non-chevauchement des creneaux | L'arithmetique des creneaux |
| Duree dans les bornes | Derive sur les longs syllabus |

La qualite des titres et de la progression reste au LLM : c'est ce qu'il fait bien, et ca ne se
verifie pas par un solveur. Cette repartition dur/souple est l'argument du projet.

## Architecture

```
syllabus.json
     |
     v
  Generator  (Semantic Kernel -> LLM, ou ScriptedGenerator pour les tests)
     |  plan JSON
     v
  Validator  (CP-SAT)
     |  violations
     v
  valide ? --oui--> plan final
     |
    non
     v
  build_feedback --> prompt enrichi --> (boucle)
```

### Pourquoi CP-SAT et pas trois `if`

Verifier un plan complet ne demande pas de solveur : l'affectation est totale, des
verifications directes suffisent et donnent de meilleurs messages. Le solveur sert ailleurs :

- `is_instance_feasible()` repond a "existe-t-il **un** plan valide pour ce syllabus ?". Chaque
  arc de prerequis est pose sous un literal d'hypothese ; si le modele est infaisable, CP-SAT
  rend le sous-ensemble d'hypotheses responsable via `SufficientAssumptionsForInfeasibility()`.
  Sur un cycle `A -> B -> A`, on obtient les deux arcs fautifs, pas juste "infaisable". Sans ce
  garde-fou, un syllabus cyclique ferait echouer la boucle 5 fois sans explication.
- `solve()` construit un plan de zero : c'est la baseline CSP pur.

## Structure

```
src/m7_neurosymbolic/
  schema.py      modele de domaine (Syllabus, PlanCandidate, Violation)
  validator.py   contraintes dures, faisabilite d'instance, solveur CSP pur
  feedback.py    violations -> consignes de correction (+ temoin naif)
  generator.py   Semantic Kernel, et generateur scripte pour les tests
  loop.py        la boucle
  baselines.py   LLM seul, CSP seul
  metrics.py     agregation sur plusieurs runs
tests/           20 tests, sans reseau ni cle API
demo.ipynb       notebook explicatif (executable sans cle)
data/syllabus.json
```

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Pour l'execution reelle uniquement :

```bash
cp .env.example .env    # renseigner OPENAI_API_KEY
```

## Tests

```bash
python -m pytest tests/ -q
```

Les tests utilisent `ScriptedGenerator`, qui rejoue des reponses fixees. Aucun appel reseau,
resultats deterministes, cout nul. Le vrai generateur expose la meme interface.

## Resultats

10 runs par configuration, `gpt-4o-mini`, budget 5 cycles, syllabus `data/syllabus.json`.
Reproductible via `python run_experiment.py --runs 10`, donnees brutes dans
`results/experiment.json`.

| Approche | Plans valides | Cycles | Qualite des titres |
|---|---|---|---|
| LLM seul | 0 / 10 | 1 | bonne |
| LLM + feedback naif | 0 / 10 | 5 (budget epuise) | bonne |
| LLM + feedback cible | **10 / 10** | 3.10 +/- 0.32 | bonne |
| CP-SAT seul | 10 / 10 par construction | 0 | inutilisable |

Trois observations, plus interessantes que le tableau :

**Le LLM a un angle mort systematique.** Sur 10 runs, il oublie `ARGU` et `KR` a chaque fois.
Ce n'est pas du bruit : ce sont les deux objectifs qui ne sont pas sur la chaine principale
`LOGIC -> SAT -> SMT -> VERIF`. Le modele suit le fil narratif et laisse tomber les branches
laterales. Un echec structurel, pas aleatoire.

**Le feedback naif ne suffit pas du tout.** Dire "invalide, recommence" fait recuperer `ARGU`,
puis plafonne sur `KR` pendant les 5 cycles (9 runs sur 10 finissent avec exactement `KR`
manquant). Meme LLM, meme solveur, meme reinjection du plan precedent : seule la formulation
du feedback change, et elle fait passer de 0 % a 100 %. C'est le resultat central du projet.

**La convergence n'est pas monotone.** La trajectoire typique est `[1, 2, 0]` (8 runs sur 10) :
nommer l'objectif manquant fait ajouter `KR`, ce qui casse l'arithmetique des creneaux, que le
cycle suivant repare. L'etat intermediaire est *pire* que le depart. C'est ce qui justifie une
boucle plutot qu'une passe de correction unique.

### Limites

- Un seul syllabus, un seul modele. Rien ne dit que le plateau du feedback naif se generalise.
- N = 10 : suffisant pour separer 0 % de 100 %, trop faible pour un intervalle de confiance
  serre sur le nombre de cycles.
- La qualite semantique n'est pas mesuree, seulement constatee a la lecture. La comparaison
  "titres bons vs inutilisables" est un jugement, pas une metrique.
- Objectif 5 (memoire vectorielle anti-repetition) : non traite.

## References

- Liang, T. et al. (2024). *LLM+Optimization: Towards Integrating Large Language Models and Optimization*. [arXiv:2401.17094](https://arxiv.org/abs/2401.17094)
- Yao, S. et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models*. ICLR 2023. [arXiv:2210.03629](https://arxiv.org/abs/2210.03629)
- Microsoft (2024). *Semantic Kernel Documentation*. [learn.microsoft.com](https://learn.microsoft.com/en-us/semantic-kernel/)
- Notebooks CoursIA : `GenAI/SemanticKernel/01`, `03`, `05` ; `Search/Part2-CSP/CSP-6-Hybridization`
