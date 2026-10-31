"""Tests de validation de la configuration des devises et des chemins"""

from pathlib import Path

from src.config import (
    DEFAULT_CURRENCY,
    CURRENCY_ORDER,
    ensure_currency_directories,
    get_currency_choices,
    get_currency_directory,
    is_path_allowed_for_currency,
    is_supported_image_extension,
)


def test_default_currency_is_eur():
    """La devise par défaut doit être EUR."""
    assert DEFAULT_CURRENCY == "EUR"


def test_currency_choices_are_available():
    """Les devises disponibles doivent être présentes."""
    choices = get_currency_choices()
    assert len(choices) == 2
    assert "Euro (EUR)" in choices
    assert "Dollar taïwanais (TWD)" in choices
    assert CURRENCY_ORDER == ("EUR", "TWD")


def test_currency_directories_are_created():
    """Les dossiers de données doivent être présents pour chaque devise."""
    directories = ensure_currency_directories()
    assert directories["EUR"].exists()
    assert directories["TWD"].exists()


def test_image_path_is_valid_for_current_currency(tmp_path):
    """Seuls les fichiers du dossier de la devise autorisée sont acceptés."""
    currency_directory = get_currency_directory("EUR")
    valid_file = currency_directory / "image_valid.png"
    valid_file.parent.mkdir(parents=True, exist_ok=True)
    valid_file.write_bytes(b"fake image")

    outside_file = tmp_path / "outside.png"
    outside_file.write_bytes(b"fake image")

    assert is_path_allowed_for_currency(valid_file, "EUR") is True
    assert is_path_allowed_for_currency(outside_file, "EUR") is False


def test_supported_extensions_are_restricted():
    """Les extensions non supportées doivent être rejetées."""
    assert is_supported_image_extension("image.png") is True
    assert is_supported_image_extension("image.jpeg") is True
    assert is_supported_image_extension("image.bmp") is True
    assert is_supported_image_extension("document.txt") is False
