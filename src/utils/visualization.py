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


def draw_circles(
    image: np.ndarray,
    circles: list[tuple[int, int, int]],
    features: list[dict] | None = None,
) -> np.ndarray:
    """Dessine des cercles, leurs centres et les identifiants des pièces."""
    if not isinstance(image, np.ndarray):
        raise ValueError("L'image doit être un tableau NumPy.")

    annotated = image.copy()

    for index, (x, y, radius) in enumerate(circles, start=1):
        cv2.circle(annotated, (x, y), radius, (0, 255, 0), 2)
        cv2.circle(annotated, (x, y), 2, (0, 0, 255), -1)

        if features is not None and index <= len(features):
            piece_id = features[index - 1].get("id", index)
            cv2.putText(
                annotated,
                str(piece_id),
                (x + 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )

    return annotated
