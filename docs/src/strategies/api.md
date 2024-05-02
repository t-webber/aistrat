# Réalisation d'APIs

## API de connection avec le server

- fichier: `api.py`

Nous avons réaliser une API pour nous connecter au serveur facilement. Cette API possède notamment

- la fonction `init`, qui permet de se connecter au serveur à une URL donnée.
- la fonction `get_data`, qui permet de mettre à jour les données de la partie. Cette fonction est executée à chaque tour.
- la fonction `get_kinds`, qui permet de récupérer les coordonnées de toutes unités, châteaux, qu'ils soient alliés ou ennemis. Elle permet aussi de récupérer les coordonnées des cases inaccessibles, que nous avons nommées _"brouillard"_ dans le code.
- Diverses fonctions pour connaître les cases adjacentes, les cases accessibles, les cases inaccessibles, les cases de l'ennemi, les cases de l'allié, etc.

## API pour la logique communément utilisée

- fichier: `player/logic/client_logic.py`
