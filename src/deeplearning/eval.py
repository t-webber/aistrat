import random
import math
import numpy as np
import torch
from collections import deque
from mainIA import gameIA
from model import Linear_QNet, QTrainer
from helper import plot
import os
from agent import Agent

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
        self.load_model()
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        #self.load_model()

    def get_state(self, game, player):
        data = game.give_data(player)
        state = []
        for y in range(game.MAP_HEIGHT):
            for x in range(game.MAP_WIDTH):
                state.append(data[y][x]['G'])
                state.append(data[y][x][player]['C'])
                state.append(data[y][x][player]['M'])
                state.append(data[y][x][player]['B'])
                state.append(data[y][x][game.opponent[player]]['C'])
                state.append(data[y][x][game.opponent[player]]['M'])
                state.append(data[y][x][game.opponent[player]]['B'])
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

    def get_action(self,state):
        # random moves : tradeoff exploration / exploitation
        self.epsilon = 160 - self.n_games
        if random.randint(0, 400) < self.epsilon:
            final_move = random.randint(0, 5)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            final_move = torch.argmax(prediction).item()

        return final_move

    def load_model(self, file_name='model2.pth'):
        model_folder_path = './model'
        file_name = os.path.join(model_folder_path, file_name)

        # Assurez-vous que le modèle est initialisé
        self.model = Linear_QNet(9*16*7+3, 512, 512, 9*16*(4+1+1+4+2))

        # Chargez l'état du modèle
        self.model.load_state_dict(torch.load(file_name))


def eval():
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
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        reward, done, score = game.play_step(final_move)
        if done:
            game.reset()
            agent.n_games += 1

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
            #if agent.n_games%1000 == 0:
            #plot(plot_scores0, plot_mean_scores0, plot_scores1, plot_mean_scores1)

if __name__ == '__main__':
    eval()
