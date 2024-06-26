# Fuite

cette fonction permet de faire fuire nos peons s'ils sont trop proches des attaquants adverses et qu'on a pas assez de defenseurs

Pour son implémentation, on utilise la fonction [neighbors](../annexes/neighbors.md) qui nous permet de savoir quels sont les ennemis qui sont autour de nous et quels sont les ennemis qui sont autour de nous et quel sont les alliés qui peuvent venir en renfort.
S'il y a plus de chevaliers ennemis que la sommes des chevaliers alliés qui sont sur notre case ou une case voisine, alors l'unité fuit sur une case safe (i.e pas de chevaliers ennemis sur les cases voisines) sinon on appelle juste assez de chevaliers en renfort pour gagner le combat si jamais toutes les forces ennemies nous attaque.
