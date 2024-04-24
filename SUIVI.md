# Suivi

## Avant le debut du projet

- (Nicolas) Modification du jeu pour pouvoir jouer uniquement au clavier sur le site du jeu pour permettre un enchaînement plus rapide des parties.

## 14/02

- Présentation du projet et des objectifs.
- Réparititon des tâches.

## 28/02

- (Tom + Nicolas) Création de l'API, et premiers tests randomisés.
- (Jules + Martin) Jouent aux jeux pour tester.
- (Pierre) Recherches sur les IA dans les jeux au tour par tour en général.

## 13/03

- Jules: implémentation d'une fonction permettant de lancer des matchs entre IA ou contre nous si on fait des modifications + première fonction qui permet d'envoyer nos peons prendre de l'or.
- Tom: Réunion pour discuter du planning + Amélioration du planning + Début construction
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
- Tom : add cli `./start_match` and fix timeout.
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

## 24/04

- Pierre : production de plus d'attaquants, preparation de la présentation de mis parcours, traduction de commentaires pour uniformiser la langue vers le français