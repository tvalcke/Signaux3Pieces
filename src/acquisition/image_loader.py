"""Chargement et validation d'images à partir d'un chemin disque."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def load_image(image_path: str | Path) -> np.ndarray:
    """Charge une image depuis le disque et valide sa structure.

    Paramètres
    ----------
    image_path : str | Path
        Chemin de l'image à charge

    Return
    -------
    np.ndarray
        Image couleur OpenCV en BGR, avec 3 canaux et type uint8.

    Raises
    ------
    FileNotFoundError
        Si le fichier n'existe pas.
    IsADirectoryError
        Si le chemin pointe vers un dossier.
    ValueError
        Si le fichier est vide, corrompu ou ne représente pas une image valide.
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Le fichier n'existe pas : {path}")

    if not path.is_file():
        raise IsADirectoryError(f"Le chemin pointe vers un dossier et non vers un fichier : {path}")

    file_size = path.stat().st_size
    if file_size == 0:
        raise ValueError(f"Le fichier est vide : {path}")

    raw_data = np.fromfile(path, dtype=np.uint8)
    if raw_data.size == 0:
        raise ValueError(f"Le fichier ne contient pas de données image valides : {path}")

    image = cv2.imdecode(raw_data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Le fichier ne peut pas être décodé comme image valide : {path}")

    if image.size == 0:
        raise ValueError(f"L'image décodée est vide : {path}")

    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"L'image doit être en couleur BGR avec 3 canaux, mais la forme est {image.shape}")

    if image.dtype != np.uint8:
        raise ValueError(f"Le tableau image doit être de type uint8, mais il est de type {image.dtype}")

    height, width = image.shape[:2]
    if height <= 0 or width <= 0:
        raise ValueError(f"Les dimensions de l'image sont invalides : {image.shape}")

    return image
