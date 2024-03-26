import random as rd
import api
import joueur.backbone.client_logic as cl


def prediction_combat(a, d):
    """
    Predicts the winner of a fight

    Parameters:
        a (int): Force of attacker.
        d (int): Force du defender.

    Returns: tuple (bool, int, int) where:
        - bool: True if the attacker wins, False otherwise.
        - int: Number of losses for the attacker.
        - int: Number of losses for the defender.
    """
    pertes_a = 0
    pertes_d = 0
    while a > 0 and d > 0:
        pertes_a += min(a, (d + 1)//2)
        a = a - (d + 1)//2
        pertes_d += min(d, (a + 1)//2)
        d = d - (a + 1)//2
    return (d <= 0, pertes_a <= pertes_d, pertes_a, pertes_d)


def neighbors(case, knights):
    """
    return the number of knights in the 4 directions of a case
    """
    dir_case = {(0, 1): 0, (1, 0): 0, (0, -1): 0, (-1, 0): 0}
    for k in knights:
        if (k[0]-case[0], k[1]-case[1] in dir_case):
            dir_case[(k[0]-case[0], k[1]-case[1])] += 1
    return dir_case


def compte_soldats_ennemis_cases_adjacentes(player, case):
    """
    compte les soldats ennemis à une distance de 1 d'une case
    """
    Y, X = case
    carte = api.get_map()
    voisins = api.get_moves(Y, X)
    eknight = 0
    for c in voisins:
        eknight += carte[Y + c[0]][X + c[1]][player][api.EKNIGHT]
    return eknight


def move_everyone(player, token, case, allies_voisins, knights):
    """
    Bouge tous les attaquants sur la case ciblée
    """
    Y, X = case
    for i in allies_voisins:
        y, x = i
        for j in range(allies_voisins[i]):
            api.move(api.KNIGHT, Y + y, X + x, Y, X, player, token)
            # knights.remove((Y + y, X + x)) already removed in hunt


def attaque(player, case_attaquee, knights, eknights, token):
    carte = api.get_map()
    Y, X = case_attaquee
    attaquants = cl.neighbors(case_attaquee, knights)[1]
    allies_voisins = cl.neighbors(case_attaquee, knights)[0]
    defenseurs_voisins = cl.neighbors(case_attaquee, eknights)[1]
    defenseurs = carte[Y][X][api.other(player)][api.KNIGHT]
    b1, b2, pertes_attaque, pertes_defense = prediction_combat(
        attaquants, defenseurs)
    if b1 and b2:
        attaquants -= pertes_attaque
        defenseurs = defenseurs_voisins
        b1, b2, pertes_attaque2, pertes_defense2 = prediction_combat(
            attaquants, defenseurs)
        if (pertes_attaque + pertes_attaque2) > (pertes_defense + pertes_defense2):
            move_everyone(player, token, case_attaquee,
                          allies_voisins, knights)


def hunt(knights, epawns, eknights, player, token):
    """ 
    chasse les péons adverses
    """
    # printknights, epawns)
    if knights and epawns:
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        vus = []
        for k, ep in cl.hongrois_distance(knights, epawns):
            vus.append(knights[k])
            y, x = knights[k]
            i, j = epawns[ep]
            if abs(y - i) + abs(x - j) == 1:
                attaque(player, (i, j), knights, eknights, token)
            else:
                if rd.random() > 0.5:  # pour ne pas que le chevalier aille toujours d'abord en haut puis à gauche
                    if x > j and cl.neighbors((y, x - 1), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y, x - 1, player, token)
                    elif x < j and cl.neighbors((y, x + 1), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y, x + 1, player, token)
                    elif y > i and cl.neighbors((y - 1, x), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y - 1, x, player, token)
                    elif y < i and cl.neighbors((y + 1, x), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y + 1, x, player, token)
                else:
                    if y > i and cl.neighbors((y - 1, x), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y - 1, x, player, token)
                    elif y < i and cl.neighbors((y + 1, x), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y + 1, x, player, token)
                    elif x > j and cl.neighbors((y, x - 1), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y, x - 1, player, token)
                    elif x < j and cl.neighbors((y, x + 1), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y, x + 1, player, token)
        for k in vus:  # j'enlève ceux que je bouge
            knights.remove(k)


def destroy_castle(knights, castles, eknights, player, token):
    """ 
    chasse les péons adverses
    """
    # printknights, castles)
    if knights and castles:
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        vus = []
        for k, ep in cl.hongrois_distance(knights, castles):
            vus.append(knights[k])
            y, x = knights[k]
            i, j = castles[ep]
            if abs(y - i) + abs(x - j) == 1:
                attaque(player, (i, j), knights, eknights, token)
            else:
                if rd.random() > 0.5:  # pour ne pas que le chevalier aille toujours d'abord en haut puis à gauche
                    if x > j and cl.neighbors((y, x - 1), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y, x - 1, player, token)
                    elif x < j and cl.neighbors((y, x + 1), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y, x + 1, player, token)
                    elif y > i and cl.neighbors((y - 1, x), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y - 1, x, player, token)
                    elif y < i and cl.neighbors((y + 1, x), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y + 1, x, player, token)
                else:
                    if y > i and cl.neighbors((y - 1, x), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y - 1, x, player, token)
                    elif y < i and cl.neighbors((y + 1, x), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y + 1, x, player, token)
                    elif x > j and cl.neighbors((y, x - 1), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y, x - 1, player, token)
                    elif x < j and cl.neighbors((y, x + 1), eknights)[1] == 0:
                        api.move(api.KNIGHT, y, x, y, x + 1, player, token)
        for k in vus:  # j'enlève ceux que je bouge
            knights.remove(k)
