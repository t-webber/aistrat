from apis import connection as con
from apis.kinds import Castle, Knight, Pawn
from typing import TYPE_CHECKING

import logic.client_logic as cl
from player.exploration import path_simple
import numpy as np
import matplotlib.pyplot as plt
import math
from player.min_max import min_max_alpha_beta_result

defHeat={"Pawn":5,"Knight":-3,"Castle":15,"Eknight":9,"ChosenKnight":-10}
attHeat={"Epawn":5,"Ecastle":30, "Epawn_adj" : 40, "Ecastle_adj" : 120}

AVANCEMENT = 0.03

def genMask(intensity: int):
    """Génère les masques pour les heatmap"""
    mask=np.zeros((2*abs(intensity)+1,2*abs(intensity)+1))
    center=len(mask[0])//2
    for i in range(2*abs(intensity)+1):
        for j in range(2*abs(intensity)+1):
            mask[i][j]=intensity/(cl.distance(center,center,i,j)+1)**2
    return mask

maskHeatDef={i: genMask(defHeat[i]) for i in defHeat}
maskHeatAtt={i: genMask(attHeat[i]) for i in attHeat}

def addLight(map:np.array,mask,coord:tuple[int,int]):
    """Ajoute la lumière liée à une unité sur map en fonction de son masque et de sa coordonnée""" 
    center=len(mask[0])//2 #Division entière par 2 pour trouver le centre du mask
    for i in range(mask[0].size):
        for j in range(mask[0].size):
            if 0<=coord[0]+i-center<len(map) and 0<=coord[1]+j-center<len(map[0]):
                map[coord[0]+i-center][coord[1]+j-center] += mask[i][j]

def moveLight(map:np.array,mask,oldcoord:tuple[int,int],newcoord:tuple[int,int]):
    """Modifie la heatmap de map en fonction de son masque et de sa nouvelle coordonnée"""
    addLight(map,mask,newcoord)
    addLight(map,-mask,oldcoord)    

def heatMapDefenseGen(pawns: list[Pawn], castles : list[Castle], eknights : list[Knight], knights : list[Knight]):
    """Génère la Heat Map défensive"""
    heat_map=np.zeros((con.size_map()))
    for pawn in pawns:
        addLight(heat_map,maskHeatDef["Pawn"],(pawn.y,pawn.x))
    for castle in castles:
        addLight(heat_map,maskHeatDef["Castle"],(castle.y,castle.x))
    for eknight in eknights:
        addLight(heat_map, maskHeatDef["Eknight"], (eknight.y, eknight.x))
    for knight in knights:
        if knight.used:
            addLight(heat_map, maskHeatDef["ChosenKnight"], (knight.y, knight.x))
    return heat_map

# def heatMapDefGenBis(pawns: list[Pawn], castles : list[Castle], knights : list[Knight], eknights : list[Knight], player : str, gold_map : list[list[int]]):
#     """Génère la Heat Map défensive en calculant la heatmap aggressive supposée de l'advversaire"""
#     heat_map=np.zeros((co.size_map()))
#     #rajout du rayonnement des péons et chateaux alliés qui sont les cibles
#     for epawn in pawns:
#         addLight(heat_map,maskHeatAtt["ePawn"],(epawn.y,epawn.x))
#     for ecastle in castles:
#         addLight(heat_map,maskHeatAtt["eCastle"],(ecastle.y,ecastle.x))

#         #rajout de l'intéret d'aller de l'avant
#     for i,j in co.size_map():
#         if player.id == "B":
#             heat_map[i][j] += 0.3*i
#         else:
#             heat_map[i][j] += 0.3*(co.size_map[0]-i-1)
            
#         heat_map[i][j] += heatbattle(eknights, knights, i, j, 2, 2, 2) + gold_map[i][j]
#     return heat_map



def heatbattle(knights : list[Knight], eknights : list[Knight], x:int, y:int,A,B,C):
    """Génère la heat de combat"""
    usable_knight=[]
    usable_eknight=[]
    poid_k=0
    poid_ek=0
    for knt in knights:
        if abs(knt.x-x)+abs(knt.y-y)<=2 and not knt.used:
            usable_knight.append(knt)
            if abs(knt.x-x)+abs(knt.y-y) == 0:
                poid_k+= 1
            else:
                poid_k+=1/(abs(knt.x-x)+abs(knt.y-y))
    for knt in eknights:
        if abs(knt.x-x)+abs(knt.y-y)<=2:
            usable_eknight.append(knt)
            if abs(knt.x-x)+abs(knt.y-y) == 0:
                poid_ek+= 1
            else:
                poid_ek+=1/(abs(knt.x-x)+abs(knt.y-y))

    victory,_,pa,pd=cl.prediction_combat(int(poid_k),int(poid_ek))
    
    if (not victory) : return -100
    if len(eknights) == 0 or pd == 0:
        return 0
    return (A*pa/pd)**B - len(usable_knight)*C


def heatMapAttackGen(epawns : list[Pawn], ecastles : list[Castle], id : str, knights : list[Knight], eknights : list[Knight], gold_map : list[list[int]]):
    """Génère la Heat Map aggressive"""
    heat_map=np.zeros(con.size_map())
        #rajout de l'intéret d'aller de l'avant
    for i in range(con.size_map()[0]):
        for j in range(con.size_map()[1]):
            if id == "A":
                heat_map[i][j] += AVANCEMENT*j
            else:
                heat_map[i][j] += AVANCEMENT*(con.size_map()[0]-j-1)
            
        #rajout de l'impact des combats    
                ### TO DO : GESTION DE LA GOLD MAP
            gold_here = 0
            if gold_map[i][j] is not None:
                gold_here = 0
            heat_map[i][j] += heatbattle(knights, eknights, j, i, 2, 2, 2) + gold_here

        #rajout du rayonnement des péons et chateaux ennemis qui sont les cibles
    for epawn in epawns:
        done = False
        print(knights)
        for knight in knights:
            print(cl.distance(knight.x, knight.y, epawn.x, epawn.y))
            if cl.distance(knight.x, knight.y, epawn.x, epawn.y) == 1:
                addLight(heat_map,maskHeatAtt["Epawn_adj"],(epawn.x,epawn[1]))
                done = True
        if not done :
            addLight(heat_map,maskHeatAtt["Epawn"],(epawn.y,epawn.x))
    for ecastle in ecastles:
        addLight(heat_map,maskHeatAtt["Ecastle"],(ecastle.y,ecastle.x))

    return heat_map




def print_heatmaps(pawns : list[Pawn], knights : list[Knight], castles : list[Castle], eknights : list[Knight], ecastles : list[Castle], epawns : list[Pawn], gold_map : list[list[int]], name : str):
    a = heatMapAttackGen(epawns, ecastles, name, knights, eknights, gold_map)
    b = heatMapDefenseGen(pawns, castles, eknights)
    plt.imshow(a, cmap='hot', interpolation='nearest')
    plt.show()
    plt.imshow(b, cmap='hot', interpolation='nearest')
    plt.show()


def heatMapMove(pawns :list[Pawn], knights : list[Knight], castles : list[Castle], epawns : list[Pawn], eknights : list[Knight], ecastles : list[Castle], gold_map : list[list[int]], id : str):
    
    while any( [not knight.used for knight in knights]) and (len(knights) != 0):
        print("A")
        attmap = heatMapAttackGen(epawns, ecastles, id, knights, eknights, gold_map)
        defmap = heatMapDefenseGen(pawns, castles, eknights, knights)

        max = 0
        co=(-1,-1)
        tp=None
        for i in range(con.size_map()[0]):
            for j in range(con.size_map()[1]):
                if attmap[i][j]>max:
                    max=attmap[i][j]
                    co=(i,j)
                    tp="A"
                if defmap[i][j]>max:
                    max=attmap[i][j]
                    co=(i,j)
                    tp="D"
        if tp=="A":
            attackHere(knights, eknights,co)
        else:
            defendHere(knights, eknights,co)

""" 
La fonction qui prend en argument la case sélectionnée à défendre prend un chevalier pertinent à 
proximité et le bouge intelligemment dans sa direction, enlève le mask knight à son point de départ
 et rajoute le mask chosenknight à son arrivée
"""


### TO DO ###

def defendHere(knights : list[Knight], eknights : list[Knight],case:tuple[int,int]):
    print("Def")
    nearestKnights=sorted(knights,key = lambda x:cl.distance(*x.coord,*case))
    i=0
    movement=None
    while movement is None and i<len(nearestKnights):
        nearest=nearestKnights[i]
        if not nearest.used:
            movement=path_simple(nearest,case,eknights)
        i+=1
    if movement is None:
        return
    if (nearest.y != case[0] or nearest.x != case[1]):
        nearest.move(movement[0], movement[1])
    else:
        nearest.used = True


def attackHere(knights : list[Knight], eknights : list[Knight],case:tuple[int,int]):
    print("Att")
    if len(eknights) == 0:
        for knight in knights:
            movement = path_simple(knight, case, eknights)
            if (movement[0] != knight.y or movement[1] != knight.x):
                knight.move(movement[0], movement[1])
            else:
                knight.used = True
        return
    nearestKnights=sorted([knight for knight in knights if not knight.used],key = lambda x:cl.distance(x.y,x.x,case[0],case[1]))
    hired_knights=[]
    i = 0
    while i<len(nearestKnights) and cl.distance(nearestKnights[i].y,nearestKnights[i].x,case[0],case[1])<4: 
        nearest=nearestKnights[i]
        hired_knights.append([nearest.x - case[1],nearest.y - case[0]])
        i+=1
    nearestEKnights=sorted(eknights,key = lambda x:cl.distance(x.y,x.x,case[0],case[1]))
    hired_Eknights=[]
    i = 0
    while i<len(nearestEKnights) and cl.distance(nearestEKnights[i].x,nearestEKnights[i][1],case[0],case[1])<4: 
        nearest=nearestEKnights[i]
        hired_Eknights.append([nearest.x - case[1], nearest.y - case[0]])
        i+=1
    next_moves=min_max_alpha_beta_result([hired_knights,hired_Eknights])
    for i, movement in enumerate(next_moves):
        if (nearestKnights[i].y != movement[0] or nearestKnights[i].x != movement[1]):
            nearestKnights[i].move(movement[0], movement[1]) 
        else:
            nearestKnights[i].used = True