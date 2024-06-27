
# Refactor vers de l'orienté object : sécurité et mémoire

À partir de la semaine du 7 mai 2024, nous avons décider de faire un refactor total du code.

En effet, la technique actuelle était très gloutonne, en ce que, à chaque tour, l'algorithme recalcule toutes les données, et puis décide le meilleur coup à jouer à ce tour.

Nous avons travaillé environ 250 heures sur cette branche.

## Conservation des données

L'objectif de cette stratégie est de conserver la mémoire des événements et des données d'un tour au suivant, assurant ainsi une continuité et une cohérence dans le déroulement des actions. Nous avons donc trouvé la programmation orientée objet bien adéquate, en ce que nous pouvons ajouter des attributs pour stocker facilement les données. Ces objets forment des APIs faciles à utiliser et avec une facilité d'abstraction

Ces données sont ensuite exploitées pour prendre des décisions. Elles permettent également de conserver des informations sur les unités, désignés comme `targets`. En effet, tuer des péons ennemis, on a besoin de le suivre, donc de garder des informations.

De plus, ces informations sont utilisées pour retenir des détails pertinents concernant les ressources financières sous forme d'or et les divers ennemis. Cette approche vise à optimiser la gestion et l'utilisation des données pour améliorer la prise de décision et renforcer la stratégie globale du jeu.

Les données stockées sont déjà triées (e.g. on trie déjà les bons et les mauvais or avant de le stocker, même chose pour la répartition attaque défense).

### API `Player`

On a créé une classe joueur pour stocker les informations sur la partie (unités alliées, ennemis, piles d'or, etc.). On les conserve avec des informations supplémentaires. Par exemple, on stocke les or dsous forme de good gold, bad gold, et on stocke la somme totale d'or.

À chaque fois qu'on farm une pile d'or, on met à jour ces valeurs. On stocke aussi les unités alliées et ennemies, et on les met à jour à chaque tour. Ainsi, lors que ces derniers sortent de la carte, on les garde dans la liste, et cela nous permet d'avoir plus d'information que ce que le serveur nous laisse avoir.

De plus, l'API permet de gérer facilement les initialisations pour forcer des cas de figures particuliers (en choisissant si les chevaliers du serveur vont à l'attaque ou à la defense par exemple).

### API pour les unités

Les unités aussi ont chacune leur classe (qui sont en fait des API). Ces classes permettent à notre code de jamais oublié des choses primordiales, comme update à la fois le serveur et les données de `player`, ou faire des vérifications de sécurité - comme la vérification de si on a suffisamment d'or pour créer l'unité, ou si la pile d'or n'a pas déjà été utilisée.

## Sécurité

On en a profiter pour sécuriser tous les appels au serveur, en *crashant* si le serveur n'aime pas notre mouvement. En effet, dans la première version de notre code, nous partions du principe que notre code fonctionnait, mais on s'est rendu compte que ce n'était absolument pas le cas. On a pris donc beaucoup de temps à corriger toutes les erreurs de logique.

Ces erreurs consistent principalement en des mouvements illégaux (vers une case non voisine), de farm des piles d'or plus qu'une fois, ou encore bougé un même chevalier dans un même tour.

## Efficacité
