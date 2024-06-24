# Heatmap

Le principe de l'utilisation de heatmap consiste à utiliser des heatmaps d'attaque et de défense pour décider des déplacement de nos soldats.
On génère deux heatmaps :

    la heatmap d'attaque
        -rajout d'importace des cases si péons ou chateaux ennemis sur place ou a proximité
        -rajour d'importance si les cases sont en avant sur la carte (pour favoriser l'aggressivité)
        -calcul de potentiel combat sur les cases d'arrivée, si le combat est perdu, on a une importance de -infini, sinon on rajoute de l'importance proportionnelement au rapport de victoir (ennemis tué/alliés perdu)

    la heatmap de défense : 2 choix possible
        -soit une heatmap basique:
            -rajout d'importance si péon ou chateaux alliés proche
            -rajout d'importance si ennemis à proximité
            -diminution de l'importance si des soldats alliés sont déjà pret à défendre cette case

        -sinon, on calcul une supposé heatmap d'attaque ennemie, avec les informations que l'on possède.
        On se sert ensuite de cette heatmap pour voir les zones que l'on pense avoir besoin de défendre


Pour le calcul des déplacement, on regarde les cases les plus importantes, quelles soient en attaques ou en défenses.
On parcours ces cases dans l'ordre décroissant d'importance, chaque case va "réserver" des soldats pour elle-même, puis update les heatmaps en conséquence.

Cette stratégie nous permet d'être plus flexible, car les soldats ne sont pas cantonner à un rôle mais peuvent changer d'objectif stratégique en fonction de l'état
de la partie. En contrepartie, il nous faut beaucoup plus de temps de calcul (même si cela reste raisonnable), et il nous faudra un grand travail d'expérimmentation pour trouver les bonnes constantes à utiliser pour avoir les bon comportement voulus.


# Debug des heatmap

La branche heatmap contient maintenant un système de débug, qui permet d'initialiser des position personnalisé et de calculer les heatmaps dans ces positions. Cela nous a permis de débug les heatmap, mais aussi de faire de nombreux test sur des constantes d'heuristiques. On peut ainsi s'approcher des comportements souhaité en faisant varier les constantes, et le débug permet de tester rapidement ces modifications sans avoir à lancer des parties en boucle en espérant obtenir la position souhaité.