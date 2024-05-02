# Lancer une partie

Si le serveur est déjà lancé et qu'on veut simplement connecter notre algorithme au serveur, il suffit d'exécuter la commande suivante

```bash
./start_match <url-du-server>
```

Si on ommet l'url du serveur, l'algorithme se connectera au serveur par défaut sur`http://localhost:8080`. Pour lancer ce serveur, il faut executer la commande

```bash
./start_server
```

Pour lancer l'algorithme contre lui-même, on peut utiliser rajouter l'options `-two`

```bash
./start_match  <url-du-server> -two
```

# Idee strategie naif

On découpe un tour de l'IA en plusieurs fonctions indépendantes (c'est surtout le fait qu'elles soient indépendantes qui pourra être amelioré). Le fait de faire ceci permet de travailler efficacement en groupe mais le manque de communication entre les différentes parties nuit forcément à l'IA. On a donc pas mal de fonctions ayant chacun un rôle mais travaillant parfois ensemble

## clean_golds et farm

Ces fonctions permettent d'envoyer nos peons prendre du gold. clean_golds fait un premier traitement des cases de golds qu'on voit et évite d'envoyer 2 peons sur des cases adjacentes si elles ne sont pas très intéressantes (ce qui encourage l'exploration).
farm utilise l'algorithme hongrois pour assigner nos peons à l'or.

## fuite

cette fonction permet de faire fuire nos peons s'ils sont trop proches des attaquants adverses et qu'on a pas assez de defenseurs

## explore

cette fonction gere l'exploration des peons qui ne sont pas assignés à une mine d'or grâce à un algorithme d'éclairement maximal.

## Builder : construction des châteaux et des unités (fichier `stages/castles.py`)

## `build_castle`

Cette fonctions s'occupent de la construction châteaux. On commence par prendre le contrôle d'un péon au début, afin de construire un château le plus rapidement possible en (2, 2). Puis on construit les autres châteaux en fonction de règles :

- **règle d'or:** il faut asser d'or pour construire le château (le coût d'un château pour l'instant, soit 15 or)
- **règle d'espacement:** on ne construit pas de châteaux trop proches les uns des autres (fixé à une distance de 4 cases pour l'instant)
- **règle de distance:** on ne construit pas de châteaux trop proches des bords de la carte (fixé à une distance de 2 cases pour l'instant)
- **règle de quantité:** on a une majoration du nombre de châteaux qu'on peut construire (dépend de la taille de la carte)

### `create_units`

`create_units` s'occupe de créer les unites avec nos châteaux. La construction des unités se fait selon la logique suivante :

- si on a moins de la moitié des châteaux qu'on est censé construire, on est au début de la partie donc on ne construit pas de chevaliers, on construit des péons et on garde de l'or pour construire les châteaux
- si le rapport $\dfrac{|\{ \text{chevaliers enemmis} \}|}{| \{ \text{ chevaliers alliés } \} |}$ est suppérieur à un certain pourcentage, on construit des chevaliers qu'on assigne à la défense.
- si on a "beaucoup" d'or, on construit des chevaliers qu'on assigne à l'attaque.
- sinon, on construit des péons ou on économise de l'or.

## defend

fonction qui utilise les chevaliers assignes à la défense pour défendre les péons.

## hunt, destroy_castle

On utilise les chevaliers restants pour attaquer les peons adverses :un chevalier chasse un peon adverse avec l'algorithme hongrois légèrement modifié (comme les peons adverses peuvent bouger, on peut privilégier le court terme plutôt que le coût total comme pour l'algothme hongrois) puis avec l'algorithme hongrois classique, on envoie un chevalier par chateau.
