""" naïve algorithm """

import random as rd
import numpy as np
import api
import joueur.backbone.client_logic as cl
import joueur.castles as build
import joueur.backbone.attaque as atk


def fuite(pawns, knights, eknights, defense, player, token):
    for p in pawns:
        direc_enemies, total_enemies = cl.neighbors(p, eknights)
        if total_enemies > 0 :
            #print(knights, defense)
            direc_allies, allies_backup = cl.neighbors(p, knights)
            allies = 0
            for k in knights:
                if k[0] == p[0] and k[1] == p[1]:
                    allies += 1
            for k in defense:
                if k[0] == p[0] and k[1] == p[1]:
                    allies += 1
            #print('prediction_combat', cl.prediction_combat(total_enemies, allies+allies_backup)[0], allies + allies_backup, total_enemies)
            if cl.prediction_combat(total_enemies, allies+allies_backup)[0]:
                # si on peut perd le combat même avec les alliés on fuit
                for direc in direc_enemies:
                    if direc_enemies[direc] == 0:
                        api.move(api.PAWN, p[0], p[1], p[0] +
                                direc[0], p[1]+direc[1], player, token)
                        pawns.remove((p[0], p[1]))
                        break
            else:
                # on peut réussir à gagner le combat avec les alliés et on le fait venir
                while not cl.prediction_combat(total_enemies, allies)[0] and allies_backup > 0:
                    for direc in direc_allies:
                        if direc_allies[direc] > 0:
                            api.move(
                                api.KNIGHT, p[0]+direc[0], p[1]+direc[1], p[0], p[1], player, token)
                            if (p[0]+direc[0], p[1]+direc[1]) in knights :
                                knights.remove((p[0]+direc[0], p[1]+direc[1]))
                            allies_backup -= 1
                            break


def farm(pawns, player, token, good_gold, eknights):
    """ 
    farm gold when possible, else go to nearest avaible gold
    """

    # simple_gold = golds
    if good_gold and pawns:
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        gold_location = []
        gold_location = [ (item[0], item[1]) for item in good_gold]
        vus = []
        # je fais bouger les peons vers leur mine d'or
        for p, g in cl.hongrois_distance(pawns, gold_location):
            vus.append(pawns[p])
            y, x = pawns[p]
            i, j, _ = good_gold[g]
            gold_location.remove((i,j))
            if rd.random() > 0.5:  # pour ne pas que le peon aille toujours d'abord en haut puis à gauche
                if x > j and cl.neighbors((y, x - 1), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j and cl.neighbors((y, x + 1), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                elif y > i and cl.neighbors((y - 1, x), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i and cl.neighbors((y + 1, x), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                else:
                    api.farm(y, x, player, token)
            else:
                if y > i and cl.neighbors((y - 1, x), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i and cl.neighbors((y + 1, x), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                elif x > j and cl.neighbors((y, x - 1), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j and cl.neighbors((y, x + 1), eknights)[1] == 0:
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                else:
                    api.farm(y, x, player, token)
        for p in vus:  # j'enlève ceux que je bouge
            pawns.remove(p)


def path_one(units_to_move, other_units, eknights):
    '''Cherche le meilleur chemin pour une unité de units_to_move pour voir plus de la map'''
    # # printlen(units_to_move))
    maxscore = cl.visibility_score(api.get_visible(units_to_move+other_units))
    bestpawn = (-1, -1)
    bestmove = (-1, -1)
    for boy in units_to_move:
        stuck = 0
        moves = api.get_moves(boy[0], boy[1])
        static_units = [
            other_boy for other_boy in units_to_move if other_boy != boy]+other_units
        static_view = api.get_visible(static_units)
        for move in moves:
            new_map = api.add_visible(static_view, move)
            # # printcl.plus_gros_trou(new_map))
            score = cl.visibility_score(new_map)
            if abs(score-maxscore) <= 1:
                stuck += 1
                continue
            ennemies=cl.neighbors(move, eknights)[1]
            if score > maxscore and (ennemies == 0 \
                    or ennemies<=len(api.get_defenders(boy[0],boy[1]))):
                maxscore = score
                bestpawn = boy
                bestmove = move

    return bestpawn, bestmove


def path_trou(units_to_move, other_units, eknights):
    '''Dirige les péons vers des trous'''
    resultat = []
    everybody = units_to_move+other_units
    visibility = api.get_visible(everybody)
    trous_list = cl.trous(visibility)
    for boy in units_to_move:
        #print("On règle par un trou", boy)
        milieu_du_trou = cl.plus_proche_trou(trous_list, boy)
        moves = api.get_moves(boy[0], boy[1])
        vecteur_trou = np.array(
            (milieu_du_trou[0]-boy[0], milieu_du_trou[1]-boy[1]))
        max_trou = -1
        bestmove_trou = (0, 0)
        for move in moves:
            vector_move = np.array((move[0]-boy[0], move[1]-boy[1]))
            ennemies=cl.neighbors(move, eknights)[1]
            if np.dot(vecteur_trou, vector_move) > max_trou \
                    and (ennemies == 0 or ennemies<=len(api.get_defenders(boy[0],boy[1]))):
                bestmove_trou = move
        resultat.append((boy, bestmove_trou))
    return resultat


def path(units_to_move, other_units, eknights):
    '''Essaye de chercher un chemin d'exploration optimal pour les units_to_move pour révéler
    le maximum de la carte pour les péons. Prend en compte other_units pour la visibilité'''
    results = []
    # print("Entrées : ",units_to_move)
    strategie = 0
    for i in range(len(units_to_move)):
        if strategie == 0:
            bestpawn, bestmove = path_one(units_to_move, other_units, eknights)
            if bestpawn == (-1, -1):
                strategie = 1
                i -= 1
                continue
            results.append((bestpawn, bestmove))
            other_units.append(bestpawn)
            units_to_move = [units_to_move[i] for i in range(
                len(units_to_move)) if units_to_move[i] is not bestpawn]
        else:
            return (results,units_to_move)
    return (results,units_to_move)
    #     print('Units updated : ',units_to_move)
    # print("Résultats de path : ",results)


def explore(pawns, player, token, eknights,otherunits=[],reste_gold=()):
    """ 
    Envoie en exploration les "pawns" inactifs pour le tour
    """
    # print("J'explore")
    moves,remaining_pawns = path(pawns, otherunits, eknights)
    # print(moves)
    for one_move in moves:
        api.move(api.PAWN, one_move[0][0], one_move[0][1],
                 one_move[1][0], one_move[1][1], player, token)
    if len(reste_gold)>0:
        #print("Reste gold:",reste_gold)
        farm(remaining_pawns,player,token,reste_gold,eknights)
    if len(remaining_pawns)>0:
        moves_trou=path_trou(remaining_pawns,otherunits,eknights)
        for one_move in moves_trou:
            api.move(api.PAWN, one_move[0][0], one_move[0][1],
                    one_move[1][0], one_move[1][1], player, token)


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
        dir_knights,near_eknights=cl.neighbors(d,eknigths)
        dir_pawns,near_epawns=cl.neighbors(d,epawns)

        if near_epawns==0 and near_eknights==0:
            return

        agressiv_defenders=0
        for d2 in defense:
            agressiv_defenders+=(d2==d)

        options=[(dir_pawns[d],d) for d in dir_knights]
        options.sort()
        for op in options:
            _,direction=op
            
            for i in range(1,agressiv_defenders):
                if cl.prediction_combat(i,dir_knights[direction])[0] and not(cl.prediction_combat(near_eknights-dir_knights[direction],agressiv_defenders-i)[0]):
                    (y,x),(y2,x2)=d,(d[0]+direction[0],d[1]+direction[1])
                    for _ in range(i):
                        defense.remove(d)
                        api.move(api.KNIGHT,y,x,y2,x2,player,token)
                        cl.move_defender(y,x,y2,x2,player)
                    agressiv_defenders-=i
                    near_eknights-=dir_knights[direction]


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
    if pawns==[]:
        return defense,[]
    hongroise = cl.hongrois_distance(defense, pawns)
    utilise=[]
    arrived=[]
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
                cl.move_defender(yd,xd, yd-1, xd, player)
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
    return (defense,arrived)


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
    arrived=[]
    while (bool(left_defense) and compteur<50):
        rd.shuffle(needing_help[compteur])
        left_defense,arrived2 = move_defense(left_defense, needing_help[compteur], player, token, eknights)
        arrived+=arrived2
        compteur += 1
    return arrived

def nexturn(player, token):
    """ 
    run next turn for the current player 
        - build a castle
        - farm coins
    """   
    kinds = api.get_kinds(player)
    pawns: list[api.Coord] = kinds[api.PAWN]
    knights: list[api.Coord] = kinds[api.KNIGHT]
    eknights: list[api.Coord] = kinds[api.EKNIGHT]
    epawns: list[api.Coord] = kinds[api.EPAWN]
    fog = kinds[api.FOG]
    # liste des chevaliers attribués à la défense
    defense: list[api.Coord] = cl.defense_knights[player]
    golds: list[api.Coord] = kinds[api.GOLD]
    castles: list[api.Coord] = kinds[api.CASTLE]
    ecastles: list[api.Coord] = kinds[api.ECASTLE]
    try:
        gold = api.get_gold()[player]
    except:
        gold = 0

    # print("FOOOOG", fog)

    # pour moi, on appelle dans l'ordre :
    # defense
    # fuite qui dit au peons de fuire s'ils vont se faire tuer
    # (i.e un méchant est à côté et pas de gentil assez près pour l'aider)
    # construction forteresse
    # farm
    # explore
    # attaque
    for d in defense:
        if d not in knights:
            defense.remove(d)
        else:
            knights.remove(d)

    good_gold, bad_gold = cl.clean_golds(golds, pawns)

    left_defense=defend(pawns, defense, eknights, castles, player, token)
    agressiv_defense(left_defense,epawns,player,token,eknights)
    
    build.create_pawns(castles, player, token,
                       eknights, knights, gold, cl.defense_knights[player],
                       len(golds), len(pawns), len(fog))
    fuite(pawns, knights, eknights, defense, player, token)

    build.check_build(pawns, castles, player, token, gold)
    farm(pawns, player, token, good_gold,eknights)  # je farm d'abord ce que je vois
    # j'explore ensuite dans la direction opposée au spawn
    explore(pawns, player, token, eknights,knights+castles,bad_gold)
    while knights :
        a = len(knights)
        atk.hunt(knights, epawns, eknights, player, token)
        atk.destroy_castle(knights, ecastles, eknights, player, token)
        if len(knights)==a:
            break
