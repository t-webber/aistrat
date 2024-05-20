# Récupération de l'or

Ces fonctions permettent d'envoyer nos peons prendre du gold. Pour cela on cherche à trier les or en deux ensembles en fonction de leur importance.

C'est la fonction `clean_golds` qui effectue un premier traitement des cases de golds qu'on voit et évite d'envoyer 2 peons sur des cases adjacentes si elles ne sont pas très intéressantes (on utlise actuellemnt le critère suivant: si une grosse pile d'or est située à côté d'une pile d'or moins importance, alors la grosse pile sera privilégiée).

Cela a pour objectif de favoriser l'exploration directe de la carte. `farm` utilise ensuite [l'algorithme hongrois](../annexes/algo_hongrois.md) pour assigner nos peons à chaque tas d'or de manière optimale, d'abord uniquement les golds de bonne qualité puis après une passe d'exploration directe, ceux de moindre importance.
