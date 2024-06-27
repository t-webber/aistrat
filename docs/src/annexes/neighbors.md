# la fonction neighbors

La fonction neighbors est une fonction qui a 2 entrées, la première est la case considérée et la seconde est une liste d'unités qu'on cherche.
Elle renvoie un dictionnaire avec en clé les directions autour de la case et en valeurs, la liste des unités se trouvant sur cette cases voisine et elle renvoie aussi le total des unités voisines.

Elle est utilisée pour principalement 2 raisons. La fuite et le déplacement, pour le second cas, elle sert à vérifier que le case sur laquelle on veut se déplacer n'est pas risquée, c'est-à-dire qu'il n'y a pas de chevaliers ennemis qui pourraient venir nous éliminer.
