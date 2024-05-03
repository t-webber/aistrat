import random
import math
import numpy as np
import torch
from collections import deque
from mainIA import gameIA
from model import Linear_QNet, QTrainer
from helper import plot
import os
import time

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) #popleft()
        self.model = Linear_QNet(9*16*7+3, 512, 512, 9*16*(4+1+1+4+2))
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        #self.load_model()

    def get_state(self, game, player):
        data = game.give_data(player)
        state = []
        for y in range(game.MAP_HEIGHT):
            for x in range(game.MAP_WIDTH):
                if data[y][x]:
                    state.append(data[y][x]['G'])
                    state.append(data[y][x][player]['C'])
                    state.append(data[y][x][player]['M'])
                    state.append(data[y][x][player]['B'])
                    state.append(data[y][x][game.opponent[player]]['C'])
                    state.append(data[y][x][game.opponent[player]]['M'])
                    state.append(data[y][x][game.opponent[player]]['B'])
                else :
                    state.extend([-1,0,0,0,-1,-1,-1])
        state.append(game.gold[player])
        state.append(game.score[player])
        state.append(game.score[game.opponent[player]])
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
            # list of tuples
        else :
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_prediction(self,state):
        self.epsilon = 160 - self.n_games
        if random.randint(0, 400) < self.epsilon:
            prediction = torch.tensor(np.random.rand(9*16*(4+1+1+4+2)), dtype=torch.float)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)


        return prediction

    def load_model(self, file_name='model2.pth'):
        model_folder_path = './model'
        file_name = os.path.join(model_folder_path, file_name)

        # Assurez-vous que le modèle est initialisé
        self.model = Linear_QNet(9*16*7+3, 512, 512, 9*16*(4+1+1+4+2))

        # Chargez l'état du modèle
        self.model.load_state_dict(torch.load(file_name))


def train():
    plot_scores0 = []
    plot_scores1 = []
    plot_mean_scores0 = []
    plot_mean_scores1 = []
    total_score0 = 0
    total_score1 = 0
    record0 = 0
    record1 = 0
    agent = Agent()
    game = gameIA()
    T = True
    while T:
        # t0=time.time()
        state_old = agent.get_state(game, 'A')
        # t1=time.time()
        # print("temps recup state",t1-t0)
        prediction = agent.get_prediction(state_old)
        # t0=time.time()
        # print("temps pour coup", t0-t1)
        reward, done, score = game.play_step('A',prediction)
        # t1=time.time()
        # print("temps jouer",t1-t0)
        state_new= agent.get_state(game,'A')
        # t0=time.time()
        # print("temps recup state",t0-t1)
        agent.train_short_memory(state_old, prediction, reward, state_new, done) 
        # t1=time.time()
        # print("temps pour train",t1-t0)
        agent.remember(state_old, prediction, reward, state_new, done) 
        # t0=time.time()
        # print("temps remember",t0-t1)

        print('Score', score)
        if done:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score[0] > record0:
                record0 = score[0]
                agent.model.save()

            if score[1] > record1:
                record1 = score[1]

            plot_scores0.append(score[0])
            plot_scores1.append(score[1])
            total_score0 += score[0]
            total_score1 += score[1]
            mean_score0 = total_score0 / agent.n_games
            mean_score1 = total_score1 / agent.n_games
            plot_mean_scores0.append(mean_score0)
            plot_mean_scores1.append(mean_score1)

            print('Game', agent.n_games, 'Score', score, 'Record somme', record0,'Record maxi',record1,'Moyenne',mean_score0 )
            plot(plot_scores0, plot_mean_scores0,plot_scores1,plot_mean_scores1)

if __name__ == '__main__':
    train()
