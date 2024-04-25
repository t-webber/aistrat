import copy
import api



def inventory_zones():
    '''
    Inventorie toutes les entites connues par type et 
    par zone du combat selon la répartition définie dans cuts
    '''
    taille=api.size_map()
    ref_taille=max(taille[0],taille[1])
    cuts=[ref_taille//4,(2*ref_taille)//4,ref_taille-1,taille[0]+taille[1]-ref_taille//4]

    joueur=api.current_player()
    if joueur=="A":
        ref=(0,0)
    else: ref=(taille[0]-1,taille[1]-1)
    total_units=api.get_kinds(joueur)
    unit_types=["C",'B','M','C2','B2','M2']
    base_dict={"C":[],"B":[],"M":[],"C2":[],"B2":[],"M2":[]}
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

def get_diff(unit_type,zone,inventory):
    '''
    Renvoie la différence de force dans une zone pour un type d'unité donné
    '''
    return len(inventory[zone][unit_type])-len(inventory[zone][f"{unit_type}2"])
