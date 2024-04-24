import player.logic.client_logic as cl
import api
import random as rd


def agressiv_defense(defense, epawns, player, token, eknigths):
    '''
    Looks at already on traget defense knights and attacks nearby enemys prioritizing enemy pawns while unsurring that the pawn they defend will still be defended for this turn
    Args:
        defense (list): A list of tuples representing the position of defense unit that havent moved already
        epawns (list): A list of tuples representing the positions of the enemy pawns.
        player (string): describes the playing player
        token (str): A token representing the player
        eknight (list): A list of tuples representing the positions of the enemy knights.
    Returns
        None
    '''
    for d in defense:
        dir_knights, near_eknights = cl.neighbors(d, eknigths)
        dir_pawns, near_epawns = cl.neighbors(d, epawns)

        if near_epawns == 0 and near_eknights == 0:
            return

        agressiv_defenders = 0
        for d2 in defense:
            agressiv_defenders += (d2 == d)

        options = [(dir_pawns[d], d) for d in dir_knights]
        options.sort()
        for op in options:
            _, direction = op

            for i in range(1, agressiv_defenders):
                if cl.prediction_combat(i, dir_knights[direction])[0] and not (cl.prediction_combat(near_eknights-dir_knights[direction], agressiv_defenders-i)[0]):
                    (y, x), (y2, x2) = d, (d[0] +
                                           direction[0], d[1]+direction[1])
                    for _ in range(i):
                        defense.remove(d)
                        api.move(api.KNIGHT, y, x, y2, x2, player, token)
                        cl.move_defender(y, x, y2, x2, player)
                    agressiv_defenders -= i
                    near_eknights -= dir_knights[direction]


def move_defense(defense, pawns, player, token, eknight):
    """
    Moves the knights according to their attributed pawn to defend.

    Args:
        hongroise: result of hungarian method on pawns and defense
        defense (list): A list of tuples representing the position of defense unit that havent moved already
        pawns (list): A list of tuples representing the positions of the pawns.
        player (string): describes the playing player
        token (str): A token representing the player

    Returns
        defense knights that still need to move
    """
    if pawns == []:
        return defense, []
    hongroise = cl.hongrois_distance(defense, pawns)
    utilise = []
    arrived = []
    for d, p in hongroise:
        yd, xd = defense[d]
        yp, xp = pawns[p]
        utilise.append(defense[d])
        # Pour ne pas que le defenseur aille toujours d'abord en haut puis à gauche
        if rd.random() > 0.5:
            if xd > xp and (yd, xd-1) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd, xd - 1, player, token)
                cl.move_defender(yd, xd, yd, xd - 1, player)
            elif xd < xp and (yd, xd+1) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd, xd + 1, player, token)
                cl.move_defender(yd, xd, yd, xd + 1, player)
            elif yd > yp and (yd-1, xd) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd-1, xd, player, token)
                cl.move_defender(yd, xd, yd-1, xd, player)
            elif yd < yp and (yd + 1, xd) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd + 1, xd, player, token)
                cl.move_defender(yd, xd, yd+1, xd, player)
            else:
                arrived.append(defense[d])
        else:
            if yd > yp and (yd - 1, xd) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd - 1, xd, player, token)
                cl.move_defender(yd, xd, yd-1, xd, player)
            elif yd < yp and (yd + 1, xd) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd + 1, xd, player, token)
                cl.move_defender(yd, xd, yd + 1, xd, player)
            elif xd > xp and (yd, xd - 1) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd, xd - 1, player, token)
                cl.move_defender(yd, xd, yd, xd - 1, player)
            elif xd < xp and (yd, xd + 1) not in eknight:
                api.move(api.KNIGHT, yd, xd, yd, xd + 1, player, token)
                cl.move_defender(yd, xd, yd, xd + 1, player)
            else:
                arrived.append(defense[d])

    for d in utilise:
        defense.remove(d)
    return (defense, arrived)


def defend(pawns, defense, eknights, castle, player, token):
    """
    Defends the pawns using the defense strategy against enemy knights.

    Args:
        pawns (list): A list of tuples representing the positions of the pawns.
        defense (list): A list of tuples representing the positions of the defense units.
        eknights (list): A list of tuples representing the positions of the enemy knights.
        token (str): A token representing the player.

    Returns:
        None
    """
    needing_help = [[] for i in range(50)]
    pawns = list(set(pawns.copy()+castle))  # elimination des doublons
    for i in range(len(pawns)):
        for j in range(len(eknights)):
            (y1, x1), (y2, x2) = pawns[i], eknights[j]
            d = cl.distance(x1, y1, x2, y2)
            if (d < 50):
                needing_help[d].append((y1, x1))

    # on priorise les pions selon la distance à un chevalier ennemi
    compteur = 0
    left_defense = defense.copy()
    arrived = []
    while (bool(left_defense) and compteur < 50):
        rd.shuffle(needing_help[compteur])
        left_defense, arrived2 = move_defense(
            left_defense, needing_help[compteur], player, token, eknights)
        arrived += arrived2
        compteur += 1
    return arrived
