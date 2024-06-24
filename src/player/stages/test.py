import copy 

config=[[[1,0],[1,0],[1,0],[1,0]],[[1,1],[0,0]]]

def min_max_alpha_beta(depth:int,alpha:int,beta:int, base_map:list[list[int,int]],player:int):
    extrem=player*10000
    map_id_max=None
    map_id=None
    new_beta=beta
    new_alpha=alpha
    if depth>0:
        cond_init=True
        next_move=copy.deepcopy(base_map)
        while(map_id!=None or cond_init ):
            if player==0 and [0,0] in next_move[0]:
                val=eval_config(next_move)+depth
            else:
                val,_ = min_max_alpha_beta(depth-1,new_alpha,new_beta,next_move,1-player)
            #print(val,extrem)
            if val> extrem and not player:
                extrem = val
                map_id_max=map_id
                new_alpha=max(alpha,val)
                if val >= beta:
                    return val,map_id_max  
            if val< extrem and player:
                #print("ancien",config,extrem)
                #print("nouveau",next_move,val)
                extrem = val
                map_id_max = map_id
                new_beta=min(new_beta,val)
                if val <= alpha:
                    return val,map_id_max  
                
            next_move,map_id = next_turn(base_map,player,map_id)
            #print(next_move)
            if map_id is not None:
                fight_resolver(next_move,player)
            cond_init=False
        return extrem,map_id_max
    else:
        return eval_config(base_map), base_map


def eval_config(config):
    score=0
    exist=False
    for knight in config[0]:
        if knight==[0,0] and not exist:
            score+=30
            exist=True
        if abs(knight[0])!=2400:
            score+=1
    for knight in config[1]:
        if abs(knight[0])!=2400:
            score-=2
    return max(score,0)


def next_match(units,new_vector):
    '''
    Crée des listes d'unités qui ont été déplacées d'après la valeur du vecteur donné
    '''
    new_units=[]
    for i,unit in enumerate(units):
        if abs(unit[0])==2400:
            new_units.append(unit)
            continue
        match(new_vector[i]):
            case 1:
                new_units.append([unit[0]-1,unit[1]])
            case 2:
                new_units.append([unit[0]+1,unit[1]])
            case 3:
                new_units.append([unit[0],unit[1]-1])
            case 4:
                new_units.append([unit[0],unit[1]+1])
            case _: 
                new_units.append(unit)
    return new_units

def good_move(last_vector:list[int],new_move:list[int],units:list[list[int,int]],baddies:list[list[int,int]]):
    '''
    Vérifie de la viabilité de l'alternative avant de brancher
    '''
    
    origin=next_match(units,[0 for _ in range(len(last_vector))])
    new=next_match(units,new_move)
    for ind in range(len(new_move)): #On vérifie pour chaque unité déplacée
        if new[ind]!=origin[ind]:
            if (distance(new[ind][0],new[ind][1],0,0)>distance(origin[ind][0],origin[ind][1],0,0) and not new[ind] in baddies) \
                    and not (origin[ind][0]==0 and origin[ind][1]==0): #############/!\ remettre les cl.
                #Si on se rapproche du centre ou 
                #print("Check pas passé : \n",baddies,new[ind])
                return False
                
    return True

def cinq_adder(last_vector,indice,units):
    '''
    Un adder en pentaire pour les vecteurs de mouvements
    
    Renvoie None en cas de overflow
    '''
    if indice>=len(last_vector):
        return None
    if abs(units[indice][0])==2400:
        return cinq_adder(last_vector,indice+1,units)
    if last_vector[indice]+1 >= 5:
        last_vector[indice]=0
        return cinq_adder(last_vector,indice+1,units)
    else:
        last_vector[indice]+=1
        return last_vector

def next_turn(units:list[list[int,int]],player:int,last_vector:list[int]=None):
    '''
    Itère sur les états de la carte possible

    Renvoie le placement des nouvelles unités ainsi que le vecteur associé
    Le vecteur correspond à un déplacement par rapport à leur situation initiale au début du tour.
    '''
    if last_vector is None: #Cas initial: Pas de dernier vecteur donc on le crée
        last_vector=[0 for _ in range(len(units[player]))]
        return units, last_vector
    units=copy.deepcopy(units)
    my_units=units[player]
    new_move=cinq_adder(last_vector,0,my_units)
    while (new_move is not None) and (not good_move(last_vector,new_move,my_units,units[1-player])):
        new_move=cinq_adder(last_vector,0,my_units)
    if new_move is None:
        return None,None
    units[player]=next_match(my_units,new_move)
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
    
#print(min_max_alpha_beta(6,-100,1000,config,0))   

def distance(x1: int, y1: int, x2: int, y2: int):
    """
    Effectue le calcul de la distance de Manhattan entre (x1, y1) et (x2, y2).

    Parametres:
        x1, y1 : les coordonées du premier point.
        x2, y2 : Les coordonées du second point.
    """
    return abs(x1 - x2) + abs(y1 - y2)

print(min_max_alpha_beta(6,-100,1000,config,0))      
