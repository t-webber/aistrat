from apis import connection as co
from apis import players as pl
from apis.kinds import Castle, Knight, Pawn
from player.logic import client_logic as cl
from player.stages.exploration import path_simple
import numpy as np

defHeat={"Pawn":5,"Knight":-3,"Castle":15,"Eknight":9,"ChosenKnight":-10}
attHeat={"Epawn":5,"Ecastle":30}

def genMask(intensity: int):
    """Génère les masques pour les heatmap"""
    mask=np.zeros((2*intensity+1,2*intensity+1))
    for i,j in range(mask.size()):
        mask[i][j]=intensity/cl.distance(0,0,i,j)^2

maskHeatDef={i: genMask(defHeat[i]) for i in defHeat}
maskHeatAtt={i: genMask(attHeat[i]) for i in attHeat}

def addLight(map:np.array,mask,coord:tuple[int,int]):
    """Ajoute la lumière liée à une unité sur map en fonction de son masque et de sa coordonnée""" 
    center=len(mask)//2 #Division entière par 2 pour trouver le centre du mask
    for i,j in range(mask.size()):
        if 0<coord[0]+i-center<len(map) and 0<coord[1]+j-center<len(map[0]):
            map[coord[0]+i-center][coord[1]+j-center]=map[coord[0]+i-center][coord[1]+j-center]+mask[i][j]

def moveLight(map:np.array,mask,oldcoord:tuple[int,int],newcoord:tuple[int,int]):
    """Modifie la heatmap de map en fonction de son masque et de sa nouvelle coordonnée"""
    addLight(map,mask,newcoord)
    addLight(map,-mask,oldcoord)    

def heatMapDefenseGen(player: pl.Player):
    """Génère la Heat Map défensive"""
    heat_map=np.zeros((co.size_map()))
    for pawn in player.pawns:
        addLight(heat_map,maskHeatDef["Pawn"],(pawn.y,pawn.x))
    for castle in player.castles:
        addLight(heat_map,maskHeatDef["Castle"],(castle.y,castle.x))
    for eknight in player.eknights:
        addLight(heat_map, maskHeatDef["eKnight"], (eknight.y, eknight.x))
    return heat_map

def heatMapDefGenBis(player : pl.Player):
    """Génère la Heat Map défensive en calculant la heatmap aggressive supposée de l'advversaire"""
    heat_map=np.zeros((co.size_map()))
    #rajout du rayonnement des péons et chateaux alliés qui sont les cibles
    for epawn in player.pawns:
        addLight(heat_map,maskHeatAtt["ePawn"],(epawn.y,epawn.x))
    for ecastle in player.castles:
        addLight(heat_map,maskHeatAtt["eCastle"],(ecastle.y,ecastle.x))

        #rajout de l'intéret d'aller de l'avant
    for i,j in co.size_map():
        if player.id == "B":
            heat_map[i][j] += 0.3*i
        else:
            heat_map[i][j] += 0.3*(co.size_map[0]-i-1)
            
        heat_map[i][j] += heatbattle(player.eknights, player.knights, i, j, 2, 2, 2) + player._gold_map[i][j]
    return heat_map


def heatbattle(knights : list[Knight], eknights : list[Knight], x:int, y:int,a,b,c):
    """Génère la heat de combat"""
    usable_knight=[]
    usable_eknight=[]
    poid_k=0
    poid_ek=0
    for knt in knights:
        if abs(knt.x-x)+abs(knt.y-y)<=3 and not knt.used:
            usable_knight.append(knt,1/(abs(knt.x-x)+abs(knt.y-y)))
            poid_k+=1/(abs(knt.x-x)+abs(knt.y-y))
    for knt in eknights:
        if abs(knt.x-x)+abs(knt.y-y)<=3 and not knt.used:
            usable_eknight.append(knt,(1/abs(knt.x-x)+abs(knt.y-y)))
            poid_ek+=(1/abs(knt.x-x)+abs(knt.y-y))
    victory,pa,pd=cl.prediction_combat(poid_k,poid_ek)
    if (not victory) : return -1000
    return (a*pa/pd)**b - len(usable_knight)*c
    

def heatMapAttackGen(player: pl.Player):
    """Génère la Heat Map aggressive"""
    heat_map=np.zeros((co.size_map()))
    #rajout du rayonnement des péons et chateaux ennemis qui sont les cibles
    for epawn in player.epawns:
        addLight(heat_map,maskHeatAtt["ePawn"],(epawn.y,epawn.x))
    for ecastle in player.ecastles:
        addLight(heat_map,maskHeatAtt["eCastle"],(ecastle.y,ecastle.x))

        #rajout de l'intéret d'aller de l'avant
    for i,j in co.size_map():
        if player.id == "A":
            heat_map[i][j] += 0.3*i
        else:
            heat_map[i][j] += 0.3*(co.size_map[0]-i-1)
            
        heat_map[i][j] += heatbattle(player.knights, player.eknights, i, j, 2, 2, 2) + player._gold_map[i][j]
    return heat_map


def heatMapMove(player:pl.Player):
    attmap=heatMapAttackGen(player)
    defmap = heatMapDefenseGen(player)
    max = 0
    co=(-1,-1)
    tp=None
    for i in range(co.sizemap()[0]):
        for j in range(co.sizemap()[1]):
            if attmap[i][j]>
                max=attmap[i][j]
                co=(i,j)
                tp="A"
            if attmap[i][j]>
                max=attmap[i][j]
                co=(i,j)
                tp="D"
    if tp=="A":
        AttackHere(player,(i,j))
    else:
        defendHere(player,(i,j))
    attmap=heatMapAttackGen(player)
    defmap = heatMapDefenseGen(player)

""" 
La fonction qui prend en argument la case sélectionnée à défendre prend un chevalier pertinent à 
proximité et le bouge intelligemment dans sa direction, enlève le mask knight à son point de départ
 et rajoute le mask chosenknight à son arrivée
"""

def defendHere(player:pl.Player,case:tuple[int,int]):
    nearestKnights=sorted(player.knights,lambda x:cl.distance(x,case))
    i=0
    nearest=nearestKnights[i]
    movement=path_simple(nearest,case,player)
    while movement is None and i<nearestKnights.length():
        i+=1
        nearest=nearestKnights[i]
        movement=path_simple(nearest,case,player)
    if i>=nearestKnights.length():
        return
    nearest.move(movement)