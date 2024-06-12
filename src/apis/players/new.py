"""Fichier qui implémente la class `Player`."""

from apis.players.player_structure import Player_struct
# import player.stages.decisions as dec
# import player.stages.defense as dfd


class Player(Player_struct):
    """Class pour implémenter les actions d'un joueur."""

    def next_turn(self):
        """Joue le prochain tour pour le joueur."""

        self.reinit_data()

        print("============= BEGin TURN for player", self.id, " =====================")

        self.turn += 1
        self.checks_turn_data()
        self.update_ennemi_data()
        self.update_fog()
        self.update_gold_map()
