## fonctions annexes

prédiction_combat : Fonction qui sert à calculer le résultat d'une attaque



## hunt, destroy_castle

On utilise les chevaliers restants après attribution des chevaliers à la défense pour attaquer les péons adverses :un ou plusieurs chevaliers chassent un péon adverse avec l'algorithme hongrois légèrement modifié (comme les péons adverses peuvent bouger, on peut privilégier le court terme plutôt que le coût total comme pour l'algothme hongrois). Tant qu'on a des chevaliers inutilisés, on lui attribu une cible (péon ou chateau). Avec l'algorithme hongrois classique, on envoie les chevaliers menacer les chateaux. La fonction destroy_castle fait bouger les chevaliers vers leur cible, tandis que hunt attribue les péons aux chevaliers qui vont faire un mouvement vers leur cible, cependant, le relais est ensuite pris par sync_atk qui coordonne le mouvement des unités.
Chasser les péons et les chateaux, même si on arrive pas à détruire la cible, permet de faire de la disruption, c'est à dire forcer l'adversaire à faire des mouvements imprévus (créer des chevaliers pour défendre des chateaux, faire fuire les péons qui ne pourront alors plus récupérer d'or). Cela permet d'essayer de prendre un avantage sur l'adversaire.

## sync_atk

Cette fonction a pour but de synchroniser les déplacements des chevaliers qui chassent les péons ennemis. Le but est de réduire les possibilités de déplacement du péons adversaire et de finir par le conicer, dans le pire des cas contre un bord ou un coin de la carte. Pour cela, on essaye de placer deschevaliers sur différentes colonnes ou lignes adjacentes à celles du péons. Par exemple, si un péon et en (2,6), on a pour objectif de placer des chevaliers sur les colonnes 5,6,7 et les lignes 1,2,3. En ayant au moins 2 colonnes ou 2 lignes différentes ocupés, on est sûr de finir par coincer le péon.

## gestion des fin de parties

Pour terminer les parties et chasser les dernières troupes ennemies, une fois tous les chateaux adverses détruits, on réutilise hunt et sync_atk en donnant comme unités cibles les chevaliers adverses qu'on va ensuite pourchasser avec nos unités. On ne fait l'attaque que si on ne perd pas plus d'unités que l'adversaire. De cette manière, on peut finir les parties, pas besoin d'atteindre la limite de tours pour gagner aux points.