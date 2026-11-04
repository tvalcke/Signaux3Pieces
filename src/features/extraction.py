"""Extraction des caractéristiques géométriques et visuelles des pièces."""

import math

import cv2
import numpy as np


def _masked_mean(image: np.ndarray, center: tuple[int, int], radius: int) -> tuple[float, float, float]:
    """Calcule la moyenne BGR d'un masque circulaire."""
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.circle(mask, center, radius, 255, -1)
    mean_bgr = cv2.mean(image, mask=mask)[:3]
    return (
        round(float(mean_bgr[0]), 2),
        round(float(mean_bgr[1]), 2),
        round(float(mean_bgr[2]), 2),
    )


def _masked_hsv_mean(image_hsv: np.ndarray, mask: np.ndarray) -> tuple[float, float, float] | None:
    """Calcule la moyenne HSV sur les pixels utiles du masque, ou None si le masque est vide."""
    pixels = image_hsv[mask > 0]
    if pixels.size == 0:
        return None

    valid_pixels = pixels[pixels[:, 2] > 15]
    if valid_pixels.size == 0:
        return None

    mean_hsv = valid_pixels.mean(axis=0)
    return (
        round(float(mean_hsv[0]), 2),
        round(float(mean_hsv[1]), 2),
        round(float(mean_hsv[2]), 2),
    )


def extract_features(image: np.ndarray, circles: list[tuple[int, int, int]]) -> list[dict]:
    """Retourne les caractéristiques d'une liste de pièces détectées."""
    if not isinstance(image, np.ndarray):
        raise ValueError("L'image doit être un tableau NumPy.")

    if image.size == 0:
        return []

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("L'image doit être une image couleur BGR avec 3 canaux.")

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    features = []

    for index, (x, y, radius) in enumerate(circles, start=1):
        if radius <= 0:
            continue

        inner_radius = int(radius * 0.85)
        if inner_radius <= 0:
            inner_radius = 1

        center_radius = max(1, int(radius * 0.50))
        ring_inner = max(1, int(radius * 0.70))
        ring_outer = max(ring_inner + 1, int(radius * 0.90))

        center_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.circle(center_mask, (int(x), int(y)), center_radius, 255, -1)

        ring_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.circle(ring_mask, (int(x), int(y)), ring_outer, 255, -1)
        cv2.circle(ring_mask, (int(x), int(y)), ring_inner, 0, -1)

        mean_bgr = _masked_mean(image, (int(x), int(y)), inner_radius)
        center_bgr = _masked_mean(image, (int(x), int(y)), center_radius)
        ring_bgr = tuple(round(float(value), 2) for value in cv2.mean(image, mask=ring_mask)[:3])
        center_hsv = _masked_hsv_mean(hsv_image, center_mask)
        ring_hsv = _masked_hsv_mean(hsv_image, ring_mask)

        diameter = 2 * radius
        area = math.pi * radius ** 2

        piece = {
            "id": index,
            "x": int(round(x)),
            "y": int(round(y)),
            "radius": int(round(radius)),
            "diameter": int(round(diameter)),
            "area": round(area, 2),
            "mean_b": mean_bgr[0],
            "mean_g": mean_bgr[1],
            "mean_r": mean_bgr[2],
            "center_bgr": center_bgr,
            "ring_bgr": ring_bgr,
            "center_hsv": center_hsv,
            "ring_hsv": ring_hsv,
            "center_hsv_available": center_hsv is not None,
            "ring_hsv_available": ring_hsv is not None,
        }

        features.append(piece)

    return features
