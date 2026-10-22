# Démarrer le projet après le pull initial


## 1) Aller dans le dossier du projet

```bash
cd /home/sleipnir/Bureau/Efek/EphecBac3/signaux3/Signaux3Pieces
```

## 2) Créer le venv s’il n’existe pas

```bash
python3 -m venv .venv
```

## 3) Activer le venv

```bash
source .venv/bin/activate
```

Tu devrais voir quelque chose comme :

```bash
(.venv) 
```

## 4) Installer les dépendances

```bash
python -m pip install -r requirements.txt
```

## 5) Vérifier que ça marche

```bash
pytest -q
```

Résultat attendu :

```bash
1 passed
```

## 6) Lancer le projet

```bash
python src/main.py
```

Pour le moment, c’est juste une base vide, prêt à accueillir les prochaines étapes.

## 7) Quand tu as fini

```bash
deactivate
```

## 8) Important

- `.venv` est local, il ne doit pas être poussé sur GitHub.
- On ne travaille jamais directement avec Python système.
- Le projet doit tourner dans le venv.

## 9) Workflow simple pour tous les jours

```bash
cd /home/sleipnir/Bureau/Efek/EphecBac3/signaux3/Signaux3Pieces
source .venv/bin/activate
pytest -q
python src/main.py
```

Voilà, c’est le workflow simple après un pull du repo.
