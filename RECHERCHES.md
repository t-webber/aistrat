# Système de classeur

Un systeme de classeur est un ensemble de règles(qui sont en fait des actions possibles) constituées de:

- une condition: représente un état globale ou local du jeu dans laquelle l'action associée est possible.
- une action: dans notre cas pour un ouvrier ce serait se déplacer à droite, à gauche, en haut, en bas, construire un château...
- un poid: l'action effectuée est sélectionée parmis les actions valides (selon la condition) aléatoirement de manière pondérée par son poid: l'usage d'un systeme de classeur n'est pas déterministe.

La création du système de classeur se fait à partir d'un algorythme génétique sur les règles (condition+action+poid) mais on pourrait ne l'appliquer qu'au poid en déterminant nous même les règles par exemple.
Les conditions pourraient porter sur des variables globales représentatnt l'état de la partie et la grille localement autour de l'élément dont on veut déterminer l'action.

# Arbre de décision

Un arbre de décision est un arbre ou chaque noeud représente une question sur l'état du jeu et chaque branche une réponse possible, en fonction de la situation on suit les branche pour arriver jusqu'à une feuille sur laquelle on pourra encoder l'action à effectuer le cas échéant. Cela revient à hardcoder une stratégie dépendant de la situation.

Les arbres de décision sont souvent utilisés pour classer des données et peuvent alors être construit par IA ou alors en se basant sur des formules d'entropie, cela s'adapte mal à notre contexte à moins de disposer d'un gigantesque jeu de parties.

L'algorithme peut être rendu non deterministe en pondérant les branches en fonction de la réponse à la question ou en utilisant un grand nombre d'arbre différents (forêt) et en séléctionnant la réponse la plus présente ou aléatoirement avec pondération selon la quantité de présence.

# Minimax

On simule toutes les parties possibles sur une profondeur n ce qui permet de creer un arbre. On évalue ensuite toutes les situations obtenues dans la partie et on leur attribue une valeur. Un étage sur deux en partant des feuilles, selon le joueur qui joue à cette étage, on conserve le fils menant à la situation la mieux notée ou la moins bien noté, ce qui donne à la racine le meilleur coup à jouer en supposant que l'évaluatio finale soit bonne et que l'adversaire joue lui aussi les meilleurs coups.

En rajoutant deux variable on peut ne pas explorer certaines branches de arbre car on sait que l'action sélectionnée ne sera pas dans cette branche. (élagage $\alpha-\beta$)

élagage meilleur avec un parcour en profondeur (et pas en largeure) mais alors l'algorithme tourne sur une profondeur fixée et non sur un temps fixé et il est difficile de définire cette profondeur.

Pour un jeu à information partielle (c'est notre cas) on peut calculer toutes les possibilitées en leur attribuant une probabilité on considère alors la partie comme un jeu non déterministe.

Dans un jeu non déterministe on ajoute un ou plusieurs étages de chance dans l'arbre représentant par exemple un lancé de dés. Au niveau du noeud de chance on fait remonter la valeur moyenne pondérée des noeuds fils.
[voir ici](https://helios2.mi.parisdescartes.fr/~bouzy/Doc/IAL3/04_IA_jeux_BB.pdf)

Trop de possibilité pour l'appliquer directement mais peut être juste sur la gestion des combats ça pourrrait peut être se faire




# Recherche arborescente Monte carlo.

On joue aléatoirement un grand nombre de partie et on note les actions ayant mené à la victoire. On construit ainsi un arbre ou chaque noeud est étiqueté par le nombre de simulations passant par ce noeud et le nombre de simulations gagantes passant par ce noeud. On choisi ensuite à partir de ces informations l'action à effectuer. C'est bien pour les jeux à haut niveau de liberté mais il risque d'y avoir trop de liberté dans ce jeu ci ou alors de nouveau sur des situations bien précise.

[voir ici](https://moodle.uphf.fr/pluginfile.php/98463/mod_resource/content/4/jeu.pdf)

# Architecture RHISC pour les systems de classeur (retourner voir au crdn)

# Système expert

On utilise un ensemble de faits et de règle (on peut fair une analogie avec la logique les fait étant des valuation d'un ensemble de variable et les règles des règles de logique) on peut utiliser comme support la logique du ppremier ordre par exemple.

On utilise ensuite des moteurs d'inférence pour résoudre le problème et prendre des décisions. Cette stratégie si je comprend bien revien à traduire la situation en formule logique ayant déjà une évaluation partielle et à le résoudre.

Cela parait compliqué à mettre en place et nécessite des recherches et réflexions poussées en logique, pour un résultat qui semble loin d'être garanti, je ne recommande pas.

# Stratégie dans un jeu 4X

(page 20)
On peut répartir les taches de l'IA sous différents niveaux. Chaque niveau décide d'actions et d'objectif qu'il va soit executer directement, soit délégué au niveau inférieur. Les niveaux sont les suivants : stratégique (gestion des ressources, des objectifs de victoire...), opérationnel (diplomacie, économie...), tactique (géographie du terrain, analyse des ennemis..)  et individuel (pathfinding des unités, combats...).

Dans notre cas, le niveau opérationnel n'existe pas. On peut cependant s'inspirer de cette répartition des prises de décisions : 
Le niveau stratégique décide de quoi défendre en priorité et où, ainsi que la priorité stratégique (attaque, défense, économie privilégié).
Le niveau tactique décide de ou placer les unités militaire, leur assignations aux zones à défendre ou attaquer, ainsi que l'assignation des péons aux piles d'or.
Le niveau individuel ne servirai qu'au pathfinding (facile).

(page 25)
On peut laisser les unités faire leur tâche de manière autonome, sans les superviser à chaque tour. Pour éviter qu'elles meurent seule, il leur suffit de rappeler leur existence lorsqu'un ennemi se rapproche.

[voir ici](https://www.theseus.fi/bitstream/handle/10024/134060/Toni_Laaveri.pdf?sequence=1)