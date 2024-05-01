import copy
import api

taille=(0,0)
ref_taille=0
cuts=None
taille_cuts=None

zones=["UArG",'ArG','Mid','AvG','UAvG']

def define_global():
    global cuts
    global taille
    global ref_taille
    global taille_cuts
    taille=api.size_map()
    ref_taille=max(taille[0],taille[1])
    cuts=[ref_taille//4,(2*ref_taille)//4,ref_taille-1,taille[0]+taille[1]-ref_taille//4]
    taille_cuts=[integer_sum(cuts[0])]
    for i in range(len(cuts)):
        taille_cuts.append(integer_sum(cuts[i])-taille_cuts[i])


def inventory_zones():
    '''
    Inventorie toutes les entites connues par type et 
    par zone du combat selon la répartition définie dans cuts
    '''
    if cuts is None:
        define_global()
    joueur=api.current_player()
    if joueur=="A":
        ref=(0,0)
    else: ref=(taille[0]-1,taille[1]-1)
    total_units=api.get_kinds(joueur)
    unit_types=["C",'B','M','C2','B2','M2','fog']
    base_dict={"C":[],"B":[],"M":[],"C2":[],"B2":[],"M2":[],'fog':[]}
    inventory={"UArG":copy.deepcopy(base_dict),"ArG":copy.deepcopy(base_dict),"Mid":copy.deepcopy(base_dict),"AvG":copy.deepcopy(base_dict),"UAvG":base_dict}
    for unit_type in unit_types:
        for entity in total_units[unit_type]:
            distanceN1=abs(entity[0]-ref[0])+abs(entity[1]-ref[1])
            if distanceN1<=cuts[0]:
                inventory['UArG'][unit_type].append(entity)
            elif distanceN1<=cuts[1]:
                inventory['ArG'][unit_type].append(entity)
            elif distanceN1<=cuts[2]:
                inventory['Mid'][unit_type].append(entity)
            elif distanceN1<=cuts[3]:
                inventory['AvG'][unit_type].append(entity)
            else:
                inventory['UAvG'][unit_type].append(entity)
    return inventory

def integer_sum(integer):
    """Calcule la somme de 1 à integer pour avoir la surface des triangles de zone"""
    return integer*(integer+1)//2

def get_diff(unit_type,zone,inventory):
    '''
    Renvoie la différence de force dans une zone pour un type d'unité donné
    '''
    return len(inventory[zone][unit_type])-len(inventory[zone][f"{unit_type}2"])


def get_stats(inventory):
    """Renvoie des statistiques militaires: le taux d'avantage avec des statistiques de manque d'information"""
    uncertainty=[len(inventory[zones[i]]['fog'])/taille_cuts[i] for i in range(len(taille_cuts))]
    military=[get_diff("M",zones[i],inventory) for i in range(len(zones))]
    return uncertainty,military

