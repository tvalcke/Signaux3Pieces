"""Tests du module de chargement d'images avec OpenCV -- écrits et importés depuis ChatGPT"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from src.acquisition.image_loader import load_image


def _write_test_image(path: Path, array: np.ndarray) -> None:
    """Écrit un tableau NumPy en image sur disque."""
    assert cv2.imwrite(str(path), array), f"Impossible d'écrire l'image de test : {path}"


def test_load_image_png_valid(tmp_path):
    """Un PNG valide doit être chargé correctement."""
    image = np.zeros((32, 48, 3), dtype=np.uint8)
    image[10:20, 12:22] = (10, 20, 30)
    path = tmp_path / "image_valid.png"
    _write_test_image(path, image)

    loaded = load_image(path)

    assert isinstance(loaded, np.ndarray)
    assert loaded.dtype == np.uint8
    assert loaded.shape == (32, 48, 3)
    np.testing.assert_array_equal(loaded, image)


def test_load_image_jpeg_valid(tmp_path):
    """Un JPEG valide doit être chargé correctement."""
    image = np.random.randint(0, 256, size=(28, 40, 3), dtype=np.uint8)
    path = tmp_path / "image_valid.jpg"
    _write_test_image(path, image)

    loaded = load_image(path)

    assert isinstance(loaded, np.ndarray)
    assert loaded.dtype == np.uint8
    assert loaded.shape == (28, 40, 3)


def test_load_image_accepts_string_path(tmp_path):
    """Le chemin peut être fourni sous forme de chaîne de caractères."""
    image = np.full((16, 16, 3), 255, dtype=np.uint8)
    path = tmp_path / "string_path.png"
    _write_test_image(path, image)

    loaded = load_image(str(path))
    assert loaded.shape == (16, 16, 3)


def test_load_image_accepts_path_object(tmp_path):
    """Le chemin peut être fourni sous forme de pathlib.Path."""
    image = np.full((12, 12, 3), 128, dtype=np.uint8)
    path = tmp_path / "path_object.png"
    _write_test_image(path, image)

    loaded = load_image(path)
    assert loaded.shape == (12, 12, 3)


def test_load_image_raises_for_missing_file(tmp_path):
    """Un chemin absent doit lever FileNotFoundError."""
    missing = tmp_path / "missing.png"

    with pytest.raises(FileNotFoundError):
        load_image(missing)


def test_load_image_raises_for_directory(tmp_path):
    """Un dossier ne doit pas être accepté comme fichier image."""
    with pytest.raises(IsADirectoryError):
        load_image(tmp_path)


def test_load_image_raises_for_empty_file(tmp_path):
    """Un fichier vide doit être refusé."""
    path = tmp_path / "empty.png"
    path.write_bytes(b"")

    with pytest.raises(ValueError, match="vide"):
        load_image(path)


def test_load_image_raises_for_corrupted_file(tmp_path):
    """Un fichier non image doit être rejeté."""
    path = tmp_path / "corrupted.bin"
    path.write_bytes(b"ceci n'est pas une image")

    with pytest.raises(ValueError, match="décodé|image valide"):
        load_image(path)


def test_load_image_accepts_accent_in_filename(tmp_path):
    """Les accents dans le nom de fichier doivent être acceptés."""
    image = np.zeros((20, 20, 3), dtype=np.uint8)
    path = tmp_path / "pièce_testé.png"
    _write_test_image(path, image)

    loaded = load_image(path)
    assert loaded.shape == (20, 20, 3)


def test_loaded_image_has_valid_dimensions_and_bgr_channels(tmp_path):
    """L'image doit avoir des dimensions positives et 3 canaux BGR."""
    image = np.arange(3 * 10 * 10, dtype=np.uint8).reshape((10, 10, 3))
    path = tmp_path / "bgr_test.png"
    _write_test_image(path, image)

    loaded = load_image(path)
    assert loaded.ndim == 3
    assert loaded.shape[2] == 3
    assert loaded.shape[0] > 0
    assert loaded.shape[1] > 0
    assert loaded.dtype == np.uint8


def test_original_image_file_is_not_modified(tmp_path):
    """Le chargement ne doit pas modifier le fichier original."""
    image = np.full((15, 15, 3), 7, dtype=np.uint8)
    path = tmp_path / "original_preserved.png"
    _write_test_image(path, image)
    original_bytes = path.read_bytes()

    loaded = load_image(path)

    assert isinstance(loaded, np.ndarray)
    assert path.read_bytes() == original_bytes

    np.testing.assert_array_equal(loaded, image)
