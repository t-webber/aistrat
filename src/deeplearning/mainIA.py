import pygame
import sys
import random
import time
from collections import defaultdict
from math import ceil
import torch.nn.functional as F

class gameIA:
    def __init__(self):

        self.Test = True  # affiche le jeu

        if self.Test:
            pygame.init()
            self.largeur = 75*16
            self.hauteur = 75*9 
            self.fenetre = pygame.display.set_mode((self.largeur, self.hauteur))
            self.horloge = pygame.time.Clock()
            self.taille_bloc = int(self.largeur / 16)
            self.pause = 0
            self.COULEURS = {
                0: (0, 0, 0),
                1: (255, 255, 255),
                2: (237, 224, 200),
                4: (242, 177, 121),
                8: (245, 149, 99),
                16: (246, 124, 95),
                32: (246, 94, 59),
                64: (237, 207, 114),
                128: (237, 204, 97),
                256: (237, 200, 80),
                512: (237, 197, 63),
                1024: (237, 194, 46),
                2048: (237, 194, 46),
            }


        self.dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.MAX_NB_ROUNDS = 2000
        self.MAP_WIDTH = 16
        self.MAP_HEIGHT = 9
        self.NB_GOLD_SPOTS = 15
        self.price = {'C': 5, 'M': 10, 'B': 15}
        self.requires = {'C': 'B', 'M': 'B', 'B': 'C'}
        
        self.players = []
        self.farmed = set()
        self.mapdata = []
        self.nbMoves = defaultdict(int)
        self.winner = ''
        self.curPlayer = 'A'
        self.gold = {'A': 25, 'B': 25}
        for y in range(self.MAP_HEIGHT):
            self.mapdata.append([])
            for x in range(self.MAP_WIDTH):
                self.mapdata[-1].append({'G': 0, 'A': {'C': 0, 'M': 0, 'B': 0}, 'B': {'C': 0, 'M': 0, 'B': 0}})
        self.mapdata[0][0]['A']['C'] = 3
        self.mapdata[-1][-1]['B']['C'] = 3
        self.opponent = {'A': 'B', 'B': 'A'}
        self.score = {'A': 0, 'B': 0}
        self.nbRounds = 0
        for i in range(self.NB_GOLD_SPOTS):
            x = random.randint(0, self.MAP_WIDTH-1)
            y = random.randint(0, self.MAP_HEIGHT-1)
            n = random.randint(1, 12)
            self.mapdata[y][x]['G'] += n*n
            self.mapdata[self.MAP_HEIGHT-1-y][self.MAP_WIDTH-1-x]['G'] += n*n

    def reset(self):
        for y in range(self.MAP_HEIGHT):
            self.mapdata.append([])
            for x in range(self.MAP_WIDTH):
                self.mapdata[-1].append({'G': 0, 'A': {'C': 0, 'M': 0, 'B': 0}, 'B': {'C': 0, 'M': 0, 'B': 0}})
        self.mapdata[0][0]['A']['C'] = 3
        self.mapdata[-1][-1]['B']['C'] = 3
        self.opponent = {'A': 'B', 'B': 'A'}
        self.score = {'A': 0, 'B': 0}
        self.nbRounds = 0
        for i in range(self.NB_GOLD_SPOTS):
            x = random.randint(0, self.MAP_WIDTH-1)
            y = random.randint(0, self.MAP_HEIGHT-1)
            n = random.randint(1, 12)
            self.mapdata[y][x]['G'] += n*n
            self.mapdata[self.MAP_HEIGHT-1-y][self.MAP_WIDTH-1-x]['G'] += n*n

        for i in range(self.NB_GOLD_SPOTS):
            x = random.randint(0, self.MAP_WIDTH-1)
            y = random.randint(0, self.MAP_HEIGHT-1)
            n = random.randint(1, 12)
            self.mapdata[y][x]['G'] += n*n
            self.mapdata[self.MAP_HEIGHT-1-y][self.MAP_WIDTH-1-x]['G'] += n*n
    
    def draw_grid(self):
        # Dessiner la grille
        if self.Test:
            self.fenetre.fill(self.COULEURS[1])
            for x in range(self.MAP_WIDTH):
                for y in range(self.MAP_HEIGHT):
                    color = (0, 0, 0)
                    text1 = ""
                    text2 = ""
                    text3 = ""
                    if self.mapdata[y][x]['A']['C'] > 0:
                        text1 = f"C={self.mapdata[y][x]['A']['C']}"
                    if self.mapdata[y][x]['A']['M'] > 0:
                        text2 = f"M={self.mapdata[y][x]['A']['M']}"
                    if self.mapdata[y][x]['A']['B'] > 0:
                        text3 = f"B={self.mapdata[y][x]['A']['B']} "
                    if self.mapdata[y][x]['B']['C'] > 0:
                        text1 = f"C={self.mapdata[y][x]['B']['C']}"
                    if self.mapdata[y][x]['B']['M'] > 0:
                        text2 = f"M={self.mapdata[y][x]['B']['M']}"
                    if self.mapdata[y][x]['B']['B'] > 0:
                        text3 = f"B={self.mapdata[y][x]['B']['B']} "
                    if self.mapdata[y][x]['G'] > 0:
                        color = (128, 128, 0)

                    pygame.draw.rect(self.fenetre, color, (x*self.taille_bloc, y*self.taille_bloc, self.taille_bloc, self.taille_bloc))

                    font = pygame.font.Font(None, 20)
                    text_surface1 = font.render(text1, True, (255, 255, 255))
                    self.fenetre.blit(text_surface1, (x*self.taille_bloc + 5, y*self.taille_bloc + 5))

                    font = pygame.font.Font(None, 20)
                    text_surface2 = font.render(text2, True, (255, 255, 255))
                    self.fenetre.blit(text_surface2, (x*self.taille_bloc + 5, y*self.taille_bloc + 20))

                    font = pygame.font.Font(None, 20)
                    text_surface3 = font.render(text3, True, (255, 255, 255))
                    self.fenetre.blit(text_surface3, (x*self.taille_bloc + 5, y*self.taille_bloc + 35))

                    if self.mapdata[y][x]['G'] > 0:
                        text4 = f"G={self.mapdata[y][x]['G']}"
                        font = pygame.font.Font(None, 20)
                        text_surface4 = font.render(text4, True, (255, 255, 255))
                        self.fenetre.blit(text_surface4, (x*self.taille_bloc + 5, y*self.taille_bloc + 50))
                    
                    

                    
                    
            pygame.display.flip()
        

    def getVisibility(self, player):
        visible = set()
        for y in range(0, self.MAP_HEIGHT):
            for x in range(0, self.MAP_WIDTH):
                if self.mapdata[y][x][player]['C']+self.mapdata[y][x][player]['M']+self.mapdata[y][x][player]['B'] > 0:
                    for dx in range(-2, 3):
                        for dy in range(-2, 3):
                            visible.add((y+dy, x+dx))
        return visible
    
    
    def give_data(self, player):
        mapView = [[{} for x in range(self.MAP_WIDTH)] for y in range(self.MAP_HEIGHT)]
        visible = self.getVisibility(player)
        if len(visible) == 0:
            self.winner = self.opponent[player]
        for y in range(0, self.MAP_HEIGHT):
            for x in range(0, self.MAP_WIDTH):
                if (y, x) in visible:
                    mapView[y][x] = self.mapdata[y][x]
                    for k in ['C', 'M', 'B']:
                        if k+"m" in mapView[y][x][self.curPlayer]:
                            mapView[y][x][self.curPlayer].pop(k+"m")
                        if self.nbMoves[(y, x, self.curPlayer, k)] < mapView[y][x][self.curPlayer][k]:
                            mapView[y][x][self.curPlayer][k+"m"] = True

        return mapView
    
    def move(self, player, kind, y, x, ny, nx):
        if (0 <= nx < self.MAP_WIDTH and 0 <= ny < self.MAP_HEIGHT):
            if self.mapdata[y][x][player][kind] > 0 and self.nbMoves[(y, x, player, kind)] < self.mapdata[y][x][player][kind]:
                self.nbMoves[(ny, nx, player, kind)] += 1
                self.mapdata[y][x][player][kind] -= 1
                self.mapdata[ny][nx][player][kind] += 1
                return "ok"
    
    def build(self, player, y, x, kind):
        if 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT :
            if self.mapdata[y][x][self.opponent[player]]['B'] == 0 and self.mapdata[y][x][player][self.requires[kind]] > 0 and self.nbMoves[(y, x, player, self.requires[kind])] < self.mapdata[y][x][player][self.requires[kind]] and self.gold[player] >= self.price[kind]:
                self.nbMoves[(y, x, player, self.requires[kind])] += 1
                self.nbMoves[(y, x, player, kind)] += 1
                self.mapdata[y][x][player][kind] += 1
                self.gold[player] -= self.price[kind]
                return "ok"
        
    def farm(self, player, y, x):
        if 0 <= x < self.MAP_WIDTH and 0 <= y < self.MAP_HEIGHT :
            if self.nbMoves[(y, x, player, 'C')] < self.mapdata[y][x][player]['C'] and self.mapdata[y][x]['G'] > 0 and (y, x) not in self.farmed:
                self.nbMoves[(y, x, player, 'C')] += 1
                self.mapdata[y][x]['G'] -= 1
                self.farmed.add((y, x))
                self.gold[player] += 1
                self.score[player] += 1
                return "ok"
    
    def battle(self, y, x, k, attacker, defender):
        na = self.mapdata[y][x][attacker][k]
        nb = self.mapdata[y][x][defender][k]
        while na > 0 and nb > 0:
            na -= ceil(nb/2)
            nb -= ceil(na/2)
        self.mapdata[y][x][attacker][k] = na
        self.mapdata[y][x][defender][k] = nb

    def solveBattles(self, attacker, defender) :# combat rules
        for y in range(0, self.MAP_HEIGHT):
                for x in range(0, self.MAP_WIDTH):
                        nbDefenderUnitsBefore = self.mapdata[y][x][defender]['B']*self.price['B'] + \
                                self.mapdata[y][x][defender]['M']*self.price['M'] + \
                                self.mapdata[y][x][defender]['C']*self.price['C']
                        # solve the case of Military vs Military
                        for k in ['M']:  # we could do C vs C by adding 'C' here
                                self.battle(y, x, k, attacker, defender)
                        for (p, o) in [('A', 'B'), ('B', 'A')]:
                                # solve the case of Military vs Civil
                                if self.mapdata[y][x][p]['M'] > 0:
                                        self.mapdata[y][x][o]['C'] = 0
                                # solve the case of remaining Military vs Building
                                if self.mapdata[y][x][p]['M'] > 0:
                                        self.mapdata[y][x][o]['B'] = 0
                                # we cannot have multiple buildings for a given player
                                # and we cannot have buildings for two different players
                                # as recruiting requires no building
                                self.mapdata[y][x][p]['B'] = min(self.mapdata[y][x][p]['B'], 1)
                        nbDefenderUnitsAfter = self.mapdata[y][x][defender]['B']*self.price['B'] + \
                                self.mapdata[y][x][defender]['M']*self.price['M'] + \
                                self.mapdata[y][x][defender]['C']*self.price['C']
                        self.score[attacker] += nbDefenderUnitsBefore-nbDefenderUnitsAfter
    
    def changeturn(self, player):
        assert (player == self.curPlayer)
        self.solveBattles(player, self.opponent[player])
        self.curPlayer = self.opponent[player]
        self.nbMoves = defaultdict(int)
        self.farmed = set()
        self.nbRounds += 1
        if self.winner == '' and self.nbRounds >= self.MAX_NB_ROUNDS:
            if self.score['A'] < self.score['B']:
                self.winner = 'B'
            elif self.score['A'] > self.score['B']:
                self.winner = 'A'
            else:
                self.winner = 'No one'
        if self.winner != "":
            self.tokenOf = defaultdict(lambda x: "")
        return "ok"
    
    def maxi(self,x,L):
        if x == max(L):
            return 0.99
        return 0

    def prediction_to_actions(self, prediction):
        prediction = prediction.reshape((9, 16, 12))
        actions = []
        for x in range(16):
            for y in range(9):
                predictions_peons = F.softmax(prediction[y][x][:6])
                predictions_knights = F.softmax(prediction[y][x][6:10])
                predictions_castles = prediction[y][x][10:]

                Nb_peons = self.mapdata[y][x][self.curPlayer]['C']
                Nb_knights = self.mapdata[y][x][self.curPlayer]['M']
                Nb_castles = self.mapdata[y][x][self.curPlayer]['B']

                for i in range(6):
                    for k in range(int(predictions_peons[i] * Nb_peons + self.maxi(predictions_peons[i], predictions_peons))):
                        if i == 0:
                            actions.append(('move', 'C', y, x, y+1, x))
                        elif i == 1:
                            actions.append(('move', 'C', y, x, y-1, x))
                        elif i == 2:
                            actions.append(('move', 'C', y, x, y, x+1))
                        elif i == 3:
                            actions.append(('move', 'C', y, x, y, x-1))
                        elif i == 4:
                            actions.append(('farm', y, x))
                        else:
                            actions.append(('build', y, x, 'B'))
                for i in range(4):
                    for k in range(int(predictions_knights[i] * Nb_knights + self.maxi(predictions_knights[i], predictions_knights))):
                        if i == 0:
                            actions.append(('move', 'M', y, x, y+1, x))
                        elif i == 1:
                            actions.append(('move', 'M', y, x, y-1, x))
                        elif i == 2:
                            actions.append(('move', 'M', y, x, y, x+1))
                        else:
                            actions.append(('move', 'M', y, x, y, x-1))

                if predictions_castles[0] > predictions_castles[1]:
                    actions.append(('build', y, x, 'C'))
                else:
                    actions.append(('build', y, x, 'M'))
        return actions
    
    def play_step(self, player, prediction):
        if self.Test:
            pass
            # pygame.time.wait(self.pause)

        self.give_data(player)
        if self.winner == self.opponent[player]:
            return -100, True, self.score
        
        previous_score = self.score[player]

        actions = self.prediction_to_actions(prediction)
        print(len(actions))
        for action in actions:
            if action[0] == 'move':
                self.move(player, action[1], action[2], action[3], action[4], action[5])
            elif action[0] == 'build':
                self.build(player, action[1], action[2], action[3])
            elif action[0] == 'farm':
                self.farm(player, action[1], action[2])
        self.draw_grid()
        self.changeturn(player)
        self.changeturn(self.opponent[player])

        new_score = self.score[player]
        
        self.give_data(self.opponent[player])
        if self.winner == player:
            return 100, True, self.score
        
        return new_score - new_score, False, self.score