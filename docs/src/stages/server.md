# API de connection avec le server

## Principe

Nous avons réaliser une API pour nous connecter au serveur facilement.

- Au début de la partie, on utilise une fonction `init` pour échanger les tokens de connexion avec le server.

- Au début de chaque tour, on envoie beaucoup de requêtes serveur avec `get_data` pour savoir si c'est à nous de joueur. Si c'est le cas, on stocke en global toutes les données (en récupère la 'carte' du jeu). Tous les autres appels à l'API utilise cette map et donc n'appellent pas le serveur.

- À la fin du tour, on informe le serveur avec `end_turn` qu'il peut dire à l'autre de joueur que c'est à son tour de jouer.

## Fonctions de l'API

Cette API possède de nombreuses fonctions, dont des fonctions qui permettent de récupérer la carte, ou le contraire, de récupérer les positions de tel et tel type d'unité. Elle donne l'accès notamment à des informations de l'ennemi (principalement sa position) et les cases qu'on ne voit pas (appelé `fog` dans le code). On peut également récuperer des données tels que la taille de la carte (calculée une seule fois au début de la partie), ou le joueur qui joue.
