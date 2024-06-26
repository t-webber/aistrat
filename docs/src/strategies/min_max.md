# min_max

L'algorithme min_max utilisé est muni d'un élagage alpha beta ainsi que d'une restriction sur les mouvement autorisés afin d'en rendre acceptable le temps d'execution.
A cette même fin la profondeur du min_max est adapté en fonction du nombre d'unité donné en argument. Deplus le min_max s'arrête dès que la case ciblé (considérée en (0,0)par le min_max) est prise par l'attaquant.

Pour les restrictions de mouvement:
    -On empêche les chevaliers des deux partis de s'éloigner de la case ciblée.
    -Sauf si le chevalier en question est déjà sur la case ciblée
    -Sauf si cela revient à se déplacer sur un chevalier ennemi (on autorise le fait de tapper en plus sur les chevaliers ennemis même si ils ne sont pas sur l'bjectif) 

# fonction d'évaluation:

La fonction d'évaluation utilisée dans le min_max attribue un très haut score pour le fait d'avoir pris la case ciblé. 
elle retranche des points au score pour chaque chevalier ennemi encore en vie et ajoute un petit peu moins de points pour chaque chevalier allié vivant.
Plus les chevaliers allié sont proches plus il gagne de points (en quantité faible) afin de les faire s'approcher de la cible lorsque celle-ci n'est pas atteignable sur la profondeur du min_max.
On ajoute un score conséquent lorsque la case cible est atteinte avant la profondeur maximum du MinMax.