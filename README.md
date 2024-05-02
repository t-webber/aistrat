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

## check_build, create_pawns

Ces fonctions s'occupent des châteaux. check_buil en gère la construction. On en construit premièrement un en case (2,2). Puis on en construit un si on peut lorsqu'on est assez loin de nos autres chateaux et pas trop proche des bords. A noter que check_build ne déplace pas les unites dans ce but. (On peut se dire que les chateaux sont construits là où les peons sont deja en train de se deplacer et qu'on ne leur impose rien).

### création des unités

fonction create pawns

Les premières unités sont formées selon un build order prédéfinit.

Ensuite elle suivent la logique suivante:si il y a plus de chevaliers ennemis en vue que de défenseurs, on priorise la formation de défenseurs. Sinon si l'équilibre est mauvais entre attaque et défense ou attaque et péons (pas assez d'attaquant) on rééquilibre en formant des attaquant. Sinon si on a construit suffissement de château et au moins quelques péons on construit plus d'attaquant. Enfin sinon si il reste des cases non explorées ou des piles d'or disponible on forme des péons. 

## defense

### defense orienté péon 

fonction defend

La défense se repose sur un groupe de chevaliers appelés defenseurs dont la seul tache est de défendre, cette tâche est attribuée à la formation du chevalier. Le but est d'attribué aux cibles portentielles des défenseurs selon la menace qui plane sur elles. L'algorithme attribut un défenseur à chaque cible potentielle (péon, château) pour chacun des ennemis à une distance de 1 de cette dernière. Si il reste des défenseurs de libres on recommence en regardant es ennemis à une distance de 2 puis de 3 jusqu'à épuisement du groupe des défenseurs.

fonction agressiv_defense

Les défenseurs qui n'ont pas bougés (ils sont déjà arrivé à leur poste de défense et celui ci n'as pas bougé), regardent si il y a des ennemis accessibles à une distance de 1. Il les attaques si
- le combat est gagant.
- l'attaque ne met pas en danger le péon protégé lors du tour adverse.

Il est possible d'attaquer plusieurs cases depuis une seul, la priorisation se fait selon le nombre de péons détruits.

## hunt, destroy_castle

On utilise les chevaliers restants pour attaquer les peons adverses :un chevalier chasse un peon adverse avec l'algorithme hongrois légèrement modifié (comme les peons adverses peuvent bouger, on peut privilégier le court terme plutôt que le coût total comme pour l'algothme hongrois) puis avec l'algorithme hongrois classique, on envoie un chevalier par chateau.
