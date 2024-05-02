# Builder : construction des châteaux et des unités (fichier `stages/castles.py`)

## `build_castle`

Cette fonctions s'occupent de la construction châteaux. On commence par prendre le contrôle d'un péon au début, afin de construire un château le plus rapidement possible en (2, 2). Puis on construit les autres châteaux en fonction de règles :

- **règle d'or:** il faut asser d'or pour construire le château (le coût d'un château pour l'instant, soit 15 or)
- **règle d'espacement:** on ne construit pas de châteaux trop proches les uns des autres (fixé à une distance de 4 cases pour l'instant)
- **règle de distance:** on ne construit pas de châteaux trop proches des bords de la carte (fixé à une distance de 2 cases pour l'instant)
- **règle de quantité:** on a une majoration du nombre de châteaux qu'on peut construire (dépend de la taille de la carte)

## `create_units`

`create_units` s'occupe de créer les unites avec nos châteaux. La construction des unités se fait selon la logique suivante :

- si on a moins de la moitié des châteaux qu'on est censé construire, on est au début de la partie donc on ne construit pas de chevaliers, on construit des péons et on garde de l'or pour construire les châteaux
- si le rapport $\dfrac{|\{ \text{chevaliers enemmis} \}|}{| \{ \text{ chevaliers alliés } \} |}$ est suppérieur à un certain pourcentage, on construit des chevaliers qu'on assigne à la défense.
- si on a "beaucoup" d'or, on construit des chevaliers qu'on assigne à l'attaque.
- sinon, on construit des péons ou on économise de l'or.
