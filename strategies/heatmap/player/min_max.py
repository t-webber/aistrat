import copy 
import random as rd
import time
#import logic.client_logic as cl

config=[[[0,1],[0,1],[0,1],[0,1],[0,1],[0,1]],[[0,0],[0,0],[0,0],[1,1],[1,1],[1,1]]]
def min_max_alpha_beta_result(base_map:list[list[int,int]]):
    '''
    Permet d'appliquer min_max_alpha_beta dans les conditions standard

    Renvoie les alliés dans leurs coordonnées relatives post-déplacement
    '''
    depth=2*(len(base_map[0])+len(base_map[1])<3) + 2 *(len(base_map[0])+len(base_map[1])<5) + 2
    alpha=-100
    beta=1000
    player=0
    offsetGood=[rd.randint(0,3) for _ in range(len(base_map[player]))]
    offsetBad=[rd.randint(0,3) for _ in range(len(base_map[1-player]))]
    #print(offsetGood,offsetBad)
    _,move=min_max_alpha_beta(depth,alpha,beta,base_map,0,offsetGood,offsetBad)
    next=next_match(base_map[player],move,offsetGood)
    return next
    #return [[next[k][0]-base_map[player][k][0],next[k][1]-base_map[player][k][1]] for k in range(len(next))] #Si c'était en relatif
    

def min_max_alpha_beta(depth:int,alpha:int,beta:int, base_map:list[list[int,int]],player:int,offsetGood:list[int],offsetBad:list[int]):
    '''
    algorithme min-max avec elaguage alpha beta, au quel sont ajoutees les contraintes suivantes:
        o impossible de s'eloigner de la case ciblee (consideree en 0,0)
        o possibilite de sortir de 0,0
        o possibilite de s'eloigner du centre si cela permet d'attaquer 7
    '''
    extrem=player*10000 - 100
    map_id_max=[0 for i  in range (len(base_map[0]))]
    map_id=None
    new_beta=beta
    new_alpha=alpha

    #Tant qu'on a pas atteind une profondeur de 0...
    if depth>0:
        cond_init=True
        next_move=copy.deepcopy(base_map)
        while(map_id!=None or cond_init ):
            if player==0 and [0,0] in next_move[0]:
                #On calcule le score si on est en première itération de la boucle ou sur le point d'aller au centre
                val=eval_config(next_move)+depth 
            else:
                #Sinon on s'enfonce
                val,_ = min_max_alpha_beta(depth-1,new_alpha,new_beta,next_move,1-player,offsetBad,offsetGood)
                #On inverse les offset ici comme on considère l'autre joueur
            if val> extrem and not player:
                #Lorsqu'on atteind un nouveau extremum et si on est l'allié...
                extrem = val
                if map_id is not None:
                    map_id_max=map_id.copy() #On retient les nouveaux déplacements
                new_alpha=max(alpha,val) #Et le nouvel alpha
                if val >= beta:
                    return val,map_id_max #Puis on renvoie val si on dépasse beta
            if val< extrem and player:
                #Même chose si on est le méchant mais en opposé
                extrem = val
                if map_id is not None:
                    map_id_max = map_id.copy()
                new_beta=min(new_beta,val)
                if val <= alpha:
                    return val,(map_id_max,config)  
                
            next_move,map_id = next_turn(base_map,player,map_id,offsetGood)
            #On récupère ensuite les paramètres pour le nouveau tour
            if map_id is not None:
                fight_resolver(next_move,player)
            cond_init=False            
        return extrem,map_id_max 
        #Si on a atteind le fond, on renvoie le maximum trouvé
    else:
        return eval_config(base_map), [] #Si on a dépassé la limite de profondeur, on renvoie simplement l'évaluation de l'état


def eval_config(config):
    '''
    Fonction d'évalutation/scoring d'une configuration de carte
    '''
    score=0
    exist=False
    for knight in config[0]:
        if knight==[0,0] and not exist:
            score+=30 #Si on est arrivé au centre, gros bonus
            exist=True
        elif abs(knight[0]) != 2400:
            score+=0.5-(abs(knight[0])+abs(knight[1]))/100
        if abs(knight[0])!=2400: #On récompense la non mort
            score+=1
    for knight in config[1]:
        if abs(knight[0])!=2400: #Chaque ennemi non mort nous pénalise
            score-=1.1
    return score #On met pas de score négatif


def next_match(units,new_vector,offsets):
    '''
    Crée des listes d'unités qui ont été déplacées d'après la valeur du vecteur donné
    '''
    new_units=[]
    matchers=[1,2,3,4]
    #print("Offset:",offsets)
    #print("Unité:",units)
    for i,unit in enumerate(units):
        if abs(unit[0])==2400:
            #Si l'unité est morte, n'y touche pas
            new_units.append(unit)
        else:  
            #0 on bonge pas, 1 haut, 2 bas, 3 gauche, 4 droites
            if new_vector[i]==matchers[(0+offsets[i])%4]:
                new_units.append([unit[0]-1,unit[1]]) 
            elif new_vector[i]==matchers[(1+offsets[i])%4]:
                new_units.append([unit[0]+1,unit[1]])
            elif new_vector[i]==matchers[(2+offsets[i])%4]:
                new_units.append([unit[0],unit[1]-1])
            elif new_vector[i] == matchers[(3+offsets[i])%4]:
                new_units.append([unit[0],unit[1]+1])
            else: 
                new_units.append(unit)
    return new_units

def good_move(last_vector:list[int],new_move:list[int],units:list[list[int,int]],baddies:list[list[int,int]],offsets:list[int]):
    '''
    Vérifie de la viabilité de l'alternative avant de brancher
    '''
    #return True
    origin=next_match(units,[0 for _ in range(len(last_vector))],offsets)
    new=next_match(units,new_move,offsets)
    for ind in range(len(new_move)): #On vérifie pour chaque unité déplacée
        if new[ind]!=origin[ind]:
            if (distance(new[ind][0],new[ind][1],0,0)>distance(origin[ind][0],origin[ind][1],0,0) and not new[ind] in baddies) \
                    and not (origin[ind][0]==0 and origin[ind][1]==0):
                #Si on ne se rapproche PAS du centre ou on ne fight pas, on a un mauvais move
                #On autorise tous les moves au centre
                return False
    #RAS = branche valide 
    return True

def cinq_adder(last_vector,indice,units):
    '''
    Un adder en pentaire pour les vecteurs de mouvements
    
    Renvoie None en cas de overflow
    '''
    if indice>=len(last_vector):
        return None
    if abs(units[indice][0])==2400: #Si on essaye de deplacer une unité morte, on la bouge pas et on passe au reste
        return cinq_adder(last_vector,indice+1,units)
    if last_vector[indice]+1 >= 5: #En cas d'overflow sur le bit, on fait passer la retenue au "bit" suivant
        last_vector[indice]=0
        return cinq_adder(last_vector,indice+1,units)
    else: #Si rien à signaler, on incrémente
        last_vector[indice]+=1
        return last_vector

def next_turn(units:list[list[int,int]],player:int,last_vector:list[int],offsets:list[int]):
    '''
    Itère sur les états de la carte possible

    Renvoie le placement des nouvelles unités ainsi que le vecteur associé
    Le vecteur correspond à un déplacement par rapport à leur situation initiale au début du tour.
    '''
    if last_vector is None: #Cas initial: Pas de dernier vecteur donc on le crée de longueur du nombre d'alliés déplaçables
        last_vector=[0 for _ in range(len(units[player]))]
        return units, last_vector
    units=copy.deepcopy(units) #On ne veut pas modifier les unités en entrée
    my_units=units[player]
    new_move=cinq_adder(last_vector,0,my_units) #Prochain mouvement = incrémentation du vecteur encodé en pentaire (1-2-3-4 pour déplacements latéraux, 0= immobile)
    while (new_move is not None) and (not good_move(last_vector,new_move,my_units,units[1-player],offsets)):
        #Si on a un move qui est vraiment pas bien (éloignant sans attaque), on évite de créer une branche pour rien et on refait
        new_move=cinq_adder(last_vector,0,my_units)
    if new_move is None: #Si on a None, cinq_adder a complètement overflow donc on a tout vu
        return None,None
    units[player]=next_match(my_units,new_move,offsets) #On effectue le déplacement une fois le move vérifié et on le renvoie avec le vecteur
    return units,new_move

def fight_resolver(all_units,player):
    '''
    Opère la logique de combat en attaque de l'allié contre l'ennemi

    Marque les unités mortes avec des +-2400 en coordonnées
    '''
    allies=all_units[player]
    ennemies=all_units[1-player]
    for index,ally in enumerate(allies): 
        if abs(ally[0])!=2400: #2400 indique une localisation "morte"
            sum=0
            for ennemy in ennemies: #Compte les ennemis présents sur la case de l'allié
                if ennemy==ally:
                    sum+=1
            if sum>=1: #S'il y a un ennemi ou +, on doit compter nos forces pour se battre
                force=1
                for index2,other_ally in enumerate(allies):
                    if index!=index2 and ally==other_ally:
                        force+=1
                removing=prediction_combat(force,sum) #On va chercher l'issue du combat
                i=0
                while i<removing[2]: #On marque removing[2] alliés morts sur la case de ally comme morts (lui le premier)
                    if allies[index]==ally: 
                        allies[index]=(2400,2400)
                        i+=1
                    index+=1
                i=0
                index=0
                while i<removing[3]: #On marque removing[3] ennemis morts sur la case de ally comme morts
                    if ennemies[index]==ally: 
                        ennemies[index]=(-2400,-2400)
                        i+=1
                    index+=1
                #Complexité au pire O(n^2*m) avec n nombres d'alliés, m nombre d'ennemis
                    
def distance(x1: int, y1: int, x2: int, y2: int):
    """
    Effectue le calcul de la distance de Manhattan entre (x1, y1) et (x2, y2).

    Parametres:
        x1, y1 : les coordonées du premier point.
        x2, y2 : Les coordonées du second point.
    """
    return abs(x1 - x2) + abs(y1 - y2)

def prediction_combat(a: int, d: int):
    """Prédit le gaganant d'un combat.

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
        pertes_a += min(a, (d + 1) // 2)
        a = a - (d + 1) // 2
        pertes_d += min(d, (a + 1) // 2)
        d = d - (a + 1) // 2
    return (d <= 0, pertes_a <= pertes_d, pertes_a, pertes_d)
a=time.time()
print(min_max_alpha_beta_result(config))
print(time.time()-a)