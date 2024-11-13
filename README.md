# Build de l'application
Si on veut build l'application en .exe, il est préférable de le faire sur un environnement Windows. Pour cela, il faut installer les dépendances suivantes:
```bash
pip install pyinstaller
```

Ensuite, il suffit de se placer dans le répertoire du projet et de lancer la commande suivante:
```bash
pyinstaller --onedir --windowed --optimize=2 .\app.py
```

Le dossier avec le .exe se trouvera dans le répertoire `dist` à la racine du projet.