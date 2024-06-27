# Fuite des chateaux

Cette fonction très similaire à [fuite](../stages/fuite.md) permet au châteaux d'appeler en défense en cas d'attaque ennemie.
Elle passe prioritaire par rapport à fuite et en diffère par plusieurs aspects :

- Les chateaux ne peuvent pas bouger donc en cas de prévision de perte du combat, on essaie quand même de placer un maximum de garder nos défenseurs sur la carte en espérant que cela dissuadera l'ennemi
- De plus on ne regarde plus seulement les cases adjacentes, on regarde plus loin et on utilise une [estimation du nombre de golds](../annexes/estimation_gold.md) qu'on aura dans les tours prochains et les défenseurs que le chateau pourra produire pour lui même
