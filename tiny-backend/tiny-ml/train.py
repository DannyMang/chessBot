import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import time
import random
from collections import deque
from typing import List, Tuple
import pickle

import wandb
from tinygrad.tensor import Tensor
from tinygrad.nn.optim import Adam, Optimizer
from tinygrad.helpers import getenv
from tinygrad import TinyJit
from tinygrad.nn.state import get_parameters, safe_load, safe_save, get_state_dict
from tinygrad.dtype import dtypes

from model import ChessNet
from mcts import mcts_alphazero, MCTSNode
from chess_helpers.cpp import chess_engine
from chess_helpers.game_logic import get_board_planes, history_to_tensor, move_to_policy_index

Tensor.training=True

def create_policy_vector(root: MCTSNode, temperature: float) -> np.ndarray:
    """
    Creates a policy vector from the visit counts of the root node's children.
    Applies temperature scaling to encourage exploration.
    """
    policy_vector = np.zeros(4672, dtype=np.float32)
    visit_counts = np.array([child.visit_count for child in root.children])
    
    if np.sum(visit_counts) > 0:
        powered_visits = visit_counts ** (1 / temperature)
        distribution = powered_visits / np.sum(powered_visits)
        
        for i, child in enumerate(root.children):
            move_idx = move_to_policy_index(child.move)
            if move_idx is not None and move_idx < 4672:
                policy_vector[move_idx] = distribution[i]
    return policy_vector

@TinyJit
def train_step(optimizer: Optimizer, model: ChessNet, board_tensors: Tensor, target_policies: Tensor, target_values: Tensor) -> Tuple[Tensor, Tensor]:
    """
    JIT-compiled training step for max performance.
    """
    predicted_policies, predicted_values = model(board_tensors)

    value_loss = (predicted_values - target_values).square().mean()
    policy_loss = -(target_policies * predicted_policies.log_softmax()).sum() / len(board_tensors)
    
    loss = value_loss + policy_loss
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    return value_loss.realize(), policy_loss.realize()


if __name__ == "__main__":
    config = {
        "learning_rate": 0.001,
        "batch_size": 64,
        "mcts_simulations": 100,
        "epochs": 10,
        "games_per_epoch": 10,
        "network_architecture": "resnet_18_custom",
        "dirichlet_alpha": 0.3,
        "dirichlet_epsilon": 0.25,
        "temperature_initial": 1.0,
        "temperature_final": 0.1,
        "temperature_decay_half_life": 30, 
        "replay_buffer_size": 50000
    }

    if getenv("WANDB"):
        import wandb
        wandb_args = {"id": wandb_id, "resume": "must"} if (wandb_id := getenv("WANDB_RESUME", "")) else {}
        wandb.init(project="chess-alphazero-tinygrad", config=config, **wandb_args)

    model = ChessNet(dtype=dtypes.half)
    optimizer = Adam(get_parameters(model), lr=config["learning_rate"])
    os.makedirs("models", exist_ok=True)
    if os.path.exists("models/chess_net_checkpoint.safetensors"):
        model.load_state_dict(safe_load("models/chess_net_checkpoint.safetensors"))
        print("Loaded model weights from models/chess_net_checkpoint.safetensors")

    print("--- Running in Training Mode ---")
    
    # Load replay buffer if it exists
    replay_buffer_path = "replay_buffer.pkl"
    if os.path.exists(replay_buffer_path):
        with open(replay_buffer_path, 'rb') as f:
            replay_buffer = pickle.load(f)
        print(f"Loaded replay buffer with {len(replay_buffer)} experiences.")
    else:
        replay_buffer = deque(maxlen=config["replay_buffer_size"])
        print("No existing replay buffer found. Starting a new one.")

    start_time = time.time()

    for epoch in range(config["epochs"]):
        print(f"\n--- Epoch {epoch+1}/{config['epochs']} ---")
        
        # self-play
        for game_num in range(config["games_per_epoch"]):
            game_history_for_replay = []
            board_plane_history = []
            board = chess_engine.ChessBitboard()
            board.set_starting_position()
            move_count = 0
            
            while True:
                board_plane_history.append(get_board_planes(board))
                
                root_node = MCTSNode(board=board)
                
                best_child_node = mcts_alphazero(
                    model,
                    root_node, 
                    list(board_plane_history),
                    num_simulations=config["mcts_simulations"],
                    dirichlet_alpha=config["dirichlet_alpha"],
                    dirichlet_epsilon=config["dirichlet_epsilon"]
                )
    
                if best_child_node is None: break

                temp = config["temperature_initial"] * (0.5 ** (move_count / config["temperature_decay_half_life"]))
                temp = max(temp, config["temperature_final"])

                policy = create_policy_vector(root_node, temp)

                game_history_for_replay.append([list(board_plane_history), board.white_to_move, policy, 0.0])
                board.make_move(best_child_node.move)
                best_child_node.parent = None

                move_count += 1
                if board.is_game_over(): break
            
            result = board.get_result()
            for i in range(len(game_history_for_replay)):
                game_history_for_replay[i][3] = result if (i % 2) == (len(game_history_for_replay) % 2) else -result
            replay_buffer.extend(game_history_for_replay)
            print(f"  Game {game_num + 1}/{config['games_per_epoch']} finished. Result: {result}, Moves: {move_count}. Replay buffer size: {len(replay_buffer)}")

        print(f"Epoch {epoch+1}: Self-play finished. Replay buffer size: {len(replay_buffer)}")
        
        # Save the replay buffer after the self-play phase
        with open(replay_buffer_path, 'wb') as f:
            pickle.dump(replay_buffer, f)
        print(f"Replay buffer with {len(replay_buffer)} experiences saved to {replay_buffer_path}")


        # Training 
        if len(replay_buffer) < config["batch_size"]:
            print("Not enough data in replay buffer. Skipping training for this epoch.")
            continue

        print("Training on collected data...")
        num_batches = len(replay_buffer) // config["batch_size"]
        for i in range(num_batches):
            batch_indices = np.random.choice(len(replay_buffer), size=config["batch_size"], replace=False)
            
            batch_histories = [replay_buffer[i][0] for i in batch_indices]
            batch_colors = [replay_buffer[i][1] for i in batch_indices]
            batch_target_policies = np.array([replay_buffer[i][2] for i in batch_indices])
            batch_target_values = np.array([replay_buffer[i][3] for i in batch_indices]).reshape(-1, 1)

            board_tensors = Tensor.cat(*[history_to_tensor(hist, col) for hist, col in zip(batch_histories, batch_colors)], dim=0)
            target_policies = Tensor(batch_target_policies, dtype=dtypes.half)
            target_values = Tensor(batch_target_values, dtype=dtypes.half)

            value_loss, policy_loss = train_step(optimizer, model, board_tensors, target_policies, target_values)
            
            if (i + 1) % 10 == 0:
                print(f"  Batch {i+1}/{num_batches}: Value Loss = {value_loss.item():.4f}, Policy Loss = {policy_loss.item():.4f}")

            if getenv("WANDB"):
                wandb.log({
                    "epoch": epoch + 1,
                    "train/value_loss": value_loss.item(),
                    "train/policy_loss": policy_loss.item(),
                    "train/total_loss": value_loss.item() + policy_loss.item(),
                })
        
        if getenv("WANDB"):
                wandb.log({"replay_buffer_size": len(replay_buffer)})

        elapsed_time = time.time() - start_time
        epochs_done = epoch + 1
        avg_time_per_epoch = elapsed_time / epochs_done
        remaining_epochs = config["epochs"] - epochs_done
        eta_seconds = remaining_epochs * avg_time_per_epoch

        eta_h = int(eta_seconds // 3600)
        eta_m = int((eta_seconds % 3600) // 60)
        eta_s = int(eta_seconds % 60)
        
        elapsed_h = int(elapsed_time // 3600)
        elapsed_m = int((elapsed_time % 3600) // 60)
        
        print(f"Epoch {epochs_done}/{config['epochs']} summary | Elapsed: {elapsed_h}h {elapsed_m}m | ETA: {eta_h}h {eta_m}m {eta_s}s")
        
        state_dict = get_state_dict(model)
        safe_save(state_dict, "models/chess_net_checkpoint.safetensors")
        print(f"  Model checkpoint saved to models/chess_net_checkpoint.safetensors")

    print("Training finished!")
    if getenv("WANDB"):
        wandb.finish()

