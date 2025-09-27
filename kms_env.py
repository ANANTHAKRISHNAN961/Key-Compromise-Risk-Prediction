import gymnasium as gym
import numpy as np

class KmsEnv(gym.Env):
    """
    A custom Gym environment to simulate a Key Management Service (KMS) for our RL agent.
    The agent's goal is to take actions to keep the key's overall risk score low.
    """
    def __init__(self):
        super(KmsEnv, self).__init__()

        # --- DEFINE ACTION SPACE ---
        # The agent can choose from 4 actions: 0, 1, 2, 3
        # 0: NO_OP (Do nothing)
        # 1: ALERT_SOC (Notify security team)
        # 2: FORCE_ROTATE_KEY (Mitigate static risk)
        # 3: RESTRICT_PERMISSIONS (Mitigate dynamic risk)
        self.action_space = gym.spaces.Discrete(4)

        # --- DEFINE OBSERVATION SPACE (STATE) ---
        # The state is what the agent "sees". It's an array of two numbers:
        # [static_vulnerability_score, dynamic_anomaly_score]
        # Both scores range from 0.0 to 1.0.
        self.observation_space = gym.spaces.Box(low=0.0, high=1.0, shape=(2,), dtype=np.float32)

        # --- INITIALIZE STATE ---
        self.state = np.array([0.0, 0.0], dtype=np.float32)
        self.max_steps = 100 # An episode ends after 100 steps
        self.current_step = 0

    def reset(self, seed=None, options=None):
        """
        Resets the environment to a new starting state for a new episode.
        """
        super().reset(seed=seed)
        # Start with a random initial risk state
        self.state = self.observation_space.sample()
        self.current_step = 0
        
        # Return the initial state and an empty info dict
        return self.state, {}

    def step(self, action):
        """
        This is the core of the environment. It takes an agent's action and returns
        the result: the new state, the reward, and whether the episode is over.
        """
        self.current_step += 1
        
        # --- 1. DEFINE REWARD LOGIC ---
        reward = 0
        # Start with a small negative reward to encourage faster resolution
        reward -= 0.1 

        # Penalize the agent based on the current risk (the higher the risk, the worse the penalty)
        current_risk = (self.state[0] + self.state[1]) / 2.0
        reward -= current_risk

        # --- 2. DEFINE STATE TRANSITION LOGIC (How actions change the state) ---
        static_score, dynamic_score = self.state

        if action == 0: # NO_OP
            # Doing nothing makes the situation slightly worse if risk is high
            static_score += 0.05 * current_risk
            dynamic_score += 0.05 * current_risk
            reward -= 0.2 # Penalize for being passive during high risk
        
        elif action == 1: # ALERT_SOC
            # Alerting doesn't change the risk, but it's a valid action
            reward += 0.1 # Small reward for taking a non-disruptive step
        
        elif action == 2: # FORCE_ROTATE_KEY
            # This action drastically reduces static risk
            static_score *= 0.1 # Reduce static score by 90%
            reward += 1.0 # Reward for taking a strong corrective action

        elif action == 3: # RESTRICT_PERMISSIONS
            # This action drastically reduces dynamic risk
            dynamic_score *= 0.1 # Reduce dynamic score by 90%
            reward += 1.0 # Reward for taking a strong corrective action

        # --- 3. SIMULATE EXTERNAL FACTORS ---
        # Randomly, a new "threat" might appear, increasing the scores
        if np.random.rand() < 0.1: # 10% chance of a new threat
             static_score += np.random.rand() * 0.2
             dynamic_score += np.random.rand() * 0.4

        # Ensure scores stay within the valid [0, 1] range
        self.state = np.clip([static_score, dynamic_score], 0.0, 1.0).astype(np.float32)

        # --- 4. CHECK IF EPISODE IS OVER ---
        terminated = self.current_step >= self.max_steps
        
        # A huge penalty if the agent lets the risk get too high (a simulated compromise)
        if self.state[0] > 0.9 and self.state[1] > 0.9:
            reward -= 100
            terminated = True # End the episode on compromise

        return self.state, reward, terminated, False, {}