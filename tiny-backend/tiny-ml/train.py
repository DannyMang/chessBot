import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import wandb
from tinygrad.tensor import Tensor
from tinygrad.nn import optim
from collections import deque
from tinygrad.nn.state import get_parameters
from chess_helpers.cpp import chess_engine 
from model import ChessNet
from mcts import mcts_alphazero, MCTSNode
from chess_helpers.game_logic import get_board_planes, history_to_tensor, move_to_policy_index


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

def main():
    #init wandb
    config = {
        "learning_rate": 0.001,
        "batch_size": 128,
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
    wandb.init(project="chess-alphazero-tinygrad", config=config)
    model = ChessNet()
    optimizer = optim.Adam(get_parameters(model), lr=wandb.config.learning_rate)
    
    # Use a deque for a fixed-size, rolling replay buffer
    replay_buffer = deque(maxlen=wandb.config.replay_buffer_size) 
    
    for epoch in range(wandb.config.epochs):
        # Self-Play Phase 
        for _ in range(wandb.config.games_per_epoch):
            game_history_for_replay = []
            board_plane_history = []
            board = chess_engine.ChessBitboard()
            board.set_starting_position()
            move_count = 0
            
            while True:
                # Add current board state to history
                board_plane_history.append(get_board_planes(board))
                
                root_node = MCTSNode(board=board)
                
                best_child_node = mcts_alphazero(
                    model,
                    root_node, 
                    list(board_plane_history),
                    num_simulations=wandb.config.mcts_simulations,
                    dirichlet_alpha=wandb.config.dirichlet_alpha,
                    dirichlet_epsilon=wandb.config.dirichlet_epsilon
                )
    
                if best_child_node is None: break

                # --- Temperature-based Policy Vector ---
                policy = np.zeros(4672, dtype=np.float32)
                
                # Determine temperature
                # In early stages of the game, use higher temperature for more exploration.
                temp = wandb.config.temperature_initial * (0.5 ** (move_count / wandb.config.temperature_decay_half_life))
                temp = max(temp, wandb.config.temperature_final)

                visit_counts = np.array([child.visit_count for child in root_node.children])
                if np.sum(visit_counts) > 0:
                    powered_visits = visit_counts ** (1 / temp)
                    distribution = powered_visits / np.sum(powered_visits)
                    
                    for i, child in enumerate(root_node.children):
                        move_idx = move_to_policy_index(child.move)
                        if move_idx is not None and move_idx < 4672:
                            policy[move_idx] = distribution[i]

                game_history_for_replay.append([list(board_plane_history), board.white_to_move, policy, 0.0])
                board.make_move(best_child_node.move)
                best_child_node.parent = None

                move_count += 1
                if board.is_game_over(): break
            
            result = board.get_result()
            for i in range(len(game_history_for_replay)):
                # The value target for each state is the final game result, from the perspective of the player at that state.
                game_history_for_replay[i][3] = result if (i % 2) == (len(game_history_for_replay) % 2) else -result
            replay_buffer.extend(game_history_for_replay)
            print(f"  Game finished. Result: {result}, Moves: {move_count}. Replay buffer size: {len(replay_buffer)}")

        print(f"Epoch {epoch+1}: Self-play finished. Replay buffer size: {len(replay_buffer)}")

        #Training
        if not replay_buffer: continue

        total_value_loss = 0
        total_policy_loss = 0
        
        # Batch Sampling Implementation 
        batch_size = min(wandb.config.batch_size, len(replay_buffer))
        batch_indices = np.random.choice(len(replay_buffer), size=batch_size, replace=False)
        
        # Collect batch data
        batch_histories = [replay_buffer[i][0] for i in batch_indices]
        batch_colors = [replay_buffer[i][1] for i in batch_indices]
        batch_target_policies = np.array([replay_buffer[i][2] for i in batch_indices])
        batch_target_values = np.array([replay_buffer[i][3] for i in batch_indices]).reshape(-1, 1)

        # Convert to tensors
        board_tensors = Tensor.cat(*[history_to_tensor(hist, col) for hist, col in zip(batch_histories, batch_colors)], dim=0)
        target_policies = Tensor(batch_target_policies)
        target_values = Tensor(batch_target_values)

        # Perform a single batch forward and backward pass
        predicted_policies, predicted_values = model(board_tensors)

        value_loss = (predicted_values - target_values).square().mean()
        policy_loss = -(target_policies * predicted_policies.log_softmax()).sum() / batch_size
        
        loss = value_loss + policy_loss
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        avg_value_loss = value_loss.item()
        avg_policy_loss = policy_loss.item()

        wandb.log({
            "epoch": epoch,
            "value_loss": avg_value_loss,
            "policy_loss": avg_policy_loss,
            "total_loss": avg_value_loss + avg_policy_loss,
            "replay_buffer_size": len(replay_buffer)
        })
        print(f"Epoch {epoch+1}: Training finished. Avg Loss: {avg_value_loss + avg_policy_loss:.4f}")

    print("Training finished!")
    wandb.finish()


if __name__ == "__main__":
    # wlll need to log in to W&B first via the terminal: `wandb login`
    main()