import torch
import random
import torch.nn as nn
import torch.nn.functional as F
from collections import deque
from game import FlappyBirdAI
import os
import matplotlib.pyplot as plt
from IPython import display

MAX_MEM = 100_000
BATCH_SIZE = 1000
LR = 1e-3

plt.ion()

#-------------------MODEL----------------------------------
class Linear_QNet(nn.Module):

    def __init__(self, input_size, hidden_size, output_size, deep=False):
        super().__init__()
        self.deep = deep

        self.init = nn.Linear(input_size, hidden_size)
        if not deep:
            self.hidden = nn.Linear(hidden_size, output_size)
        if deep:
            self.hidden = nn.Linear(hidden_size,hidden_size)
            self.second_hidden = nn.Linear(hidden_size, output_size)
    
    def forward(self,x):
        x = F.relu(self.init(x))
        x = self.hidden(x)
        if self.deep:
            x = F.relu(x)
            x = self.second_hidden(x)

        return F.tanh(x)
        #return F.sigmoid(x)
    
    def save(self, file_name = 'flappy_bird.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)


#------------------MODEL 2 -----------------------------------
class TripleOjo(nn.Module):

    def __init__(self):
        super().__init__()
        self.ojos = nn.Linear(3,5)
        self.cerebro = nn.Linear(5,1)
    
    def forward(self, x):
        x = self.ojos(x)
        x = self.cerebro(F.relu(x))
        return F.relu(x)

#--------------------TRAINNING--------------------------------
class QTrainer:
    def __init__(self, model, lr, gamma):
        self.model=model
        self.lr = lr
        self.gamma = gamma
        self.optimizer = torch.optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = torch.nn.MSELoss()
    
    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward,dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward,0)
            done = (done,)
        
        # 1: predicted Q value with current state
        pred = self.model(state)
        target = pred.clone()
        try:
            for idx in range(len(done)):
                Q_new = reward[idx]
                if not done[idx]:
                    Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
                
                target[idx][torch.argmax(action).item()] = Q_new
        except:
            print(f"target: {target}")
            print(f"target.shape: {target.shape}")
            print(f"idx: {idx}, argmax:{torch.argmax(action).item()}")
            print(f"action: {action}")
        # 2: Q_new = r + y * max(next_pred Q)
        #pred.clone()
        #preds[argmax(action)] = Q_new
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        
        self.optimizer.step()

#---------------------AGENT-----------------------------
class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen = MAX_MEM)
        self.model = TripleOjo()
        self.trainer = QTrainer(self.model,lr=LR, gamma=self.gamma)
        

    def get_state(self, game):
        state = game.get_game_state()
        return state
        #bp_y, tp_y, p_x, bird_y, bird_m = game.get_game_state()

    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self,state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random_moves: tradeoff exploration / explotation
        self.epsilon = 80 - self.n_games
        final_move = [0]
        if random.randint(0,200) < self.epsilon:
            move = random.randint(0,1)
            final_move[0] = move
        else:
            state0 = torch.tensor(state,dtype=torch.float)
            prediction =  self.model(state0).item()
            move = [0] if prediction==0.0 else [1]
       
        return final_move

def plot(scores, mean_scores):
    display.clear_output(wait=True)
    display.display(plt.gcf())
    plt.clf()
    plt.title("Training...")
    plt.xlabel('Number of games')
    plt.ylabel('Score')
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))


def train():
    plot_mean_scores = []
    total_score = 0
    plot_scores = []
    record = 0

    agent = Agent()
    game = FlappyBirdAI()

    while True:
        
        # get old state
        state_old = agent.get_state(game)
        
        # get move
        move = agent.get_action(state_old)

        #perform move, get next state
        reward, game_active, score = game.play_step(ai=True, agent_move=move)
        done = not game_active
        state_new = agent.get_state(game)
        
        # train short memory
        agent.train_short_memory(state_old, move, reward,state_new, done)
        
        # remember
        agent.remember(state_old, move, reward,state_new, done)

        if done:
            # train long memory plot results
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            
            if score > record:
                record = score
                agent.model.save()
            print(f'Game: {agent.n_games}, Score: {score}, Record: {record}')

            plot_scores.append(score)
            total_score += score
            mean_score = total_score /agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()
