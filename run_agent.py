import torch
import numpy as np
from dqn_agent import DQNAgent # Import your agent class

# --- 1. SETUP THE AGENT ---
# Create an instance of your agent
agent = DQNAgent(state_size=2, action_size=4)

# Load the trained weights from your checkpoint file
agent.qnetwork_local.load_state_dict(torch.load('checkpoint.pth'))
print("✅ Trained model 'checkpoint.pth' loaded successfully.")

# --- 2. DEFINE A FUNCTION TO GET THE AGENT'S ACTION ---
def get_best_action(static_score, dynamic_score):
    """
    This function takes two scores, gives them to the agent,
    and returns the best action.
    """
    # Create the state array, which is the input for the agent
    state = np.array([static_score, dynamic_score], dtype=np.float32)
    
    # Use the agent's act() method to choose the best action.
    # We set eps (epsilon) to 0.0 because we are now making decisions, not exploring.
    action = agent.act(state, eps=0.0)
    
    return action

# --- 3. MAP ACTIONS TO HUMAN-READABLE NAMES ---
action_map = {
    0: "NO_OP (Do nothing)",
    1: "ALERT_SOC (Notify security team)",
    2: "FORCE_ROTATE_KEY (Mitigate static risk)",
    3: "RESTRICT_PERMISSIONS (Mitigate dynamic risk)"
}

# --- 4. RUN EXAMPLES TO SEE YOUR AGENT IN ACTION ---
if __name__ == "__main__":
    # --- EXAMPLE 1: Low risk scenario ---
    print("\n--- Scenario 1: Low Risk ---")
    static_input_1 = 0.1
    dynamic_input_1 = 0.2
    print(f"INPUT: Static Score={static_input_1}, Dynamic Score={dynamic_input_1}")
    
    chosen_action_1 = get_best_action(static_input_1, dynamic_input_1)
    
    print(f"OUTPUT: Agent chose action code '{chosen_action_1}' which means '{action_map[chosen_action_1]}'")
    
    # --- EXAMPLE 2: High risk scenario ---
    print("\n--- Scenario 2: High Risk ---")
    static_input_2 = 0.9
    dynamic_input_2 = 0.8
    print(f"INPUT: Static Score={static_input_2}, Dynamic Score={dynamic_input_2}")

    chosen_action_2 = get_best_action(static_input_2, dynamic_input_2)
    
    print(f"OUTPUT: Agent chose action code '{chosen_action_2}' which means '{action_map[chosen_action_2]}'")