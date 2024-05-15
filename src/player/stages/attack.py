import random as rd
from apis import connection
import player.logic.client_logic as cl


def prediction_combat(a, d):
    """
    Prédit le gaganant d'un combat

    Parameters:
        a (int): Force de l'attaquant.
        d (int): Force du defenseur.

    Returns: tuple (bool, int, int) où:
        - bool: True si l'attaquant gagne, False sinon.
        - int: nombre de pertes de l'attaquant.
        - int: nombre de pertes du défenseur.
    """
    pertes_a = 0
    pertes_d = 0
    while a > 0 and d > 0:
        pertes_a += min(a, (d + 1)//2)
        a = a - (d + 1)//2
        pertes_d += min(d, (a + 1)//2)
        d = d - (a + 1)//2
    return (d <= 0, pertes_a <= pertes_d, pertes_a, pertes_d)


def compte_soldats_ennemis_cases_adjacentes(player, case):
    """
    compte les soldats ennemis à une distance de 1 d'une case
    """
    Y, X = case
    carte = connection.get_map()
    voisins = connection.get_moves(Y, X)
    eknight = 0
    for c in voisins:
        eknight += carte[Y + c[0]][X + c[1]][player][connection.EKNIGHT]
    return eknight


def move_everyone(player, token, case, allies_voisins, knights):
    """
    Bouge tous les attaquants sur la case ciblée
    """
    Y, X = case
    for i in allies_voisins:
        y, x = i
        for j in range(allies_voisins[i]):
            connection.move(connection.KNIGHT, Y + y,
                            X + x, Y, X, player, token)
            # knights.remove((Y + y, X + x)) already removed in hunt


def prediction_attaque(player, case_attaquee, knights, eknights):
    """
    Regarde les résultats d'un combat en prenant en compte une contre attaque sur la case au tour suivant
    """
    carte = connection.get_map()
    Y, X = case_attaquee
    attaquants = cl.neighbors(case_attaquee, knights)[1]
    allies_voisins = cl.neighbors(case_attaquee, knights)[0]
    defenseurs_voisins = cl.neighbors(case_attaquee, eknights)[1]
    defenseurs = carte[Y][X][connection.other(player)][connection.KNIGHT]
    b1, b2, pertes_attaque, pertes_defense = prediction_combat(
        attaquants, defenseurs)
    if b1 and b2:
        attaquants -= pertes_attaque
        defenseurs = defenseurs_voisins
        b1, b2, pertes_attaque2, pertes_defense2 = prediction_combat(
            attaquants, defenseurs)
        return ((pertes_attaque + pertes_attaque2) >= (pertes_defense + pertes_defense2))


def attaque(player, case_attaquee, knights, eknights, token):
    allies_voisins = cl.neighbors(case_attaquee, knights)[0]
    if prediction_attaque(player, case_attaquee, knights, eknights):
        move_everyone(player, token, case_attaquee, allies_voisins, knights)


def hunt(knights, epawns, eknights, player, token):
    """ 
    chasse les péons adverses, en assignant un chevalier à un péon adverse qui va le traquer
    """
    for k in knights:
        voisins, somme = cl.neighbors(k, epawns)
        voisins_ennemis, _ = cl.neighbors(k, eknights)
        if somme:
            for i in voisins:
                if voisins[i]:
                    if not voisins_ennemis[i]:
                        y, x = k
                        connection.move(connection.KNIGHT, y, x, y +
                                        i[0], x + i[1], player, token)
                        if k in knights:  # erreur si y pas ça, mais comprend pas pk
                            knights.remove(k)
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
                    if x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y, x - 1, player, token)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y, x + 1, player, token)
                    elif y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y - 1, x, player, token)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y + 1, x, player, token)
                else:
                    if y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y - 1, x, player, token)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y + 1, x, player, token)
                    elif x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y, x - 1, player, token)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y, x + 1, player, token)
        for k in vus:  # j'enlève ceux que je bouge
            knights.remove(k)


def destroy_castle(knights, castles, eknights, player, token):
    """ 
    chasse les chateaux adverses, si possibilité de le détruire, le détruit
    """
    if knights and castles:
        # probleme d'affectation
        # choisis les chateaux vers lesquelles vont se diriger les chevaliers
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
                    if x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y, x - 1, player, token)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y, x + 1, player, token)
                    elif y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y - 1, x, player, token)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y + 1, x, player, token)
                else:
                    if y > i and cl.neighbors((y, x), eknights)[0][(-1, 0)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y - 1, x, player, token)
                    elif y < i and cl.neighbors((y, x), eknights)[0][(1, 0)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y + 1, x, player, token)
                    elif x > j and cl.neighbors((y, x), eknights)[0][(0, -1)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y, x - 1, player, token)
                    elif x < j and cl.neighbors((y, x), eknights)[0][(0, 1)] == 0:
                        connection.move(connection.KNIGHT, y, x,
                                        y, x + 1, player, token)
        for k in vus:  # j'enlève ceux que je bouge
            knights.remove(k)


def free_pawn(knights, player, token, eknights, epawns):
    """
        libère les péons bloqués par les chevaliers adverses
        """
    for knight in knights:
        for epawn in epawns:
            if cl.distance(knight[1], knight[0], epawn[1], epawn[0]) == 1 and epawn not in eknights:
                connection.move(connection.KNIGHT, knight[0], knight[1],
                                epawn[0], epawn[1], player, token)
