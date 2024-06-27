# defense

## defense orientée péon

### fonction `defend`

La défense se repose sur un groupe de chevaliers appelés defenseurs dont la seul tache est de défendre, cette tâche est attribuée à la formation du chevalier. Le but est d'attribuer aux cibles portentielles des défenseurs selon la menace qui plane sur elles. L'algorithme attribut un défenseur à chaque cible potentielle (péon, château) pour chacun des ennemis à une distance de 1 de cette dernière. S'il reste des défenseurs de libres on recommence en regardant les ennemis à une distance de 2 puis de 3 jusqu'à épuisement du groupe des défenseurs.

### fonction `agressiv_defense`

Les défenseurs qui n'ont pas bougés (ils sont déjà arrivés à leur poste de défense et celui-ci n'a pas bougé), regardent s'il y a des ennemis accessibles à une distance de 1. Il les attaques si:

- le combat est gagnant.
- l'attaque ne met pas en danger le péon protégé lors du tour adverse.

Il est possible d'attaquer plusieurs cases depuis une seule, la priorisation se fait selon le nombre de péons détruits.
