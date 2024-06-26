# API d'abstraction du joueur

On a créé une classe joueur pour stocker les informations sur la partie (unités alliées, ennemis, piles d'or, etc.). On les conserve avec des informations supplémentaires. Par exemple, on stocke les or dsous forme de good gold, bad gold, et on stocke la somme totale d'or.

À chaque fois qu'on farm une pile d'or, on met à jour ces valeurs. On stocke aussi les unités alliées et ennemies, et on les met à jour à chaque tour. Ainsi, lors que ces derniers sortent de la carte, on les garde dans la liste, et cela nous permet d'avoir plus d'information que ce que le serveur nous laisse avoir.

De plus, l'API permet de gérer facilement les initialisations pour forcer des cas de figures particuliers (en choisissant si les chevaliers du serveur vont à l'attaque ou à la defense par exemple).
