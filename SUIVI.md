# Suivi

## Avant le debut du projet

- Nicolas: Modification du jeu pour pouvoir jouer uniquement au clavier sur le site du jeu pour permettre un enchaînement plus rapide des parties.
- Tom : joue au jeu pour comprendre les règles et les mécanismes.

## 14/02

- Présentation du projet et des objectifs.
- Réparititon des tâches.

## 28/02

- Tom + Nicolas: Création de l'API, et premiers tests randomisés.
- Jules + Martin: Jouent aux jeux pour tester.
- Pierre: Recherches sur les IA dans les jeux au tour par tour en général.

## 13/03

- Jules: implémentation d'une fonction permettant de lancer des matchs entre IA ou contre nous si on fait des modifications + première fonction qui permet d'envoyer nos peons prendre de l'or.
- Tom: Réunion pour discuter du planning + Amélioration du planning + construction des chateaux
  random des chateaux.
- Nicolas: Structuration des fichiers avec la création d'un client_logic pour des fonctions utiles non liées à l'intéraction avec le serveur. Création d'une fonction clean_golds pour essayer de trier les or prioritaires.
- Pierre: Fin des recherches sur l'iA dans les jeux au tour par tour en général.

## 20/03

- Tom: Construction d'un premier chateau en case (2, 2) dès le début (prise de contrôle d'un péon) + Espacement entre chateaux + Créations de chevaliers
- Jules : Implémentation fuite.
- Martin et Jules : début de l'implémentation de premières fonctions pour aider à implémtner l'attaque ( neighbors, prediction combat).
- Nicolas: Implémentation d'un système de décision pour le chemin des pions ne récupérant pas d'or en cherchant des maximum locaux de visibilité et amélioration de clean_golds.
- Pierre : Debut de l'implémentation d'une fonction de répartition des chevaliers en défense.

## 26/03

- Nicolas: Retrait de la logique de points négatifs pour un éclairement trop superposé qui amenait les pions à aller dans le coin le plus proche. Ajout d'une logique supplémentaire pour path: on considère les trous dans la visibilité du plateau pour essayer d'orienter les pions ne trouvant pas de maximum local vers leur centre.
- Tom : ajout du cli `./start_match` and correction d'un timeout.
- Jules : On regarde où on va pour éviter de faire se suicider nos troupes.
- Martin et Jules : implémentation de l'attaque des nos chevaliers pour traquer les peons adverses et leurs chateaux.
- Pierre : Version finale en terme d'architecture de la fonction de répartition des chevaliers en défense.

## 02/04

- Tom: Si un péon est accessible directement, le prendre + refactor le code suite à la réunion.
- Nicolas: Correction de la fonction de détection de trous et de pathing des unités. Ajout d'une logique intermédiaire pour l'ordre des actions: farm des bons or -> déplacment optimal -> farm des mauvais or -> déplacement vers trous lointains.
- Jules : compréhension globale du programme et donc écriture du README.
- Martin: amélioration de la traque, saisi d'opportunités lorqu'on peut tuer un adversaire voisin.
- Pierre : Debug de la défense et utilisation des défenseurs inutilisés pour de possibles attaques d'opportunité.

## 09/04

- Nicolas: Changement de rôle pour la gestion de l'armée, prise en main et premières améliorations sur le mouvement des troupes avec des péons en collaboration avec Pierre.
- Pierre : fin du debug de la defense opportuniste et reflexion avec nicholas sur le mouvement combiné des chevaliers et des peons et sur la production des chevaliers plus tôt dans la partie.
- Jules : Correction de suicides d'unités
- Tom : ne pas construire des châteaux si des chevaliers ennemis sont proches.

## 24/04

- Pierre : production de plus d'attaquants, preparation de la présentation de mis parcours, traduction de commentaires pour uniformiser la langue vers le français
- Jules : Correction de fuite
- Tom: préparation de la présentation de mi-parcours + fait le diaporama

## 02/05

- Nicolas: Continuation de l'implémentation de fonctions pour jauger la partie en fonction de zones déterminées préalablemenrt entre arrière-garde et avant garde du champ de bataille ainsi que pour voir les unités perçant nos défenses
- Tom: début de l'implémenation en oop pour garder des données sur plusieurs tours + Présentation de mi-parcourt
- Jules: Ajout du fait que les attaquants explorent. Implémentation d'une interface de jeu en local, ainsi qu'un réseau test de type Q-learning qui apprend à jouer au jeu.
- Tout le monde: présentation de mi-parcours
- Pierre: reglage de la production, création d'un build order

## 07/05

- Pierre: fonction de défense visant à entraver les déplacements ennemis (non finie)
- Tout le monde: travail en collaboration pour la mise en place de la mémoire sur plusieurs tours avec l'ajout de classes
- Nicolas: Mise à jour du wiki sur l'exploration, la récupération de gold et `client_logic`. Restructuration du code des fonctions d'exploration
- Jules : Restructuration de fuite et d'attaque pour la nouvelle frome de données
- Erwan : début d'une branche "Blitzkrieg" avec développement d'une stratégie différente pour la comparer avec notre main stratégie.

## 15/05

- Tout le monde : Travail sur le rapport environnement/social
- Jules : travail en collaboration pour la même chose, ajout de documentation pour le mdbook
- Pierre : Mise au propre du rapport.

## 22/05

- Tout le monde : Travail en liveshare sur le debug de la nouvelle structure du code en poo et la mise en forme plus propre du code (meilleure documentation au sein des fichiers par exemple).

## 05/06

- Martin: fonction pour terminer les parties (pourchasser les dernières unités ennemies pour éviter d'atteindre la limite de tours)
- Nicolas, Erwan et Pierre: Théorisation et début de la programmation d'un système de heatmap pour des déplacements plus intelligents et utilisant les informations connues sur la carte
- Tom et Jules: correction des bugs de la nouvelle structure du code, sécurisation des appels au serveurs et détection des erreurs de piles vides

## 12/06

- Jules : ajout d'une estimation de l'or restant sur la carte ( qui pourrait aider pour le choix de décisions dans la prod d'unités ) + clean du code pour les deplacements d'unités dans farm et attack + restructuration de la classe joueur + orretion de fuite pour qu'il marche avec la nouvelle structure + correction d'erreur concernant l'actualisation des données d'or (le joueur B avait accès au cases d'or du joueur A car on n'actualisait pas les données dès le début).
- Martin : réalisation de l'affiche du projet
- Tom: résolution des bugs sur l'or et les mouvements non synchronisés + implémentation de la stratégie heatmap pour évaluer les risques et calculer les déplacements
- Pierre et Nicolas : Programmation des fonctions essentielles pour utiliser la Heatmap (abstraction, itération, génération)
- Erwan : Mise a jour de la branche Blitzkrieg pour pouvoir l'utiliser avec le refactor de code, et ainsi pouvoir s'en servir pour comparer différente IA entre elles et éviter les machup miroirs.

## 22/06

- Tom: amélioration de la logique des chateaux, avec des constantes empiriques facilement modifiables

## 24/06

- Jules et Nicolas : correction de l stratégie d'exploration sur la branche oop10
- Jules et Tom: correction de multiples bugs concernant la fonction pour récupérer les chevaliers ennemis d'une case, l'update des golds, la fuite. Il n'y a maintenant que les attaquants qui explorent s'ils n'ont rien à faire
- Tom : correction de bugs sur les déplacements des péons et des chevaliers, et amélioration des piles vides.
- Pierre et Nicolas : Continuation du travail sur le min-max avec application de l'itération, résolution des éventuels combats...
- Erwan : rajout d'un système de débug dans la branche heatmap pour tester les heatmaps sur des configurations personnalisées et ainsi mieux approcher les comportemants souhaité. Puis aide de Pierre et Nicolas pour le débug du min-max.
- Martin : modification de l'algorithme pour gérer la fin de partie et modification de l'attaque pour corriger des bugs apparuent avec l'orienté objet.

## 25/06

- Erwan : Finalisation du code de heatmap et aide pour le minmax. Premiers tests de heatmap avec débug et différents test sur des constante d'heuristique choisies.
- Nicolas : Aide au débug de heatmap et minmax. Commentaire de tout heatmap et minmax + nettoyage du code pour plus de lisibilité.
- Jules et Pierre: Ajout de la défense dans la branche oop10.
- Jules : réflexion sur la fonction buil_castle et début d'implémentation d'un autre choix pour la construction de châteaux. Correction d'erreurs concernant des tests dans move_safe, du fait de regarder si un gold est used avant de le considérer comme une destination par un autre péon1. On regarde maintenant aussi si un péon est used avant de le faire fuir (même si ce cas ne devrait pas arriver, il arrive parfois)
- Tom: debuggage des mouvements des unités et de la gestion d'exploration, creations d'un système de 24 match concurrents pour tester les différentes versions de l'IA.
- Tom et Jules: ajout d'outils pour mieux débuguer, notamment le debugage tour par tour et l'option debut avec start_match
- Tom: fix des tests de vérification de cohérence avec le serveur (gérer les attaquants défenseurs et les comparer avec le serveur pour savoir quand est-ce qu'ils meurent ou change de type).
- Martin : correction d'un bug de l'attaque d'opportunité, amorce d'un algorithme pour coordonner les attaquants chassant une même cible.

### 26/06
- Erwan : Amélioration des constantes de heatmap en jouant avec ces dernières, et en comparant notre IA avec celle présente actuellement sur le main.
Débuggage de heatmap et fusion propre avec oop10 pour profiter du travail sur la gestion des péons et des châteaux.s
- Martin : implémentation finale de l'attaque synchronisé et debuggage en tout genre sur l'attaque.