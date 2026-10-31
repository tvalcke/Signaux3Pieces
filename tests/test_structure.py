"""Tests de validation de base pour l'architecture du projet. - écrits et importés depuis ChatGPT """

import importlib

MODULES = [
    "src",
    "src.main",
    "src.preprocessing",
    "src.preprocessing.preprocessing",
    "src.detection",
    "src.detection.detection",
    "src.features",
    "src.features.extraction",
    "src.classification",
    "src.classification.classifier",
    "src.utils",
    "src.utils.visualization",
]


def test_python_modules_can_be_imported():
    """Vérifie que les modules principaux du projet s'importent sans erreur."""
    for module_name in MODULES:
        module = importlib.import_module(module_name)
        assert module is not None
