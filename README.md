
# Signaux III - Reconnaissance de pièces

## Description

Projet académique développé dans le cadre du cours de Signaux III à l'EPHEC, durant l'année académique 2026-2027.

L'objectif est de développer une application Python capable de détecter et de reconnaître automatiquement plusieurs pièces de monnaie présentes sur une photographie, puis de calculer leur valeur totale.

Le projet utilise OpenCV pour le traitement d'image et Tkinter pour l'interface graphique.

Actuellement, l'application permet de charger une photographie, d'effectuer plusieurs traitements d'image et de détecter automatiquement les pièces à l'aide de la transformée de Hough.

La reconnaissance de leur valeur et le calcul du montant total restent à développer.

## Prérequis

- Python 3.12
- Tkinter
- OpenCV
- NumPy
- Pillow
- Matplotlib

Les dépendances Python sont indiquées dans `requirements.txt`.

## Installation

Cloner le dépôt et se placer dans le dossier du projet.

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activer l'environnement sous Linux :

```bash
source .venv/bin/activate
```

Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

Sous Linux, si Tkinter n'est pas disponible, installer le paquet correspondant à sa distribution :

Debian / Ubuntu :

```bash
sudo apt install python3-tk
```

Fedora :

```bash
sudo dnf install python3-tkinter
```

## Lancement de l'application

Depuis la racine du projet, avec l'environnement virtuel activé :

```bash
python -m src.main
```

Une fenêtre Tkinter s'ouvre et permet de sélectionner une devise, de charger une photographie et de lancer son analyse.

## Organisation du projet

```text
Signaux3Pieces/
├── data/
│   ├── raw/
│   │   ├── EUR/
│   │   └── TWD/
│   ├── processed/
│   └── test/
├── docs/
├── results/
│   ├── graphs/
│   ├── images/
│   └── reports/
├── src/
│   ├── acquisition/
│   │   └── image_loader.py
│   ├── preprocessing/
│   │   └── preprocessing.py
│   ├── detection/
│   │   └── detection.py
│   ├── features/
│   │   └── extraction.py
│   ├── classification/
│   │   └── classifier.py
│   ├── utils/
│   │   └── visualization.py
│   ├── gui/
│   │   └── app.py
│   ├── config.py
│   └── main.py
├── tests/
├── README.md
├── requirements.txt
└── pyproject.toml
```

### Rôle des dossiers

- `data/raw/EUR/` : photographies de pièces en euros.
- `data/raw/TWD/` : photographies de pièces en dollars taïwanais.
- `data/processed/` : emplacement prévu pour les images prétraitées.
- `data/test/` : images destinées aux essais.
- `docs/` : documentation du projet.
- `results/` : emplacement prévu pour les résultats, graphiques et rapports.
- `src/acquisition/` : chargement des photographies avec OpenCV.
- `src/preprocessing/` : conversion en niveaux de gris et filtrage.
- `src/detection/` : détection des contours et des cercles.
- `src/features/` : extraction des caractéristiques des pièces, à développer.
- `src/classification/` : identification des valeurs monétaires, à développer.
- `src/utils/` : fonctions de visualisation des résultats.
- `src/gui/` : interface graphique Tkinter.
- `tests/` : tests présents dans le dépôt.

## Images utilisées

Les photographies doivent idéalement respecter les conditions suivantes :

- Être prises du dessus, avec l'appareil perpendiculaire aux pièces.
- Présenter des pièces séparées et non superposées.
- Utiliser un fond relativement uniforme, de préférence contrastant avec les pièces.
- Éviter les reflets importants et les ombres trop marquées.
- Conserver une qualité et une résolution suffisantes.

Les premiers développements sont réalisés avec des pièces en euros. Le projet prévoit également la prise en charge des dollars taïwanais (TWD).

### Formats d'images

Le format JPG est actuellement utilisé pour les essais.

Les autres formats, notamment PNG, JPEG, BMP et TIFF, pourront être vérifiés avec le pipeline complet.

Pour obtenir les photographies de travail ou davantage d'informations sur le jeu de données, contacter Tristan.

## Fonctionnement de l'application

L'interface permet actuellement :

- De sélectionner une devise (EUR ou TWD).
- De choisir une photographie dans le dossier correspondant.
- D'afficher l'image originale.
- De lancer le traitement d'image avec le bouton « Analyser l'image ».
- D'afficher les pièces détectées à l'aide de cercles dessinés sur la photographie.
- De consulter le nombre de cercles détectés ainsi que leurs centres et rayons.

L'image originale apparaît à gauche et le résultat de la détection à droite.

Lorsqu'une nouvelle photographie est sélectionnée, le résultat de l'analyse précédente est réinitialisé.

## Traitement d'image

Le traitement est réalisé progressivement avec OpenCV.

### 1. Chargement de l'image

L'image est chargée depuis le disque et convertie en tableau NumPy.

Le chargement est indépendant de l'interface graphique et ne modifie pas le fichier original.

Fonctions utilisées :

- `np.fromfile()`
- `cv2.imdecode()`

### 2. Conversion en niveaux de gris

L'image couleur BGR est convertie en niveaux de gris pour simplifier les traitements suivants.

Fonction utilisée :

- `cv2.cvtColor()`

### 3. Filtrage gaussien

Un filtre gaussien est appliqué pour atténuer le bruit et les petites variations d'intensité.

Le noyau actuellement utilisé est de 7 × 7 pixels.

Fonction utilisée :

- `cv2.GaussianBlur()`

### 4. Détection des contours

L'algorithme de Canny permet de mettre en évidence les transitions d'intensité dans l'image.

Cette étape a notamment servi à observer les contours des pièces et à expérimenter différents paramètres.

Fonction utilisée :

- `cv2.Canny()`

La détection des contours reste disponible dans le projet, même si elle n'est pas directement utilisée comme entrée de la détection de cercles.

### 5. Détection des cercles

La transformée de Hough est utilisée pour rechercher les formes circulaires présentes sur la photographie.

Elle permet de récupérer, pour chaque cercle détecté :

- La position horizontale de son centre (x).
- La position verticale de son centre (y).
- Son rayon en pixels.

Fonction utilisée :

- `cv2.HoughCircles()`

Les paramètres ont été ajustés expérimentalement afin de réduire les détections multiples sur une même pièce.

La méthode a été essayée sur des photographies contenant différents nombres de pièces.

### 6. Filtrage des détections

Un filtrage complémentaire permet de vérifier la cohérence des cercles retournés par Hough.

Il vise notamment à :

- Écarter les cercles présentant des dimensions invalides.
- Vérifier la position des centres dans l'image.
- Limiter les détections multiples correspondant à une même pièce.

Deux cercles ne sont pas considérés comme identiques uniquement parce qu'ils sont proches. Leurs centres et leurs rayons doivent être suffisamment similaires.

Le filtrage conserve les détections jugées valides pour l'affichage final.

## Limites actuelles

Le projet permet de détecter des formes circulaires correspondant aux pièces, mais plusieurs fonctionnalités restent à développer :

- La distinction entre une pièce et un autre objet circulaire.
- L'extraction des caractéristiques propres à chaque pièce.
- La reconnaissance automatique de la valeur monétaire.
- Le calcul du montant total.
- La validation du fonctionnement sur un jeu de données plus varié.

La détection dépend également des conditions de prise de vue, notamment de l'éclairage, du contraste, de la résolution et de la taille apparente des pièces.

## Étapes prévues

- Phase 1 : création de l'interface graphique et sélection des images — terminée.
- Phase 2A : préparation de l'architecture et des modules de traitement — terminée.
- Phase 2B : prétraitement, détection et filtrage des pièces — en cours de validation.
- Phase 3 : extraction des caractéristiques et reconnaissance des valeurs — à développer.
- Phase 4 : calcul du montant total, validation et documentation finale — à développer.

## Équipe

- Valcke Tristan
- Étudiant 2 : à compléter
- Étudiant 3 : à compléter
- Étudiant 4 : à compléter

## Informations

- Cours : Signaux III - Traitement numérique
- Établissement : EPHEC
- Année académique : 2026-2027

Projet en cours de développement.
