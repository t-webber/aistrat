# Explore

L'exploration des péons est basé sur un système d'ordre d'actions basé sur la hiérarchie suivante:

1. Récupération des ors de bonne qualité
1. Exploration directe de la carte à 1 case
1. Récupération des ors de moindre priorité
1. Exploration à plus grande distance de la carte

Les deux algorithmes d'exploration ont des fonctionnements relativement différent

## Déplacement direct

<div style="text-align:justify;">

Pour l'exploration à courte portée, l'algorithme analyse les cases connues dues aux chevaliers et aux châteaux, ce qui sert de base au reste. On utilise pour cela la propriété qu'une unité "éclaire" autour d'elle une zone de 5x5. 

Ensuite, on ajoute à cette carte l'éclairage de tous les péons sauf un, puis celui du péon en question déplacé d'une case dans chaque direction.

Pour chaque configuration on attribue un score égal au nombre de cases connues, et on cherche quel déplacement maximise le score parmis tous les péons, puis on réitère sur la nouvelle configuration jusqu'à ce qu'on ait épuisé tous les péons disponibles ou qu'aucune nouvelle configuration n'augmente strictement notre connaissance de la carte.

Les listes des péons déplacés et de leur nouvelle position est donc exportée et les péons restants sont renvoyées pour la suite de l'algorithme
</div>

## Déplacement lointain

<div style="text-align:justify;">

Pour les déplacements à plus grande portée, on observe l'éclairage de la carte dans son état actuel qu'on souhaite analyser pour savoir vers où envoyer nos pions

Pour cela on cherche à détecter les trous dans notre connaissance de la carte. Pour chaque case inconnue on effectue donc un parcours en profondeur pour détecter les trous contigus.

Une fois ceux-ci détectés et rassemblés dans des liste, on envoie ensuite chaque péon restant vers le centre du trou le plus proche d'eux sans regarder la superposition des objectifs
</div>
