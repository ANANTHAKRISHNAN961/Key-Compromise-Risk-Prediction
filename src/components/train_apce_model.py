import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from kms_env import KmsEnv
import joblib

# --- Configuration ---
MODELS_DIR = "models"
LOGS_DIR = "logs"
TOTAL_TIMESTEPS = 50000

# Create directories if they don't exist
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# --- Environment Setup ---
# Instantiate the custom environment
env = KmsEnv()

# It's a good practice to check if your custom environment is compliant with the Gym API
check_env(env)

# --- Model Training ---
# We'll use the Proximal Policy Optimization (PPO) algorithm, which is a good default choice.
# 'MlpPolicy' means we're using a multi-layer perceptron (a standard neural network) for the policy.
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=LOGS_DIR)

print("--- Starting APCE Model Training ---")
# The learn() method starts the training process.
# The agent will interact with the environment for the specified number of timesteps.
model.learn(total_timesteps=TOTAL_TIMESTEPS)
print("--- APCE Model Training Finished ---")

# --- Save the Model ---
# The trained model is saved so it can be loaded later for inference.
model_path = os.path.join(MODELS_DIR, "apce_model.zip")
model.save(model_path)

print(f"Model saved to {model_path}")

# --- Example of Loading and Using the Model ---
# del model # remove to demonstrate loading

# loaded_model = PPO.load(model_path, env=env)

# print("\n--- Testing Loaded Model ---")
# obs, _ = env.reset()
# for i in range(10):
#     action, _states = loaded_model.predict(obs, deterministic=True)
#     obs, reward, terminated, truncated, info = env.step(action)
#     print(f"Step {i+1}: State={obs}, Action={action}, Reward={reward:.2f}")
#     if terminated or truncated:
#         break
# env.close()
