# Signaux III - Reconnaissance de pièces

## Description

Projet académique développé dans le cadre du cours de Signaux III à l'EPHEC. L'objectif est de construire une application Python capable de reconnaître automatiquement une ou plusieurs pièces de monnaie présentes sur une photographie et d'en calculer la valeur totale.

Le dépôt est actuellement dans sa phase 1 : développement de l'interface graphique Tkinter. Le traitement d'image et la reconnaissance automatique ne sont pas encore implémentés.

## Prérequis

- Python 3.12
- Tkinter (inclus avec la plupart des distributions Python)
- Pillow pour le chargement et l'affichage des images
- OpenCV, NumPy et Matplotlib déjà présents comme base technique du projet

## Installation

1. Créer un environnement virtuel :
   python -m venv .venv
2. Activer l'environnement :
   . .venv/bin/activate
3. Installer les dépendances :
   python -m pip install -r requirements.txt

Sous Linux, si Tkinter n'est pas disponible, installer le paquet système :

- Debian / Ubuntu : sudo apt install python3-tk
- Fedora : sudo dnf install python3-tkinter

## Organisation des dossiers

- data/raw/EUR/ : images de pièces euro
- data/raw/TWD/ : images de pièces taïwanaises
- data/processed/ : images traitées ultérieurement
- data/test/ : jeux de test
- results/ : sorties graphiques et rapports

Les dossiers EUR et TWD sont créés et permettent de préparer le système de sélection de devise.

## Formats d'images acceptés

- PNG
- JPG
- JPEG
- BMP
- TIFF

Pour les images ( ce msg sera visible si vous bossez un peu et donc lisez cau moins le readme...) demandez à Tris

## Lancement de l'application

Commande depuis la racine du dépôt :

python -m src.main

## Fonctionnement de l'interface

La phase 1 permet à l'utilisateur :

- de choisir une devise dans une liste déroulante ;
- d'ouvrir une image depuis le dossier correspondant à la devise active ;
- d'afficher un aperçu de l'image dans l'interface Tkinter ;
- de lancer un bouton d'analyse ;
- d'afficher un message indiquant que le traitement d'image n'est pas encore implémenté.

La sélection de devise réinitialise l'image précédente dès que l'utilisateur change de devise.

## Limites actuelles

- aucun algorithme de détection de pièces n'est mis en œuvre ;
- aucune reconnaissance automatique de valeur n'est calculée ;
- aucun montant total n'est affiché depuis le pipeline de traitement ;
- le système est préparé pour la phase 2, où le prétraitement, la détection, l'extraction et la classification seront reliés.

## Étapes prévues

- Phase 1 : interface graphique et sélection de devise/image
- Phase 2 : traitement d'image et détection des pièces
- Phase 3 : extraction de caractéristiques et classification
- Phase 4 : validation, tests et documentation finale

## Équipe

- Étudiant 1 : Valcke Tristan
- Étudiant 2 : à compléter
- Étudiant 3 : à compléter
- Étudiant 4 : à compléter

## Informations

- Cours : Signaux III - Traitement numérique
- Établissement : EPHEC
- Année académique : 2026-2027

Projet en cours de développement. La phase 1 a été mise en place sans implémentation du moteur de reconnaissance automatique.

>> Les readme et wikis sont repasés dans chatGPT pour structurer