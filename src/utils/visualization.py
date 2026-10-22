"""Utilitaires de visualisation.

Ce module fournit des fonctions utilitaires pour afficher et tracer les
résultats intermédiaires du projet pendant le développement.
"""


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
