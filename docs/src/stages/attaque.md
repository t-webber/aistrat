# hunt, destroy_castle

Nous utilisons les chevaliers restants pour attaquer les péons adverses : un chevalier chasse un péon adverse avec l'algorithme hongrois légèrement modifié (comme les péons adverses peuvent bouger, on peut privilégier le court terme plutôt que le coût total comme pour l'algothme hongrois). Cela permet de faire de la disruption : les péons chassés, s'ils fuient, ne seront plus en capacité de récupérer de l'or, et l'ennemi prendra du retard sur son développement.

De plus, cette "chasse aux péons" permet d'explorer du territoire avec les chevaliers qui poursuivent les péons adverses dans leur moitié. Cette stratégie ne présente pas beaucoup de risques au niveau des pertes. En effet, on envoie les chevaliers un par un et donc en cas d'attaque de l'ennemi sur ces chevaliers, dans le pire des cas, les deux camps perdent une unité et nous ne sommes pas perdant.

De même, nous utilisons l'algorithme hongrois classique afin d'envoyer les chevaliers restants menacer les chateaux adverses. Cela permet de forcer l'adversaire à effectuer des actions qui n'étaient pas prévues pour défendre ses chateaux, et donc encore une fois retarder son développement.
