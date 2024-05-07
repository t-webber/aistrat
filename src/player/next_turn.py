""" naïve algorithm """

import numpy as np
import random as rd
import player.stages.peons as peons
import api
import player.logic.client_logic as cl
import player.stages.castles as builder
import player.stages.attack as atk
import player.stages.defense as dfd
import player.stages.decisions as dec
import player.stages.front_line as fl

def nexturn(player, token):
    """ 
    run next turn for the current player 
        - build a castle
        - farm coins
    """
    kinds = api.get_kinds(player)
    pawns: list[api.Coord] = kinds[api.PAWN]
    knights: list[api.Coord] = kinds[api.KNIGHT]
    eknights: list[api.Coord] = kinds[api.EKNIGHT]
    epawns: list[api.Coord] = kinds[api.EPAWN]
    fog = kinds[api.FOG]
    # liste des chevaliers attribués à la défense
    defense: list[api.Coord] = cl.defense_knights[player]
    golds: list[api.Coord] = kinds[api.GOLD]
    castles: list[api.Coord] = kinds[api.CASTLE]
    ecastles: list[api.Coord] = kinds[api.ECASTLE]
    try:
        gold = api.get_gold()[player]
    except:
        gold = 0

    # pour moi, on appelle dans l'ordre :
    # defense
    # fuite qui dit au peons de fuire s'ils vont se faire tuer
    # (i.e un méchant est à côté et pas de gentil assez près pour l'aider)
    # construction forteresse
    # farm
    # explore
    # attaque
    for d in defense:
        if d not in knights:
            defense.remove(d)
        else:
            knights.remove(d)
    good_gold, bad_gold = cl.clean_golds(golds, pawns, ecastles)

    builder.create_pawns(castles, player, token,
                         eknights, knights, gold, cl.defense_knights[player],
                         len(golds), len(pawns), len(fog))
    peons.fuite(pawns, knights, eknights, defense, player, token)

    builder.check_build(pawns, castles, player, token, gold, eknights)
    # je farm d'abord ce que je vois
    peons.farm(pawns, player, token, good_gold, eknights, ecastles)
    # j'explore ensuite dans la direction opposée au spawn
    peons.explore(pawns, player, token, eknights,
                  ecastles, knights+castles, bad_gold)

    atk.free_pawn(knights, player, token, eknights, epawns)

    left_defense = dfd.defend(pawns, defense, eknights, castles, player, token)
    dfd.agressiv_defense(left_defense, epawns, player, token, eknights)
    while knights:
        a = len(knights)
        atk.hunt(knights, epawns, eknights, player, token)
        atk.destroy_castle(knights, ecastles, eknights, player, token)
        if len(knights) == a:
            break
    # inventory=dec.inventory_zones()
    # print(inventory)
    # print(dec.get_diff("M","Mid",inventory))



def next_turn_fl(player, token):
    """ 
    run next turn for the current player with a front line strategie
        - build a castle
        - farm coins
    """
    kinds = api.get_kinds(player)
    pawns: list[api.Coord] = kinds[api.PAWN]
    knights: list[api.Coord] = kinds[api.KNIGHT]
    eknights: list[api.Coord] = kinds[api.EKNIGHT]
    epawns: list[api.Coord] = kinds[api.EPAWN]
    fog = kinds[api.FOG]
    # liste des chevaliers attribués à la défense
    defense: list[api.Coord] = cl.defense_knights[player]
    golds: list[api.Coord] = kinds[api.GOLD]
    castles: list[api.Coord] = kinds[api.CASTLE]
    ecastles: list[api.Coord] = kinds[api.ECASTLE]
    try:
        gold = api.get_gold()[player]
    except:
        gold = 0

    good_gold, bad_gold = cl.clean_golds(golds, pawns, ecastles)

    builder.create_pawns_fl(castles, player, token,
                         eknights, knights, gold, cl.defense_knights[player],
                         len(golds), len(pawns), len(fog))
    peons.fuite(pawns, knights, eknights, defense, player, token)

    builder.check_build(pawns, castles, player, token, gold, eknights)
    # je farm d'abord ce que je vois
    peons.farm(pawns, player, token, good_gold, eknights, ecastles)
    # j'explore ensuite dans la direction opposée au spawn
    peons.explore(pawns, player, token, eknights,
                  ecastles, knights+castles, bad_gold)
    


    if len(fl.front_line[player]) == 0:
        fl.create_front(player)

    fl.update_front(player, knights)


    fl.is_full[player] = (fl.is_full_update(player) or fl.is_full[player])
    
    if not fl.is_full[player]:
        fl.move_to_line(knights, player, token)
    
    fl.equilibrate(knights, player, token)
    if fl.is_full[player]:
        if fl.broken_line(player):
            print("there")
            atk.free_pawn(knights, player, token, eknights, epawns)
            while knights:
                a = len(knights)
                atk.hunt(knights, epawns, eknights, player, token)
                atk.destroy_castle(knights, ecastles, eknights, player, token)
                if len(knights) == a:
                    break
        else :
            print("here")
            fl.move_to_line(knights, player, token)
            fl.advance(knights, eknights, player, token)