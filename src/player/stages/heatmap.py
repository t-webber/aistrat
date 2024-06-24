from apis import connection as co
from apis.kinds import Castle, Knight, Pawn
from typing import TYPE_CHECKING

from player.logic import client_logic as cl
from player.stages.exploration import path_simple
import numpy as np
import matplotlib.pyplot as plt
import math


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

def heatMapDefenseGen(pawns: list[Pawn], castles : list[Castle], eknights : list[Knight]):
    """Génère la Heat Map défensive"""
    heat_map=np.zeros((co.size_map()))
    for pawn in pawns:
        addLight(heat_map,maskHeatDef["Pawn"],(pawn.y,pawn.x))
    for castle in castles:
        addLight(heat_map,maskHeatDef["Castle"],(castle.y,castle.x))
    for eknight in eknights:
        addLight(heat_map, maskHeatDef["Eknight"], (eknight[0], eknight[1]))
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


def print_heatmaps(pawns : list[Pawn], knights : list[Knight], castles : list[Castle], eknights : list[Knight], ecastles : list[Castle], epawns : list[Pawn], gold_map : list[list[int]], name : str):
    a = heatMapAttackGen(epawns, ecastles, name, knights, eknights, gold_map)
    b = heatMapDefenseGen(pawns, castles, eknights)
    plt.imshow(a, cmap='hot', interpolation='nearest')
    plt.show()
    plt.imshow(b, cmap='hot', interpolation='nearest')
    plt.show()


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
        if abs(knt[1]-x)+abs(knt[0]-y)<=2:
            usable_eknight.append(knt)
            if abs(knt[1]-x)+abs(knt[0]-y) == 0:
                poid_ek+= 1
            else:
                poid_ek+=1/(abs(knt[1]-x)+abs(knt[0]-y))

    victory,_,pa,pd=cl.prediction_combat(int(poid_k),int(poid_ek))
    
    if (not victory) : return -100
    if len(eknights) == 0 or pd == 0:
        return 0
    return (A*pa/pd)**B - len(usable_knight)*C

config=[[[3,0],[3,0],[3,0],[3,0]],[[0,0],[0,0],[0,0],[0,0]]]

def min_max_alpha_beta(depth:int,alpha:int,beta:int, base_map:list[list[int,int]],player:int):
    extrem=player*10000
    config=None
    map_id=None
    new_beta=beta
    new_alpha=alpha
    if depth>0:
        cond_init=True
        next_move=base_map.copy()
        while(map_id!=None or cond_init ):
            val,_ = min_max_alpha_beta(depth-1,new_alpha,new_beta,next_move,1-player)
            if val>= extrem and not player:
                if val >= beta:
                    return val,next_move  
                extrem = val
                config = next_move
                new_alpha=max(alpha,val)
            if val<= extrem and player:
                if val <= alpha:
                    return val,next_move  
                extrem = val
                config = next_move
                new_beta=min(new_beta,val)
            next_move,map_id = next_turn(base_map,player,map_id)
            cond_init=False
        return extrem,config
    else:
        return eval_config(base_map, base_map)

# min_max_alpha_beta(6,-100,1000,config,0)


def eval_config(config):
    score=0
    for knight in config[0]:
        if knight==[0,0]:
            score+=15
    score+=len(knight[0])*2
    score-=len(knight[1])
    return min(score,0)

def heatMapAttackGen(epawns : list[Pawn], ecastles : list[Castle], id : str, knights : list[Knight], eknights : list[Knight], gold_map : list[list[int]]):
    """Génère la Heat Map aggressive"""
    heat_map=np.zeros((co.size_map()))

        #rajout de l'intéret d'aller de l'avant
    for i in range(co.size_map()[0]):
        for j in range(co.size_map()[1]):
            if id == "A":
                heat_map[i][j] += AVANCEMENT*j
            else:
                heat_map[i][j] += AVANCEMENT*(co.size_map[0]-j-1)
            
        #rajout de l'impact des combats    
            gold_here = 0
            if gold_map[i][j] is not None:
                gold_here = 0
            heat_map[i][j] += heatbattle(knights, eknights, j, i, 2, 2, 2) + gold_here

        #rajout du rayonnement des péons et chateaux ennemis qui sont les cibles
    for epawn in epawns:
        done = False
        print(knights)
        for knight in knights:
            print(cl.distance(knight.x, knight.y, epawn[1], epawn[0]))
            if cl.distance(knight.x, knight.y, epawn[1], epawn[0]) == 1:
                addLight(heat_map,maskHeatAtt["Epawn_adj"],(epawn[0],epawn[1]))
                done = True
        if not done :
            addLight(heat_map,maskHeatAtt["Epawn"],(epawn[0],epawn[1]))
    for ecastle in ecastles:
        addLight(heat_map,maskHeatAtt["Ecastle"],(ecastle[0],ecastle[1]))

    return heat_map


# def heatMapMove(player:pl.Player):
#     while all( not knight.used for knight in player.knights):
#         attmap = heatMapAttackGen(player)
#         defmap = heatMapDefenseGen(player)
#         max = 0
#         co=(-1,-1)
#         tp=None
#         for i in range(co.sizemap()[0]):
#             for j in range(co.sizemap()[1]):
#                 if attmap[i][j]>max:
#                     max=attmap[i][j]
#                     co=(i,j)
#                     tp="A"
#                 if defmap[i][j]>max:
#                     max=attmap[i][j]
#                     co=(i,j)
#                     tp="D"
#         if tp=="A":
#             attackHere(player,(i,j))
#         else:
#             defendHere(player,(i,j))

""" 
La fonction qui prend en argument la case sélectionnée à défendre prend un chevalier pertinent à 
proximité et le bouge intelligemment dans sa direction, enlève le mask knight à son point de départ
 et rajoute le mask chosenknight à son arrivée
"""


### TO DO WITHOUT PLAYER ###

# def defendHere(player:pl.Player,case:tuple[int,int]):
#     nearestKnights=sorted(player.knights,lambda x:cl.distance(x,case))
#     i=0
#     movement=None
#     while movement is None and i<nearestKnights.length():
#         nearest=nearestKnights[i]
#         if not nearest.used:
#             movement=path_simple(nearest,case,player.eknights)
#         i+=1
#     if i>=nearestKnights.length():
#         return
#     nearest.move(movement)

# def attackHere(player:pl.Player,case:tuple[int,int],T):
#     pass
#     nearestKnights=sorted(player.knights,lambda x:cl.distance(x,case))
#     hired_knights=[]
#     target_manpower= T
#     while i<nearestKnights.length() and len(hired_knights)<target_manpower : 
#         nearest=nearestKnights[i]
#         movement=path_simple(nearest,case,player.eknights)
#         if movement!=None and not nearest.used:
#             hired_knights.append(nearest)
#         i+=1





#     if i>=nearestKnights.length():
#         return
#     nearest.move(movement)

#     """
#     units=[]
#     for i,j in range(len(map_zero)),len(map_zero[0]):
#         if map_zero[i][j] is not None:
#             for k in range(map_zero[i][j][player]):
#                 units.add((i,j))"""

def next_match(units,new_vector):
    new_units=[]
    for i,unit in enumerate(units):
        match(new_vector):
            case 1:
                new_units.append(unit[0]-1,unit[1])
            case 2:
                new_units.append(unit[0]+1,unit[1])
            case 3:
                new_units.append(unit[0],unit[1]-1)
            case 4:
                new_units.append(unit[0],unit[1]+1)
            case _: 
                new_units.append(unit)
    return new_units

def good_move(last_vector:list[int],new_move:list[int],units:list[list[int,int]]):
    origin=next_match(units,last_vector)
    new=next_match(units,new_move)
    for move,ind in iter(new_move): #On vérifie pour chaque unité déplacée
        if move!=last_vector[ind]:
            if cl.distance(*new[ind],0,0)>=cl.distance(*origin[ind],0,0):
                return False
    return True

def cinq_adder(last_vector,indice,units):
    if indice>last_vector.lenght():
        return None
    if last_vector[indice]+1 >= 5:
        last_vector[indice]=0
        return cinq_adder(last_vector,indice+1,units)
    else:
        last_vector[indice]+=1
        return last_vector

def next_turn(units:list[list[int,int]],player:int,last_vector:list[int]=None):
    if last_vector is None:
        last_vector=[0 for i in range(len(units[player]))]
        return units, last_vector
    new_move=cinq_adder(last_vector,0,units)
    while (new_move is not None) and (not good_move(last_vector,new_move,units)):
        new_move=cinq_adder(last_vector,0,units)
    if new_move is None:
        return None,None
    return next_match(units,new_move),new_move
    
    
            
