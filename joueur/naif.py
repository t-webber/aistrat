import api
import random as rd
import joueur.backbone.client_logic as cl #Pour quand on part de aistrat

def distance(x1, y1, x2, y2):
    return abs(x1-x2)+abs(y1-y2)

def farm(pawns,golds, player, token):
    if golds and pawns:
        # affecation problem
        # choisis les mines d'or vers lesquelles vont se diriger les peons
        # pour en minimiser le nombre total de mouvements
        print(golds)
        goldLocation=dict()
        goldLocation=[(item[0],item[1]) for item in golds]
        vus = []
        for p, g in cl.hongroisDistance(pawns,goldLocation):  # Je fais bouger les peons vers leur mine d'or
            vus.append(pawns[p])
            y, x = pawns[p]
            i, j , _ = golds[g]
            if rd.random() > 0.5:  # pour ne pas que le peon aille toujours d'abord en haut puis à gauche
                if x > j:
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j:
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                elif y > i:
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i:
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                else:
                    api.farm(y, x, player, token)
            else:
                if y > i:
                    api.move(api.PAWN, y, x, y - 1, x, player, token)
                elif y < i:
                    api.move(api.PAWN, y, x, y + 1, x, player, token)
                elif x > j:
                    api.move(api.PAWN, y, x, y, x - 1, player, token)
                elif x < j:
                    api.move(api.PAWN, y, x, y, x + 1, player, token)
                else:
                    api.farm(y, x, player, token)
        for p in vus:  # j'enlève ceux que je bouge
            pawns.remove(p)


def explore(pawns, player, token):
    dico = {'A': [(0, 1), (1, 0)], 'B': [(0, -1), (-1, 0)]}
    for y,x in pawns:
        moves = []
        moves_p = api.getMoves(y, x)
        for i, j in moves_p:
            if (i-y, j-x) in dico[player]:
                moves.append((i, j))
        if moves:
            i, j = rd.choice(moves)
            api.move(api.PAWN, y, x, i, j, player, token)
        else:
            i, j = rd.choice(moves_p)
            api.move(api.PAWN, y, x, i, j, player, token)


def nexturn(player,token):
    kinds = api.getKinds(player)
    pawns = kinds[api.PAWN]
    golds = kinds[api.GOLD]

    
    ''' Pour moi, on appelle dans l'ordre : 
    fuite qui dit au peons de fuire s'ils vont se faire tuer (i.e un méchant est à côté et pas de gentil assez prêt pour l'aider)
    construction forteresse
    farm 
    explore
    defense/attaque
    '''
    farm(pawns, golds, player, token)  # je farm d'abord ce que je vois
    explore(pawns, player, token)  # j'explore ensuite dans la direction opposée au spawn
