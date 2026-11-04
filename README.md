
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

La classification des pièces repose sur la combinaison des diamètres et des familles de couleur. Pour chaque pièce, le programme distingue entre une valeur identifiée, une valeur incertaine avec plusieurs hypothèses plausibles, et une pièce non identifiée lorsqu'aucune valeur n'est suffisamment fiable.

L'affichage de l'application a été simplifié pour présenter uniquement la pièce et son statut final, sans details techniques de calcul interne.

Le calcul du montant total repose sur les pièces déjà classées. Le montant identifié ne prend en compte que les pièces entièrement reconnues, tandis que le montant estimé ajoute également les pièces incertaines en utilisant leur meilleure valeur disponible. Les additions sont faites en centimes pour éviter les erreurs d'arrondi et le total est ensuite converti en euros pour l'affichage.

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

Le filtrage final repose sur les coordonnées du centre, le rayon et la suppression des doublons quasi identiques. Il n'utilise pas de score supplémentaire basé sur les contours Canny, afin de garder une logique simple et robuste.

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
- Contrôler la présence de contours autour du périmètre, afin de rejeter les faux positifs qui ne correspondent pas à une pièce réelle.

Deux cercles ne sont pas considérés comme identiques uniquement parce qu'ils sont proches. Leurs centres et leurs rayons doivent être suffisamment similaires.

La validation par contours repose sur un échantillonnage simple de points sur le cercle détecté et sur le calcul d'une proportion de points soutenus par les bords de l'image. Un score trop faible indique qu'un cercle n'a pas une structure suffisamment circulaire et suffisamment visible dans l'image.

Le filtrage conserve les détections jugées valides pour l'affichage final.

### 7. Extraction des caractéristiques des pièces

Après la détection et le filtrage des cercles, chaque pièce est caractérisée à partir de son centre, de son rayon, de son diamètre et de sa surface théorique.

La couleur moyenne est aussi calculée dans une zone légèrement plus petite que le cercle détecté, afin de limiter l'influence du fond sur les bords de la pièce.

Ces mesures sont stockées dans une liste de dictionnaires Python et servent de base pour les étapes suivantes de reconnaissance et d'analyse.

### 8. Identification de la valeur des pièces

La classification combine encore les diamètres mesurés avec les diamètres officiels des pièces en euros, puis elle affine la famille visuelle avec une analyse HSV de la zone centrale et de l'anneau extérieur.

Les diamètres servent à estimer l'échelle de la photographie et à générer des hypothèses plausibles. La teinte HSV évite de confondre les pièces dorées avec les pièces cuivrées lorsque les différences de luminosité ou de rouge influencent fortement les canaux BGR.

Les pixels trop sombres ou peu saturés sont ignorés pour calculer la teinte moyenne, car leur teinte est peu informative. Si la famille visuelle reste incertaine, la pièce est conservée comme indéterminée plutôt qu'attribuée à une mauvaise famille.

Cette approche reste expérimentale et dépend encore de l'éclairage et des reflets, mais elle est plus prudente et plus explicite que l'analyse BGR seule.

## Limites actuelles

Le projet permet de détecter des formes circulaires correspondant aux pièces, d'extraire leurs caractéristiques de base et de proposer une première identification de la valeur en euros à partir des diamètres. Plusieurs aspects restent à améliorer :

- La distinction entre une pièce et un autre objet circulaire.
- La fiabilité de l'identification si plusieurs diamètres sont proches.
- Le calcul du montant total.
- La validation du fonctionnement sur un jeu de données plus varié.
- L'extension à d'autres devises, notamment les dollars taïwanais.

La détection dépend également des conditions de prise de vue, notamment de l'éclairage, du contraste, de la résolution et de la taille apparente des pièces.

Pour la reconnaissance des pièces bicolores, le projet compare séparément les zones centrales et les anneaux. Une pièce de 1 euro est ainsi repérée par un centre argenté et un anneau doré, tandis qu'une pièce de 2 euros présente l'inverse. Cette logique reste simple et expérimentale, sans validation supplémentaire sur les contours Canny.

## Étapes prévues

### Phase 1 - Interface graphique et structure du projet

- [x] Création de la structure du projet Python.
- [x] Création de l'interface graphique avec Tkinter.
- [x] Sélection de la devise (EUR / TWD).
- [x] Sélection et affichage d'une photographie.
- [x] Préparation des modules de traitement d'image.

### Phase 2 - Traitement d'image et détection des pièces

- [x] Étape 1 : chargement des images avec OpenCV.
- [x] Étape 2 : conversion des images en niveaux de gris.
- [x] Étape 3 : application d'un filtre gaussien pour réduire le bruit.
- [x] Étape 4 : détection des contours avec l'algorithme de Canny.
- [x] Étape 5 : détection des pièces circulaires avec la transformée de Hough.
- [x] Étape 6 : filtrage des détections invalides et suppression des doublons.
- [x] Étape 7 : visualisation des cercles détectés sur l'image originale.
- [x] Étape 8 : intégration de la détection dans l'interface Tkinter.

### Phase 3 - Extraction des caractéristiques et reconnaissance

- [x] Étape 9 : extraction des caractéristiques des pièces (rayon, diamètre, surface, couleur).
- [x] Étape 10 : identification de la valeur de chaque pièce à partir des caractéristiques extraites.
- [x] Étape 11 : calcul du montant total des pièces reconnues.
- [ ] Étape 11' : affiner le plus possible pour avoir un meilleur taux de réussite.
- [ ] Étape 12 : adaptation de la reconnaissance aux pièces en dollars taïwanais (TWD).

### Phase 4 - Validation et finalisation

- [ ] Étape 13 : validation sur différentes photographies (nombre de pièces, éclairage, arrière-plan, position).
- [ ] Étape 14 : analyse des résultats et des limites des algorithmes utilisés.
- [ ] Étape 15 : finalisation du rapport, de la documentation et du poster académique.


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


> les readme et wikis sont repassés dans chatGPT pour structurer 
