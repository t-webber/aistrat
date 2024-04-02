# Lancer une partie 

Si le serveur est déjà lancé et qu'on veut simplement connecter notre IA au serveur, il suffit d'exécuter la commande qui va lancer le script `1player.py`
```bash
./start_match <url-du-server>
```

Sinon on peut lancer le serveur avec `serveur.py` et lancer une partie entre 2 IA avec `2player.py`
# Idee strategie naif

On découpe un tour de l'IA en plusieurs fonctions indépendantes (c'est surtout le fait qu'elles soient indépendantes qui pourra être amelioré). Le fait de faire ceci permet de travailler efficacement en groupe mais le manque de communication entre les différentes parties nuit forcément à l'IA. On a donc pas mal de fonctions ayant chacun un rôle mais travaillant parfois ensemble

## clean_golds et farm

Ces fonctions permettent d'envoyer nos peons prendre du gold. clean_golds fait un premier traitement des cases de golds qu'on voit et évite d'envoyer 2 peons sur des cases adjacentes si elles ne sont pas très intéressantes (ce qui encourage l'exploration).
farm utilise l'algorithme hongrois pour assigner nos peons à l'or.


## fuite

cette fonction permet de faire fuire nos peons s'ils sont trop proches des attaquants adverses et qu'on a pas assez de defenseurs

## explore

cette fonction gere l'exploration des peons qui ne sont pas assignés à une mine d'or grâce à un algorithme d'éclairement maximal.

## check_build, create_pawns

Ces fonctions s'occupent des châteaux. check_buil en gère la construction. On en construit premièrement un en case (2,2). Puis on en construit un si on peut lorsqu'on est assez loin de nos autres chateaux et pas trop proche des bords. A noter que check_build ne déplace pas les unites dans ce but. (On peut se dire que les chateaux sont construits là où les peons sont deja en train de se deplacer et qu'on ne leur impose rien).
create_pawns s'occupe de creer les unites avec nos chateaux. Au debut on construit d'abord des peons. On priorise ensuite la defense s'il y a trop de chevaliers adverses et sinon on construit des chevaliers pour l'attaque. Il y a donc 2 types de chevaliers : ceux assignés à la defense et ceux à l'attaque.

## defend

fonction qui utilise les chevaliers assignes à la défense pour défendre les péons.

## hunt, destroy_castle

On utilise les chevaliers restants pour attaquer les peons adverses :un chevalier chasse un peon adverse avec l'algorithme hongrois légèrement modifié (comme les peons adverses peuvent bouger, on peut privilégier le court terme plutôt que le coût total comme pour l'algothme hongrois) puis avec l'algorithme hongrois classique, on envoie un chevalier par chateau.

