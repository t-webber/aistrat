"""Évaluation de l'état de la partie, independamment du reste du code."""

# import copy
# from apis import connection

# taille = (0, 0)
# ref_taille = 0
# cuts = None
# taille_cuts = None

# zones = ["UArG", 'ArG', 'Mid', 'AvG', 'UAvG']


# def define_global():
#     """Définit les quelques variables globales utilisées par les fonctions."""
#     global cuts
#     global taille
#     global ref_taille
#     global taille_cuts
#     taille = connection.size_map()
#     ref_taille = max(taille[0], taille[1])
#     cuts = [ref_taille // 4, (2 * ref_taille) // 4, ref_taille - 1,
#             taille[0] + taille[1] - ref_taille // 4]
#     taille_cuts = [integer_sum(cuts[0])]
#     for i in range(len(cuts)):
#         taille_cuts.append(integer_sum(cuts[i]) - taille_cuts[i])


# def inventory_zones():
#     """Inventorie toutes les entites connues par type et par zone du combat selon la répartition définie dans cuts."""
#     if cuts is None:
#         define_global()
#     player = connection.current_player()
#     total_units = connection.get_kinds(player)
#     unit_types = ["C", 'B', 'M', 'C2', 'B2', 'M2', 'fog']
#     base_dict = {"C": [], "B": [], "M": [],
#                  "C2": [], "B2": [], "M2": [], 'fog': []}
#     inventory = {"UArG": copy.deepcopy(base_dict), "ArG": copy.deepcopy(
#         base_dict), "Mid": copy.deepcopy(base_dict), "AvG": copy.deepcopy(base_dict), "UAvG": base_dict}
#     for unit_type in unit_types:
#         for entity in total_units[unit_type]:
#             inventory[myZone(entity, player)][unit_type].append(entity)
#     return inventory


# def myZone(entity: tuple[int, int], player: str):
#     """Renvoie la zone d'une entité."""
#     if player == "A":
#         ref = (0, 0)
#     else:
#         ref = (taille[0] - 1, taille[1] - 1)
#     distanceN1 = dist1(entity, ref)
#     for i in range(len(cuts)):
#         if distanceN1 <= cuts[i]:
#             return zones[i]
#     return ('UAvG')


# def dist1(pt1: tuple[int, int], pt2: tuple[int, int]):
#     """Donne la norme 1 du vecteur entre les 2 points."""
#     return abs(pt1[0] - pt2[0]) + abs(pt1[1] - pt2[1])


# def integer_sum(integer: int):
#     """Donne la somme de 1 à integer pour avoir la surface des triangles de zone."""
#     return integer * (integer + 1) // 2


# def get_diff(unit_type: str, zone: str, inventory: dict[str, dict[str, tuple[int, int]]]):
#     """Renvoie la différence de force dans une zone pour un type d'unité donné."""
#     return len(inventory[zone][unit_type]) - len(inventory[zone][f"{unit_type}2"])


# def get_stats(inventory: dict[str, dict[str, tuple[int, int]]]):
#     """
#     Statistiques militaires.

#     Returns:
#         - uncertainty: proportion d'incertitude par zone
#         - military: différence de force par zone
#     """
#     uncertainty = [len(inventory[zones[i]]['fog']) / taille_cuts[i]
#                    for i in range(len(taille_cuts))]
#     military = [get_diff("M", zones[i], inventory) for i in range(len(zones))]
#     return uncertainty, military


# def is_within(ally: tuple[int, int], ennemy: tuple[int, int], player: str):
#     """
#     Vérifie si une unité est dans le territoire allié.

#     Le détermine si le produit scalaire entre un allié et son point de départ est de signe inverse que celui entre lui et l'ennemi.
#     """
#     if player == "A":
#         ref = (0, 0)
#     else:
#         ref = (taille[0] - 1, taille[1] - 1)
#     vector = (ennemy[0] - ally[0], ennemy[1] - ally[1])
#     vect_ref = (ref[0] - ally[0], ref[1] - ally[1])
#     return vector[0] * vect_ref[0] + vector[1] * vect_ref[1] <= 0


# def inbound_ennemies():
#     """Cherche des unités ennemies dans des situations particulières à gérer dans notre territoire."""
#     results = {'Pierced': [], 'Invading Peon': [], "Sieged Castle": []}

#     player = connection.current_player()
#     total_units = connection.get_kinds(player)
#     all_allies = total_units['C'] + total_units['B'] + total_units['M']

#     for ennemy in total_units['M2']:
#         for unit in all_allies:
#             if is_within(unit, ennemy, player):
#                 results['Piereced'].append(ennemy)
#                 break

#     for ennemy in total_units['C2']:
#         for unit in all_allies:
#             if is_within(unit, ennemy, player):
#                 results['Invading Peon'].append(ennemy)
#                 break

#     for ennemy in total_units['B2']:
#         for unit in all_allies:
#             if is_within(unit, ennemy, player):
#                 results['Sieged Castle'].append(ennemy)
#                 break

#     return results


# def menacing_ennemies():
#     """Renvoie les unités proches de nos alliés."""
#     results = {'Attackable Castle': [],
#                'Dangerous Knight': [], "Killable peon": []}
#     player = connection.current_player()
#     total_units = connection.get_kinds(player)
#     all_allies = total_units['C'] + total_units['B'] + total_units['M']
#     max_range = 2  # Portée en norme 1 de détection aka tours de marche

#     for ennemy in total_units['M2']:
#         for unit in all_allies:
#             if dist1(ennemy, unit) < max_range:
#                 results['Dangerous Knight'].append(ennemy)
#                 break

#     for ennemy in total_units['C2']:
#         for unit in all_allies:
#             if dist1(ennemy, unit) < max_range:
#                 results['Killable peon'].append(ennemy)
#                 break

#     for ennemy in total_units['B2']:
#         for unit in all_allies:
#             if dist1(ennemy, unit) < max_range:
#                 results['Attackable Castle'].append(ennemy)
#                 break

#     return results
