# AISTRAT1 : Résolution algorithmique d'un jeu de stratégie

## Voir la documentation

La documentation se présente sous la forme d'un [mdbook](https://rust-lang.github.io/mdBook/index.html). Pour la consulter, il suffit de lancer la commande suivante

```bash
./docs/mdbook serve --open
```

et vous aurez une magnifique documentation détaillée de notre projet !

> À noter : la documentation est en français, mais le code est en anglais.

## Lancer une partie

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

> DISCLAIMER: Le CLI ne marche pas sur MacOS, et l'option `-two` ne marche que sur Windows.

## Présentation globale de notre algorithme

On découpe un tour de l'algorithme en plusieurs fonctions indépendantes (c'est surtout le fait qu'elles soient indépendantes qui pourra être amelioré). Le fait de faire ceci permet de travailler efficacement en groupe mais le manque de communication entre les différentes parties nuit forcément à l'algorithme. On a donc pas mal de fonctions ayant chacun un rôle mais travaillant parfois ensemble
