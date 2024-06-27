
"""Fichier qui implémente la class `Player`."""
from apis import connection
from apis.players.player_structure import Player_struct
from player.castles import create_units, build_castle, castle_flee
import player.attack as atk
# import player.decisions as dec
import player.defense as dfd
from player import peons
from debug import log_func, pause


class Player(Player_struct):
    """Class pour implémenter les actions d'un joueur."""

    def next_turn(self):
        """Joue le prochain tour pour le joueur."""
        self.reinit_data()

        print(f"============= Begin {self.turn} turn for player {self.id} =====================")

        self.turn += 1

        self.checks_turn_data()
        self.update_golds()
        self.update_ennemi_data()
        self.update_fog()

        # fonction pour le debug
        pause(self.id)

        # je crée des unités en premier
        create_units(self)

        # j'appelle des chevaliers pour défendre mes chateaux et mes péons
        log_func("castle_flee and fuite")
        castle_flee(self.castles, self.defense + self.attack, self.eknights, self)
        peons.fuite(self.pawns, self.defense + self.attack, self.eknights)

        # je vois d'abord si un péons veut construire un chateau
        log_func("castle")
        build_castle(self)

        # je farm ensuite l'or que je vois
        log_func("farm")
        peons.coordination_farm(self)

        # puis j'explore dans la direction opposée au spawn
        log_func("explore")
        peons.explore(self, self._knights + self.castles)
        
        # les defenseurs se dirigent vers les peons les plus fragiles
        log_func("defend")
        dfd.defend(self.pawns, self.defense, self.eknights, self.castles)

        # si des chevaliers ennemis sont proches et qu'on ne perd rien à les attaquer 
        log_func("agressiv_defense")
        dfd.agressiv_defense(self.defense + self.attack, self.epawns, self.eknights, self.ecastles)

        # je gère mes chevaliers d'attaques pour attaquer les cibles ennemis
        atk.coordination(self)

        # si je n'ai pas de cible, nos attaquants vont explorer
        log_func("explore_knight")
        peons.explore_knight(self, self.pawns + self.castles)

        # comme on a gagné de l'or par le farm pendant le tour, on regarde si jamais on ne peut pas en créer d'autres
        log_func("second create unit")
        create_units(self)

        # je mets à jour la map de l'or
        self.update_gold_map()

        # je mets fin à mon tour
        connection.end_turn(self.id, self.token)
