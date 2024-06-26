# Stratégie 'Gloutonne'

- branche actuelle: `main`
- dernière mise à jour: `7 mai`
- acteurs impliqués: tous les membres du groupe

La stratégie gloutonne consiste en la superposition des fonctions des étapes. À chaque tour, on récupère les données grâve à l'[API de connection](../stages/server.md), puis on utilise ces données pour déterminer quelle est la meilleure action que l'on peut faire à ce tour. Glouton ne veut pas dire que chaque unité fait le meilleur coût ! C'est uniquement glouton sur le tour. Des algorithmes tels que l'algorithme hongrois permet par exemple de choisir les meilleures actions, en prenant en compte tous les péons.
