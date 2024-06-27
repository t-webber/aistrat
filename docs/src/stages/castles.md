# Construction des châteaux et des unités

- fichier: `player/stages/castles.py`

## Construction des châteaux

- fonction: `build_castle`

Cette fonctions s'occupe de la construction châteaux. On commence par prendre le contrôle d'un péon au début, afin de construire un château le plus rapidement possible en (2, 2). Puis on construit les autres châteaux en fonction de règles :

- **règle d'or:** il faut asser d'or pour construire le château (le coût d'un château pour l'instant, soit 15 or)
- **règle d'espacement:** on ne construit pas de châteaux trop proches les uns des autres (fixé à une distance de 4 cases pour l'instant)
- **règle de distance:** on ne construit pas de châteaux trop proches des bords de la carte (fixé à une distance de 2 cases pour l'instant)
- **règle de quantité:** on a une majoration du nombre de châteaux qu'on peut construire (dépend de la taille de la carte)

## Création des unités

- fonction: `create_units`

`create_units` s'occupe de créer les unites avec nos châteaux. La construction des unités se fait selon les étapes suivantes, sachant qu'elles s'excluent (si on a pas assez d'or pour la première condition et qu'elle est vraie, on saute toutes les autres conditions pour garder l'or nécessaire pour le tour d'après) :

- si nous sommes attaqués, production de défenseurs
- si on a pas assez de châteaux
  - si on a pas assez de péons pour construire des châteaux, on en crée
- si il y a trop de péons ennemis sur les cases voisines, on crée des attaquants
- si on a pas assez de péons par rapport aux piles d'or voisines, on en crée
- sinon, on créé des attaquants
