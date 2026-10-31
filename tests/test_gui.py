"""Tests de validation des modules de l'interface graphique"""

from src.gui.app import CoinRecognitionApp


def test_gui_module_imports_cleanly():
    """L'interface graphique doit être importable sans exécuter la fenêtre."""
    assert CoinRecognitionApp.__name__ == "CoinRecognitionApp"
