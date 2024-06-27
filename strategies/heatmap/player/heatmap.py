from apis import connection as con
from apis.kinds import Castle, Knight, Pawn
from typing import TYPE_CHECKING

import logic.client_logic as cl
from player.exploration import path_simple_bis
import numpy as np
import matplotlib.pyplot as plt
import math
from player.min_max_quick import min_max_alpha_beta_result



IMPORTANCE_ATT = 5
AVANCEMENT = 0.03
VAL_GOLD = 1/300

defHeat={"Pawn":3,"Knight":-2,"Castle":5,"Eknight":30,"ChosenKnight":-50}
attHeat={"Epawn":10*IMPORTANCE_ATT,"Ecastle":30*IMPORTANCE_ATT, "Epawn_adj" : 100*IMPORTANCE_ATT, "Ecastle_adj" : 120*IMPORTANCE_ATT, "Eknight":50*IMPORTANCE_ATT}




def genMask(intensity: int):
    """Génère les masques pour les heatmap"""
    mask=np.zeros((int(2*abs(intensity))+1,int(2*abs(intensity))+1)) #Crée une carte de coté 2*taille de l'éclairage + 1 centré sur la "lampe"
    center=len(mask[0])//2
    for i in range(int(2*abs(intensity))+1): #Dans la portée du masque...
        for j in range(int(2*abs(intensity))+1):
            mask[i][j]=intensity/(cl.distance(center,center,i,j)+1)**2 #Y inscrit une intensité en Max/(Distance^2)
    return mask

maskHeatDef={i: genMask(defHeat[i]) for i in defHeat}
maskHeatAtt={i: genMask(attHeat[i]) for i in attHeat}

def addLight(map:np.array,mask,coord:tuple[int,int], factor : int):
    """Ajoute la lumière liée à une unité sur map en fonction de son masque et de sa coordonnée""" 
    center=len(mask[0])//2 #Division entière par 2 pour trouver le centre du mask
    for i in range(mask[0].size):
        for j in range(mask[0].size):
            if 0<=coord[0]+i-center<len(map) and 0<=coord[1]+j-center<len(map[0]): #A l'intérieur du masque inter l'intérieur de la carte...
                map[coord[0]+i-center][coord[1]+j-center] += mask[i][j]*factor #Ajoute la lumière contenue dans le masque

def moveLight(map:np.array,mask,oldcoord:tuple[int,int],newcoord:tuple[int,int]):
    """Modifie la heatmap de map en fonction de son masque et de sa nouvelle coordonnée"""
    addLight(map,mask,newcoord, 1) #Ajoute la nouvelle lumière à la bonne coordonnée
    addLight(map,-mask,oldcoord, 1) #La retire à l'ancienne

def heatMapDefenseGen(pawns: list[Pawn], castles : list[Castle], eknights : list[Knight], knights : list[Knight]):
    """Génère la Heat Map défensive"""
    heat_map=np.zeros((con.size_map()))
    for pawn in pawns:
        addLight(heat_map,maskHeatDef["Pawn"],(pawn.y,pawn.x), 1) #Les péons
    for castle in castles:
        addLight(heat_map,maskHeatDef["Castle"],(castle.y,castle.x), 1) #Les châteaux
    for eknight in eknights:
        for unit in pawns + castles:
            if cl.distance(*unit.coord, *eknight.coord) < 2:
                addLight(heat_map, maskHeatDef["Eknight"], (unit.y, unit.x), 1/(0.01 + cl.distance(*unit.coord, *eknight.coord))) #Les chevaliers ennemis placent leur lumière sur les cases a protéger.
    for knight in knights:
        if knight.used:
            addLight(heat_map, maskHeatDef["ChosenKnight"], (knight.y, knight.x), 1) #Les chevaliers alliés déjà utilisés
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
        if abs(knt.x-x)+abs(knt.y-y)<=2 and not knt.used: #Si le chevalier est à moins de 2 et utilisables...
            usable_knight.append(knt) #On l'ajoute à notre liste d'intérêt
            if abs(knt.x-x)+abs(knt.y-y) == 0:
                poid_k+= 1 #Si déjà sur la case, notre puissance instantanée augmente de son nombre...
            else:
                poid_k+=1/(abs(knt.x-x)+abs(knt.y-y)) #et à distance on pondère par la norme 1
    for knt in eknights:
        if abs(knt.x-x)+abs(knt.y-y)<=2: #On compte de manière identique la force ennemie
            usable_eknight.append(knt)
            if abs(knt.x-x)+abs(knt.y-y) == 0:
                poid_ek+= 1
            else:
                poid_ek+=1/(abs(knt.x-x)+abs(knt.y-y))

    victory,_,pa,pd=cl.prediction_combat(int(poid_k),int(poid_ek)) 
    #On prédit ensuite le résultat du combat avec la partie entière des forces présentes

    if (not victory) : return -10000 #Si l'estimation nous annonce une défaite, on n'attaque absolument pas
    if len(eknights) == 0 or pd == 0:
        return 0 #Si aucun ennemi, neutralité
    return (A*pa/pd)**B - len(usable_knight)*C #Sinon on donne un score à l'opportunité


def heatMapAttackGen(epawns : list[Pawn], ecastles : list[Castle], id : str, knights : list[Knight], eknights : list[Knight], gold_map : list[list[int]]):
    """Génère la Heat Map aggressive"""
    corner = (0,0)
    if id == "B":
        corner = (con.size_map()[0]-1, con.size_map()[1]-1)
    heat_map=np.zeros(con.size_map())
        #rajout de l'intéret d'aller de l'avant
    for i in range(con.size_map()[0]): #On ajout un incentive à aller vers le camps adverse
        for j in range(con.size_map()[1]):
            if id == "A":
                heat_map[i][j] += AVANCEMENT*j #Avancement est la quantification de l'avantage de rapprochement
            else:
                heat_map[i][j] += AVANCEMENT*(con.size_map()[0]-j-1)
            
        #rajout de l'impact des combats
            gold_here = 0
            if gold_map[i][j] is None:
                gold_here = 0
            elif type(gold_map[i][j]) is not int:
                gold_here=gold_map[i][j].gold*VAL_GOLD #On pondère l'or connu par un gros chiffre
            heat_map[i][j] += heatbattle(knights, eknights, j, i, 2, 2, 2) + gold_here #Et on l'utilise aussi comme pondération

        #rajout du rayonnement des péons et chateaux ennemis qui sont les cibles
        #Les cibles sont moins importantes si elles sont loins, permettant ainsi d'avoir une structuration du front
    for epawn in epawns:
        done = False
        for knight in knights:
            if cl.distance(knight.x, knight.y, epawn.x, epawn.y) == 1: #Si un chevalier est proche d'un péon ennemi...
                addLight(heat_map,maskHeatAtt["Epawn_adj"],(epawn.y,epawn.x), 1) #... on ajoute de la lumière associée
                done = True
        if not done : #Si aucun chevalier à côté, on ajoute une autre lumière plus faible
            addLight(heat_map,maskHeatAtt["Epawn"],(epawn.y,epawn.x), 1/(1 + (cl.distance(*epawn.coord, *corner))**(1/4)))
    for ecastle in ecastles:
        addLight(heat_map,maskHeatAtt["Ecastle"],(ecastle.y,ecastle.x), 1/(1+ (cl.distance(*ecastle.coord, *corner))**(1/4))) #Et on considère aussi les châteaux à attaquer

    for eknight in eknights:
        addLight(heat_map,maskHeatAtt["Eknight"],(eknight.y,eknight.x), 1/(1+ (cl.distance(*eknight.coord, *corner))**(1/4))) #Et on considère aussi les knights ennemis.

    return heat_map


def print_heatmaps(pawns : list[Pawn], knights : list[Knight], castles : list[Castle], eknights : list[Knight], ecastles : list[Castle], epawns : list[Pawn], gold_map : list[list[int]], name : str):
    '''
    Affiche les heatmaps associée à la configuration donnée en entrée

    Sert essentiellement pour le debugging
    '''
    a = heatMapAttackGen(epawns, ecastles, name, knights, eknights, gold_map)
    b = heatMapDefenseGen(pawns, castles, eknights, knights)
    for i in range(len(a)):
        for j in range(len(a[0])):
            a[i][j] = max(a[i][j], -5)
            b[i][j] = max(b[i][j], -5)

    plt.imshow(a, cmap='hot', interpolation='nearest')
    plt.show()
    plt.imshow(b, cmap='hot', interpolation='nearest')
    plt.show()

    # b = heatMapDefenseGen(pawns, [], [], [])
    # for i in range(len(a)):
    #     for j in range(len(a[0])):
    #         a[i][j] = max(a[i][j], -5)
    #         b[i][j] = max(b[i][j], -5)

    # plt.imshow(b, cmap='hot', interpolation='nearest')
    # plt.show()

    # b = heatMapDefenseGen([], castles, [], [])
    # for i in range(len(a)):
    #     for j in range(len(a[0])):
    #         a[i][j] = max(a[i][j], -5)
    #         b[i][j] = max(b[i][j], -5)

    # plt.imshow(b, cmap='hot', interpolation='nearest')
    # plt.show()

    # b = heatMapDefenseGen(pawns, castles], knights, [])
    # for i in range(len(a)):
    #     for j in range(len(a[0])):
    #         a[i][j] = max(a[i][j], -5)
    #         b[i][j] = max(b[i][j], -5)

    # plt.imshow(b, cmap='hot', interpolation='nearest')
    # plt.show()
     # b = heatMapDefenseGen([], [], [], knights)
    # for i in range(len(a)):
    #     for j in range(len(a[0])):
    #         a[i][j] = max(a[i][j], -5)
    #         b[i][j] = max(b[i][j], -5)

    
   #  plt.imshow(b, cmap='hot', interpolation='nearest')
   #  plt.show()

def heatMapMove(pawns :list[Pawn], knights : list[Knight], castles : list[Castle], epawns : list[Pawn], eknights : list[Knight], ecastles : list[Castle], gold_map : list[list[int]], id : str):
    """ 
    La fonction qui prend en argument la case sélectionnée à défendre prend un chevalier pertinent à 
    proximité et le bouge intelligemment dans sa direction, enlève le mask knight à son point de départ
    et rajoute le mask chosenknight à son arrivée
    """
    forbiden_case_def = []
    forbiden_case_att = []
    while any( [not knight.used for knight in knights]) and (len(knights) != 0): 
        #Si on a au moins un chevalier non déjà déplacé...
        
        attmap = heatMapAttackGen(epawns, ecastles, id, knights, eknights, gold_map) #On génère les cartes...
        defmap = heatMapDefenseGen(pawns, castles, eknights, knights)
        for coord in forbiden_case_def:
            defmap[coord[0]][coord[1]]=-100
        for coord in forbiden_case_att:
            attmap[coord[0]][coord[1]]=-100
        max = 0
        co=(-1,-1)
        tp=None
        for i in range(con.size_map()[0]):
            for j in range(con.size_map()[1]):

                # Cas particulier : la attmap a vue une défaite un 1 sur certaine cases, on l'indique ainsi aussi a defmap  
                # if attmap[i][j] < 0:
                #     defmap[i][j] = -10


                #Quand des valeurs se distinguent sur les cates on va essayer d'agir en conséquence en prennant la plus grande
                if attmap[i][j]>max:
                    max=attmap[i][j]
                    co=(i,j)
                    tp="A"

                if defmap[i][j]>max:
                    max=defmap[i][j]
                    co=(i,j)
                    tp="D"
        if tp=="A": #Et ensuite en fonction d'où est le résultat on va attaquer ou défendre en priorité
            attackHere(knights, eknights,co, forbiden_case_att)
        else:
            defendHere(knights, eknights,co, forbiden_case_def)



def defendHere(knights : list[Knight], eknights : list[Knight],case:tuple[int,int], forbiden_case : list[tuple[int,int]]):
    '''Pour les ordres de défense'''
    print("Def")
    print("cible : ", case)
    nearestKnights=sorted(knights,key = lambda x:cl.distance(*x.coord,*case)) 
    #On trie les chevaliers par proximité au point d'intérêt
    i=0
    movement=None
    while movement is None and i<len(nearestKnights): #On cherche un déplacement valide et sûr dans nos chevaliers proches
        nearest=nearestKnights[i]
        if not nearest.used:
            movement=path_simple_bis(nearest,case,eknights)
        i+=1
    if movement is None: #Si movement est None à la fin on a rien pu bouger donc on sort
        forbiden_case.append(case)
        return
    if (nearest.y != case[0] or nearest.x != case[1]): #Et tant qu'on est pas exactement sur la case on se déplace
        nearest.move(movement[0], movement[1])
        if(movement[1] < 5):
            print("Ici ca casse les couilles", case)
            print(movement)
    else:
        nearest.used = True #Sinon on immobilise le chevalier.


def attackHere(knights : list[Knight], eknights : list[Knight],case:tuple[int,int], forbiden_case : list[tuple[int,int]]):
    '''Pour les ordres d'attaque'''
    print("Att")
    print(case)
    forbiden_case.append(case)
    nearestKnights=sorted([knight for knight in knights if not knight.used],key = lambda x:cl.distance(x.y,x.x,case[0],case[1]))
    #On trie les chevaliers par proximité à la case d'intérêt. 
    if len(eknights) == 0: 
        #S'il n'y a aucun ennemis, on avance directement vers l'objectif
        knight = nearestKnights[0]
        movement = path_simple_bis(knight, case, eknights)
        if movement is None:
            return
        if (movement[0] != knight.y or movement[1] != knight.x):
            knight.move(movement[0], movement[1])
        else:
            knight.used = True
        return
    
    #Sinon on va devoir engager un lot de chevaliers pour aller se battre
    hired_knights=[]
    i = 0
    while i<len(nearestKnights) and cl.distance(nearestKnights[i].y,nearestKnights[i].x,case[0],case[1])<3: 
        #On va prendre tout le monde qu'on trouve à une distance plus petite que 4 de l'objectif
        nearest=nearestKnights[i]
        hired_knights.append([nearest.y - case[0],nearest.x - case[1]])
        i+=1

    if len(hired_knights) == 0:
        #Si on a trouvé personne, on force le chevalier le plus proche à agir quand même
        hired_knights.append([nearestKnights[0].y - case[0], nearestKnights[0].x - case[1]])

    nearestEKnights=sorted(eknights,key = lambda x:cl.distance(x.y,x.x,case[0],case[1]))
    hired_Eknights=[]
    i = 0
    #On répète la même chose pour les ennemis... sans le forçage car vérifié précédemment 
    while i<len(nearestEKnights) and (cl.distance(nearestEKnights[i].y,nearestEKnights[i].x,case[0],case[1])<=max(3, abs(hired_knights[0][0]) + abs(hired_knights[0][1]))): 
        nearest=nearestEKnights[i]
        
        if len(hired_knights) != 1 or cl.distance(hired_knights[0][0], hired_knights[0][1], nearest.y, nearest.x) <= 2:        
            hired_Eknights.append([nearest.y - case[0], nearest.x - case[1]])
        i+=1

    print("chevaliers en actions : ",[hired_knights, hired_Eknights])

    if len([knight for knight in hired_Eknights if knight == (0,0)]) > len(hired_knights) :
        print("Trop dangereux")
        return

    if hired_knights[0] == case:
        for i, knights in enumerate(hired_knights):
            if knight == case:
                nearestKnights[i].used = True
        return
    
    liste_trie_conjoint=[(hired_knights[i],nearestKnights[i])for i in range(len(hired_knights))]
    liste_trie_conjoint=sorted(liste_trie_conjoint)
    nearestKnights = [liste_trie_conjoint[i][1] for i in range(len(liste_trie_conjoint))]
    hired_knights = [liste_trie_conjoint[i][0] for i in range(len(liste_trie_conjoint))]

    hired_EKnights=sorted(hired_Eknights)

    next_moves=min_max_alpha_beta_result([hired_knights,hired_Eknights]) 
    #Pour choisir comment déplacer les unités, on fait un min-max

    print("moves proposés : ",next_moves)
    print(case)
    for i, movement in enumerate(next_moves): 
        #Et on opère ensuite les déplacements en fonction du résultat du min_max
        if (nearestKnights[i].y != movement[0] + case[0] or nearestKnights[i].x != movement[1] + case[1]):
            nearestKnights[i].move(movement[0] + case[0], movement[1] + case[1]) 
        else:
            nearestKnights[i].used = True