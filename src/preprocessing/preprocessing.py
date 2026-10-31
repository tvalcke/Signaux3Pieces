"""
Ce module contient les fonctions de base pour préparer les images avant le
traitement de détection et de classification
"""

from __future__ import annotations

import cv2
import numpy as np


class PreprocessingPipeline:
    """Classe de remplacement pour les opérations de prétraitement."""

    def __init__(self):
        """Initialise le pipeline de prétraitement."""
        pass

    def prepare_image(self, image):
        """Renvoie une image préparée pour l'analyse suivante.

        Paramètres
        ----------
        image :
            Image d'entrée sous forme de tableau NumPy ou d'image OpenCV.
        """
        return image


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convertit une image couleur bgr en niveaux de gris

    Paramètres
    ---------
    image : np.ndarray
        Image couleur OpenCV au format BGR, avec 3 canaux.

    Retourne
    ---------
    np.ndarray
        Imge en niveaux de gris, de forme (hauteur, largeur).

    Raises
    ------
    TypeError
        Si l'entrée n'est pas un tableau NumPy
    ValueError
        Si l'image est vide, invalide ou ne contient pas 3 canaux.
    """
    if not isinstance(image, np.ndarray):
        raise TypeError("L'image doit être un tableau NumPy.")

    if image.size == 0:
        raise ValueError("L'image ne peut pas être vide.")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("L'image doit être une image couleur BGR avec exactement 3 canaux.")

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image
