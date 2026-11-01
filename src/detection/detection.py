"""Module de détection des objets.

Ce module contiendra à terme la logique permettant de détecter et d'isoler
les pièces présentes dans une image
"""

from __future__ import annotations

import cv2
import numpy as np


class CoinDetector:
    """Classe de remplacement pour la détection des pièces."""

    def __init__(self):
        """Initialise les paramètres du détecteur."""
        pass

    def detect(self, image):
        """Renvoie les régions correspondant aux pièces détectées.

        Paramètres
        ----------
        image :
            Image d'entrée sous forme de tableau NumPy ou d'image OpenCV.
        """
        return []


def detect_edges(
    image: np.ndarray,
    threshold1: int = 50,
    threshold2: int = 150,
) -> np.ndarray:
    """Détecte les contours d'une image en niveaux de gris avec Canny"""
    if not isinstance(image, np.ndarray):
        raise ValueError("L'image doit être un tableau NumPy.")

    if image.size == 0:
        raise ValueError("L'imagene peut pas être vide.")

    if image.ndim != 2:
        raise ValueError("L'image doit être une image en niveaux de gris avec 2 dimensions.")

    if not isinstance(threshold1, (int, np.integer)):
        raise ValueError("threshold1 doit être un entier entre 0 et 255")

    if not isinstance(threshold2, (int, np.integer)):
        raise ValueError("threshold2 doit être un entier entre 0 et 255")

    if not 0 <= threshold1 <= 255 or not 0 <= threshold2 <= 255:
        raise ValueError("Les seuils doivent etre entre 0 et 255")

    if threshold1 >= threshold2:
        raise ValueError("threshold1 doit être strictement inf à threshold2.")

    edges = cv2.Canny(image, int(threshold1), int(threshold2))
    return edges


def detect_circles(image: np.ndarray) -> list[tuple[int, int, int]]:
    """Détecte les cercles dans une image en niveaux de gris ( de l'étape 3)"""
    if not isinstance(image, np.ndarray):
        raise ValueError("L'image doit être un tableau NumPy.")

    if image.size == 0:
        raise ValueError("L'image ne peut pas être vide.")

    if image.ndim != 2:
        raise ValueError("L'image doit être une image en niveaux de gris en 2dimensions.")

    if image.dtype != np.uint8:
        raise ValueError("L'image doit être de type uint8.")

    circles = cv2.HoughCircles(  #Données chiffrées trouvées grâce à chatgpt à force d'affinage
        image,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=300,
        param1=120,
        param2=45,
        minRadius=130,
        maxRadius=250,
    )

    if circles is None:
        return []

    found_circles = []
    for circle in circles[0]:
        x = int(np.round(circle[0]))
        y = int(np.round(circle[1]))
        radius = int(np.round(circle[2]))
        found_circles.append((x, y, radius))

    return found_circles
