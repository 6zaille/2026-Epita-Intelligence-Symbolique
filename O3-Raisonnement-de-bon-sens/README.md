# Raisonnement de bon sens par graphe de connaissances

Ce projet a été simplifié pour être exploitable localement avec des notebooks Jupyter et un petit dossier `data/`.

## Objectif

Comparer un LLM seul à un LLM enrichi par des connaissances ConceptNet, sur des tâches de bon sens simples.

## Principe

- Notebook 1 : découverte de ConceptNet
- Notebook 2 : chargement des datasets
- Notebook 3 : baseline vs graphe
- Notebook 4 : analyse des résultats

## Dépendances

Installer les dépendances minimales :

```bash
python -m pip install requests pandas networkx matplotlib seaborn datasets python-dotenv notebook ipykernel
```

## Utilisation locale

1. Démarrer Ollama :

```bash
ollama serve
```

2. Télécharger un modèle local :

```bash
ollama pull llama3.2:3b
```

3. Ouvrir les notebooks dans le dossier `notebooks/`.

## Structure

- `notebooks/` : quatre notebooks Jupyter
- `data/` : cache, résultats et exports
- `presentation_10min.txt` : script de présentation
- `presentation.html` : slide HTML simple
