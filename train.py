from kms_env import KmsEnv
from dqn_agent import DQNAgent
from collections import deque
import torch
import numpy as np
import matplotlib.pyplot as plt

# --- 1. INSTANTIATE THE ENVIRONMENT AND AGENT ---
env = KmsEnv()
agent = DQNAgent(state_size=2, action_size=4)

# --- 2. DEFINE THE TRAINING FUNCTION ---
def train(n_episodes=2000, max_t=100, eps_start=1.0, eps_end=0.01, eps_decay=0.995):
    """
    Train the DQN Agent.
    
    Params
    ======
        n_episodes (int): maximum number of training episodes
        max_t (int): maximum number of timesteps per episode
        eps_start (float): starting value of epsilon, for epsilon-greedy action selection
        eps_end (float): minimum value of epsilon
        eps_decay (float): multiplicative factor (per episode) for decreasing epsilon
    """
    scores = []                        # list containing scores from each episode
    scores_window = deque(maxlen=100)  # last 100 scores
    eps = eps_start                    # initialize epsilon
    
    for i_episode in range(1, n_episodes+1):
        state, _ = env.reset()
        score = 0
        for t in range(max_t):
            action = agent.act(state, eps)
            next_state, reward, done, _, _ = env.step(action)
            agent.step(state, action, reward, next_state, done)
            state = next_state
            score += reward
            if done:
                break 
        scores_window.append(score)       # save most recent score
        scores.append(score)              # save most recent score
        eps = max(eps_end, eps_decay*eps) # decrease epsilon
        
        print(f'\rEpisode {i_episode}\tAverage Score: {np.mean(scores_window):.2f}', end="")
        if i_episode % 100 == 0:
            print(f'\rEpisode {i_episode}\tAverage Score: {np.mean(scores_window):.2f}')
            
    # Save the trained model
    torch.save(agent.qnetwork_local.state_dict(), 'checkpoint.pth')
    return scores

# --- 3. RUN THE TRAINING ---
scores = train()

# --- 4. PLOT THE RESULTS ---
fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(np.arange(len(scores)), scores)
plt.ylabel('Score')
plt.xlabel('Episode #')
plt.title('Agent Training Performance')
plt.show()