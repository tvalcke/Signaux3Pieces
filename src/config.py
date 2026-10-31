"""Configuration centralisée du projet de reconnaissance de pièces."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = PROJECT_ROOT / "data" / "raw"

CURRENCIES = {
    "EUR": {"code": "EUR", "label": "Euro", "folder_name": "EUR"},
    "TWD": {"code": "TWD", "label": "Dollar taïwanais", "folder_name": "TWD"},
}

CURRENCY_ORDER = ("EUR", "TWD")
DEFAULT_CURRENCY = "EUR"
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def get_currency_directory(currency_code: str) -> Path:
    """Retourne le dossier de données associé à la devise."""
    code = (currency_code or DEFAULT_CURRENCY).upper()
    if code not in CURRENCIES:
        raise ValueError(f"Devise inconnue : {currency_code}")
    currency_folder = CURRENCIES[code]["folder_name"]
    return DATA_ROOT / currency_folder


def get_currency_choices() -> list[str]:
    """Retourne les choix d'affichage du menu des devises."""
    return [f"{CURRENCIES[code]['label']} ({code})" for code in CURRENCY_ORDER]


def get_currency_label(currency_code: str) -> str:
    """Retourne le libellé lisible d'une devise."""
    code = (currency_code or DEFAULT_CURRENCY).upper()
    return CURRENCIES[code]["label"]


def ensure_currency_directories() -> dict[str, Path]:
    """Crée les dossiers d'images pour les devises disponibles."""
    directories = {}
    for code in CURRENCY_ORDER:
        directory = get_currency_directory(code)
        directory.mkdir(parents=True, exist_ok=True)
        directories[code] = directory
    return directories


def is_supported_image_extension(file_path: str | Path) -> bool:
    """Vérifie si l'extension du fichier est prise en charge."""
    suffix = Path(file_path).suffix.lower()
    return suffix in ALLOWED_IMAGE_EXTENSIONS


def is_path_allowed_for_currency(file_path: str | Path, currency_code: str) -> bool:
    """Vérifie qu'un fichier appartient bien au dossier de la devise active."""
    path = Path(file_path).resolve()
    allowed_directory = get_currency_directory(currency_code).resolve()

    try:
        path.relative_to(allowed_directory)
        return True
    except ValueError:
        return False
