# Explication de la stratégie blitzkrieg

> Cette stratégie peut être trouvée sur la branche dans le git, portant le même nom.

La stratégie blitzkrieg repose sur une ligne de front verticale sur laquelle l'on repartit nos soldats.
Une fois la ligne complête, on la fait avancer pour gagner du terrain, puis une fois qu'elle est brisée, on repasse à une attaque "normale" suivant nos fonction d'attaque.

- fichier `player/stages/front_line.py`

## Variable ligne de front

- variblable `front_line`

C'est un dictionnaire, qui permet d'acceder aux lignes de fronts de 'A' et 'B'.
Chaque ligne est une liste de la taille du nombre de ligne sur la carte. Chaque élément de cette liste est une liste a deux éléments : la colonne où est placée la ligne, et le nombre de soldats sur cette cases.

## Fonctions de gestion de ligne

- fonction `create_line`

Créé la ligne pour un joueur, en la plaçant à quelques cases de son emplacement de départ.

- fonction `update_line`

Actualise le nombre de soldats sur les cases

- fonction `is_broken`

Vérifie si la ligne a été brisé. Cela sert pour savoir s'il faut lancer l'assault en brisant la formation ou non.

## Fonctions de déplacement de soldats

- fonction `move_to_line`

Déplace les soldats qui ne sont pas sur la ligne pour les faire rejoindre la ligne de front.

- fonction `equilibrate`

Répartit les soldats sur la ligne de front, pour le moment de manière naîve (on se déplace si il y a strictement moins de monde juste à coté)

- fonction `advance`

Permet de faire avancer la ligne (et tout les soldats sur cette dernière). Pour avancer en gardant la formation, on s'assure qu'il n'y a pas d'ennemis en face. Si il y a des ennemis, on préfère ne rien faire.
