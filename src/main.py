"""Point d'entrée principal de l'application de reconnaissance de pièces"""

from src.gui.app import CoinRecognitionApp


def main() -> None:
    """Lance l'interface graphique de la phase 1 du projet   """
    app = CoinRecognitionApp()
    app.mainloop()


if __name__ == "__main__":
    main()
