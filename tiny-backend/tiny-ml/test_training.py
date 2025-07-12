# run this just to test the training loop

import numpy as np
import random
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tinygrad.tensor import Tensor
from tinygrad.nn.optim import Adam
from tinygrad.helpers import get_parameters
from tinygrad.dtype import dtypes

from model import ChessNet
from train import train_step
from chess_helpers.game_logic import history_to_tensor

def generate_mock_data(buffer_size, policy_size):
    """Generates a replay buffer with mock data to test the training loop."""
    print(f"Generating {buffer_size} samples of mock data...")
    replay_buffer = []
    
    mock_history = [np.zeros((12, 8, 8), dtype=np.float32) for _ in range(8)]

    for _ in range(buffer_size):
        white_to_move = random.choice([True, False])
        pi = np.random.rand(policy_size).astype(np.float32)
        pi /= pi.sum()
        z = np.random.uniform(-1, 1)
        replay_buffer.append((mock_history, white_to_move, pi, float(z)))
    print("Mock data generated.")
    return replay_buffer

if __name__ == "__main__":
    print("--- Running Training Step Test ---")
    Tensor.training = True
    
    model = ChessNet(dtype=dtypes.half)
    optimizer = Adam(get_parameters(model), lr=1e-4)

    BATCH_SIZE = 64
    POLICY_SIZE = 4672 
    debug_replay_buffer = generate_mock_data(buffer_size=BATCH_SIZE * 4, policy_size=POLICY_SIZE)
    
    print(f"Running {100} training steps with a batch size of {BATCH_SIZE}...")
    for step in range(100):
        batch_indices = np.random.choice(len(debug_replay_buffer), BATCH_SIZE, replace=False)
        batch_histories = [debug_replay_buffer[i][0] for i in batch_indices]
        batch_colors = [debug_replay_buffer[i][1] for i in batch_indices]
        batch_target_policies = np.array([debug_replay_buffer[i][2] for i in batch_indices])
        batch_target_values = np.array([debug_replay_buffer[i][3] for i in batch_indices]).reshape(-1, 1)
        board_tensors = Tensor.cat(*[history_to_tensor(hist, col) for hist, col in zip(batch_histories, batch_colors)], dim=0)
        target_policies = Tensor(batch_target_policies, dtype=dtypes.half)
        target_values = Tensor(batch_target_values, dtype=dtypes.half)
        value_loss, policy_loss = train_step(optimizer, model, board_tensors, target_policies, target_values)
        
        if (step + 1) % 10 == 0:
            print(f"Debug Step {step+1:3d}: Value Loss = {value_loss.item():.4f}, Policy Loss = {policy_loss.item():.4f}")
    
    print("\n--- Training Step Test Finished ---") 