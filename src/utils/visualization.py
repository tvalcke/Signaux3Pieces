"""Utilitaires de visualisation

Ce module fournit des fonctions utilitaires pour afficher et tracer les
résultats intermédiaires du projet pendant le développement.
"""

import cv2
import numpy as np


def display_image(image, title="Image"):
    """Affiche une image avec un titre.

    Paramètres
    ----------
    image :
        Image à afficher.
    title : str
        Titre lisible utilisé dans la visualisation.
    """
    return {"image": image, "title": title}


def draw_circles(image: np.ndarray, circles: list[tuple[int, int, int]]) -> np.ndarray:
    """Dessine des cercles et des centres sur une image couleur - étape 5 avec transfo de hough"""
    if not isinstance(image, np.ndarray):
        raise ValueError("L'image doit être un tableau NumPy.")

    annotated = image.copy()

    for x, y, radius in circles:
        cv2.circle(annotated, (x, y), radius, (0, 255, 0), 2)
        cv2.circle(annotated, (x, y), 2, (0, 0, 255), -1)

    return annotated
