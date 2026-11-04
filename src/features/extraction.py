"""Extraction des caractéristiques géométriques et visuelles des pièces."""

import math

import cv2
import numpy as np


def extract_features(image: np.ndarray, circles: list[tuple[int, int, int]]) -> list[dict]:
    """Retourne les caractéristiques d'une liste de pièces détectées sur une image dl"""
    if not isinstance(image, np.ndarray):
        raise ValueError("L'image doit être un tableau NumPy.")

    if image.size == 0:
        return []

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("L'image doit être une image couleur BGR avec 3 canaux.")

    features = []

    for index, (x, y, radius) in enumerate(circles, start=1):
        if radius <= 0:
            continue

        inner_radius = int(radius * 0.85)
        if inner_radius <= 0:
            inner_radius = 1

        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (int(x), int(y)), inner_radius, 255, -1)

        mean_bgr = cv2.mean(image, mask=mask)[:3]
        diameter = 2 * radius
        area = math.pi * radius ** 2

        piece = {
            "id": index,
            "x": int(round(x)),
            "y": int(round(y)),
            "radius": int(round(radius)),
            "diameter": int(round(diameter)),
            "area": round(area, 2),
            "mean_b": round(float(mean_bgr[0]), 2),
            "mean_g": round(float(mean_bgr[1]), 2),
            "mean_r": round(float(mean_bgr[2]), 2),
        }

        features.append(piece)

    return features
