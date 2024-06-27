# Introduction

## Lancer une partie

### Sur Windows

Le CLI `./start_match` permet de lancer une partie entre deux algorithmes. Il permet de choisir quelles stratégies utiliser pour analyser les résultats d'une IA contre une autre. Pour lancer une partie, il suffit d'executer la commande suivante:

```bash
./start_match.ps1 [-url <url>] [-port <port>] [-strategy1 <strategy1>] [-strategy2 <strategy2>] [-two] [-help]       
```

Par exemple, pour faire jouer l'IA `glouton` contre l'IA `memory`, on peut executer la commande suivante:

```bash
./start_match.ps1 -strategy1 glouton -strategy2 memory -two
```

Autre exemple, pour faire tourner que l'IA `memory` sur un serveur distant, on peut executer la commande suivante:

```bash
./start_match.ps1 -strategy1 memory -url <url-du-server>
```

Avec l'option `-two`, il n'y a pas besoin de lancer le serveur.

### Sur Linux

Les CLIs ne sont pas à jour, et ne permettent que de lancer l'IA `memory` sur un serveur distant avec la commande

```bash
./start_match <url-du-server>
```

## Lancer le serveur

Cette partie concerne `Windows` et `Linux`.

On peut aussi uniquement lancer le serveur, avec la commande suivante:

```bash
./start_server
```

On peut préciser le port sur lequel il est lancé, avec

```bash
./start_server 8080
```

## Présentation globale de notre algorithme

On découpe un tour de l'algorithme en plusieurs fonctions indépendantes (c'est surtout le fait qu'elles soient indépendantes qui pourra être amelioré). Le fait de faire ceci permet de travailler efficacement en groupe mais le manque de communication entre les différentes parties nuit forcément à l'algorithme. On a donc pas mal de fonctions ayant chacun un rôle mais travaillant parfois ensemble
