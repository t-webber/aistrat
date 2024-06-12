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


def heatbattle(knights : list[Knight], eknights : list[Knight], x:int, y:int,A,B,C):
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
    return (A*pa/pd)**B - len(usable_knight)*C
    
def min_max_alpha_beta(depth:int,alpha:int,beta:int, base_map:list[list[int,int]],player:int):
    max=-1000*(player)-1
    config=None
    map_id=None
    if depth>0:
        next_move=base_map.copy()
        while(map_id!=None):
            val,_ = min_max_alpha_beta(depth-1,alpha,beta,next_move,1-player)
            if val*(1-player*(-2)) > max:
                max = val*(1-player*2)
                config = next_move
            next_move,map_id = next_turn(base_map,player,map_id)
    return max,config

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
    attmap = heatMapAttackGen(player)
    defmap = heatMapDefenseGen(player)
    max = 0
    co=(-1,-1)
    tp=None
    for i in range(co.sizemap()[0]):
        for j in range(co.sizemap()[1]):
            if attmap[i][j]>max:
                max=attmap[i][j]
                co=(i,j)
                tp="A"
            if defmap[i][j]>max:
                max=attmap[i][j]
                co=(i,j)
                tp="D"
    if tp=="A":
        AttackHere(player,(i,j))
    else:
        defendHere(player,(i,j))
    attmap = heatMapAttackGen(player)
    defmap = heatMapDefenseGen(player)

""" 
La fonction qui prend en argument la case sélectionnée à défendre prend un chevalier pertinent à 
proximité et le bouge intelligemment dans sa direction, enlève le mask knight à son point de départ
 et rajoute le mask chosenknight à son arrivée
"""

def defendHere(player:pl.Player,case:tuple[int,int]):
    nearestKnights=sorted(player.knights,lambda x:cl.distance(x,case))
    i=0
    movement=None
    while movement is None and i<nearestKnights.length():
        nearest=nearestKnights[i]
        if not nearest.used:
            movement=path_simple(nearest,case,player)
        i+=1
    if i>=nearestKnights.length():
        return
    nearest.move(movement)

def attackHere(player:pl.Player,case:tuple[int,int]):
    pass
    nearestKnights=sorted(player.knights,lambda x:cl.distance(x,case))
    hired_knights=[]
    target_manpower=
    while i<nearestKnights.length() and len(hired_knights)<target_manpower : 
        nearest=nearestKnights[i]
        movement=path_simple(nearest,case,player)
        if movement!=None and not nearest.used:
            hired_knights.append(nearest)
        i+=1
    




    if i>=nearestKnights.length():
        return
    nearest.move(movement)

    """
    units=[]
    for i,j in range(len(map_zero)),len(map_zero[0]):
        if map_zero[i][j] is not None:
            for k in range(map_zero[i][j][player]):
                units.add((i,j))"""

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

def cinq_adder(last_vector,indice,units):
    if indice>last_vector.lenght():
        return None
    if last_vector[indice]+1 >= 5:
        last_vector[indice]=0
        return cinq_adder(last_vector,indice+1,units)
    elif cl.distance(*next_match[units[indice]]):
        #TODO, condition aussi, ne pas faire un move si éloignement
        
    else:
        last_vector[indice]+=1
        return last_vector

def next_turn(units:list[list[int,int]],player:int,last_vector:list[int]=None):
    if last_vector is None:
        last_vector=[0 for i in range(len(units[player]))]
        return units, last_vector
    new_move=cinq_adder(last_vector,0,units)
    if new_move is None:
        return None,None
    return next_match(units,new_move),new_move
    
    
            
        