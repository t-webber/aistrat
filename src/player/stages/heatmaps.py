from apis import connection as co
from apis import players as pl
from player.logic import client_logic as cl
import numpy as np

HeatDef={"Pawn":5,"Knight":-4,"Castle":10,"Eknight":8}
HeatAtt={}

def genMask(intensity: int):
    mask=np.zeros((2*intensity+1,2*intensity+1))
    for i,j in range(mask.size()):
        mask[i][j]=intensity/cl.distance(0,0,i,j)^2

maskHeat={i: genMask(defHeat[i]) for i in defHeat}

def addLight(map:np.array,nature:str,coord:(int,int)):
    mask=maskHeat[nature]
    center=(len(mask)+1)//2 #Division entière par 2 pour trouver le centre du mask
    for i,j in range(mask.size()):
        map[coord[0]+i-center][coord[1]+j-center]=map[coord[0]+i-center][coord[1]+j-center]+mask[i][j]


def defHeatMap(player: pl.Player):
    heat_map=np.zeros((co.size_map()))
    for pawn in player.pawns:
        for i,j in range(co.size_map()):
            heat_map[i][j]=HeatDef["Pawn"]/((cl.distance(i,j,pawn.y,pawn.x))^2)
    for knight in player.defense:
        for i,j in range(co.size_map()):
            heat_map[i][j]=HeatDef["Knight"]/((cl.distance(i,j,pawn.y,pawn.x))^2)
    for knight in player.attack:
        for i,j in range(co.size_map()):
            heat_map[i][j]=HeatDef["Knight"]/((cl.distance(i,j,pawn.y,pawn.x))^2)
    for castle in player.castles:
        for i,j in range(co.size_map()):
            heat_map[i][j]=HeatDef["Castle"]/((cl.distance(i,j,pawn.y,pawn.x))^2)


def attHeatMap(player : pl.Player):
    heat_map = np.zeros((co.size_map()))
    for epawn in player.epawns:
        for i,j in range(co.size_map()):
            heat_map[i][j]=HeatAtt["ePawn"]/((cl.distance(i,j,epawn.y,epawn.x))^2)
    for ecastle in player.ecastles:
        for i,j in range(co.size_map()):
            heat_map[i][j]=HeatAtt["Knight"]/((cl.distance(i,j,ecastle.y,ecastle.x))^2)
    