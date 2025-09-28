import gymnasium as gym
from gymnasium import spaces
import numpy as np

class KmsEnv(gym.Env):
    metadata = {'render_modes': ['human']}

    def __init__(self):
        super(KmsEnv, self).__init__()
        self.action_space = spaces.Discrete(5)
        self.observation_space = spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32)
        self.reset()

    def step(self, action):
        current_risk = self.state[0]
        reward = 0
        
        # 1. Define risk bands
        is_low_risk = current_risk < 0.3
        is_medium_risk = 0.3 <= current_risk < 0.6
        is_high_risk = 0.6 <= current_risk < 0.8
        is_critical_risk = current_risk >= 0.8

        # 2. Define cost of each action (business disruption)
        action_cost = {0: 0, 1: 0.1, 2: 0.4, 3: 0.6, 4: 1.0}
        reward -= action_cost[action]

        # 3. Reward or penalize based on action appropriateness
        if action == 0: # NO_OP
            if is_low_risk: reward += 1.0 # Correct
            else: reward -= 2.0 # Incorrect, should have done something
        
        elif action == 1: # ALERT_SOC
            if is_medium_risk: reward += 1.8 # Good choice
            elif is_low_risk: reward -= 0.5 # Overkill
            else: reward -= 1.0 # Under-reaction

        elif action == 2: # FORCE_ROTATE_KEY
            if is_high_risk: reward += 2.2 # Correct
            elif is_medium_risk: reward += 0.5 # Acceptable, but costly
            else: reward -= 1.5 # Severe over-reaction

        elif action == 3: # RESTRICT_PERMISSIONS
            if is_high_risk: reward += 2.8 # Very good choice
            elif is_critical_risk: reward += 1.0 # Good, but maybe not enough
            else: reward -= 2.0 # Severe over-reaction

        elif action == 4: # QUARANTINE_KEY
            if is_critical_risk: reward += 3.0 # Absolutely correct, but less extreme reward
            else: reward -= 5.0 # Extreme over-reaction, higher penalty

        # 4. Simulate the effect of the action on the state for the next step
        # This is a simplified model of how risk might evolve
        if action == 1: self.state[0] *= 0.95 # Alerting slightly reduces future risk perception
        elif action == 2: self.state[0] *= 0.7 # Rotation significantly reduces risk
        elif action == 3: self.state[0] *= 0.5 # Restriction is very effective
        elif action == 4: self.state[0] = 0.0 # Quarantine neutralizes risk
        
        # Natural decay/change in risk over time
        self.state[0] *= np.random.uniform(0.9, 1.1) # Add some randomness
        self.state = np.clip(self.state, 0, 1)

        terminated = bool(self.state[0] < 0.05) # Episode ends if risk is neutralized
        return self.state, reward, terminated, False, {}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # Start with a random risk score for each new episode
        self.state = np.array([np.random.uniform(0.05, 1.0)], dtype=np.float32)
        return self.state, {}

    def render(self, mode='human'):
        if mode == 'human':
            print(f"Current Risk: {self.state[0]:.3f}")

if __name__ == '__main__':
    env = KmsEnv()
    obs, info = env.reset()
    for _ in range(20):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Action: {action}, Risk: {obs[0]:.3f}, Reward: {reward:.3f}")
        if terminated or truncated:
            print("--- Episode Finished ---")
            obs, info = env.reset()
    env.close()
