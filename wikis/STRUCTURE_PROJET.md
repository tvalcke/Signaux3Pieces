# Structure du projet

Ce dépôt est organisé pour servir de base solide au projet académique de reconnaissance de pièces TWD dans le cadre du cours de Signaux III.

## Arborescence générale

```text
SignauxXPieces/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── test/
│
├── docs/
│   ├── acquisition.md
│   └── methodology.md
│
├── results/
│   ├── images/
│   ├── graphs/
│   └── reports/
│
├── src/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── acquisition/
│   │   └── __init__.py
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── preprocessing.py
│   │
│   ├── detection/
│   │   ├── __init__.py
│   │   └── detection.py
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   └── extraction.py
│   │
│   ├── classification/
│   │   ├── __init__.py
│   │   └── classifier.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── visualization.py
│
├── tests/
│   ├── __init__.py
│   └── test_structure.py
│
├── .gitignore
├── requirements.txt
├── README.md
├── pyproject.toml
├── STRUCTURE_PROJET.md
└── .venv/
```

## Rôle de chaque dossier

### `data/`
Ce dossier contient les données du projet.

- `raw/` : images acquises brutes, avant traitement.
- `processed/` : images prétraitées ou modifiées.
- `test/` : images de test utilisées pour valider les performances.

### `docs/`
Ce dossier contient la documentation technique et méthodologique du projet.

- `acquisition.md` : protocole de prise de vue des pièces.
- `methodology.md` : étapes prévues du pipeline de traitement.

### `results/`
Ce dossier est réservé aux résultats produits pendant le projet.

- `images/` : images de sortie ou d'illustration.
- `graphs/` : graphiques et courbes d'analyse.
- `reports/` : rapports ou conclusions intermédiaires.

### `src/`
C'est le cœur du code Python.

- `main.py` : point d'entrée du programme.
- `acquisition/` : gestion de l'acquisition des données.
- `preprocessing/` : nettoyage et préparation des images.
- `detection/` : localisation des pièces dans les images.
- `features/` : extraction des caractéristiques.
- `classification/` : identification de la valeur nominale.
- `utils/` : fonctions utiles comme la visualisation.

### `tests/`
Ce dossier contient les tests permettant de vérifier que la structure du projet fonctionne bien.

- `test_structure.py` : vérifie que les modules importants s'importent correctement.

## Rôle des fichiers de configuration

- `pyproject.toml` : configuration du projet Python et de pytest.
- `requirements.txt` : liste des dépendances nécessaires.
- `.gitignore` : exclut les fichiers temporaires, les environnements virtuels et les résultats non destinés au dépôt.

## Principe général

Le projet est structuré de manière simple et pédagogique :

1. acquisition des données,
2. préparation des images,
3. détection des pièces,
4. extraction de caractéristiques,
5. classification,
6. validation et résultats.

Cette organisation permet d'ajouter progressivement les fonctionnalités sans casser la base du projet.

## Exemple de progression prévue

Au fur et à mesure du développement, chaque module pourra être enrichi :

- ajout de fonctions de chargement d'images,
- développement de filtres et de normalisation,
- implémentation de la détection de contours ou de cercles,
- calcul de mesures discriminantes,
- mise en place d'un classifieur de pièces.

La structure actuelle est donc une base de travail propre, claire et extensible.
