import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os


class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size1, hidden_size2 ,output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size1)
        self.linear2 = nn.Linear(hidden_size1, hidden_size2)
        self.linear3 = nn.Linear(hidden_size2, output_size)
        self.batch_norm = nn.BatchNorm1d(output_size)

    def forward(self,x):
        x = F.relu(self.linear1(x))
        x = F.relu(self.linear2(x))
        x = F.sigmoid(self.linear3(x))
        return x

    def save(self, file_name='model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class QTrainer :
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(),lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, states, predictions, rewards, next_states, dones):
        states = torch.tensor(states, dtype=torch.float)
        next_states = torch.tensor(next_states, dtype=torch.float)
        predictions = torch.tensor(predictions, dtype=torch.float)
        rewards = torch.tensor(rewards, dtype=torch.float)

        if len(states.shape) == 1 :
            # (1,x)
            states = torch.unsqueeze(states, 0)
            next_states = torch.unsqueeze(next_states, 0)
            predictions = torch.unsqueeze(predictions, 0)
            rewards = torch.unsqueeze(rewards, 0)
            dones = (dones, )

        pred = self.model(states)

        target = pred.clone()
        for idx in range(len(dones)):
            Q_new = rewards[idx]
            if not dones[idx]:
                Q_new += self.gamma * torch.max(self.model(next_states[idx]))
            #print(predictions)
            target[idx] = Q_new*predictions[idx]

        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()


