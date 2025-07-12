from dataclasses import dataclass, field
import math
import copy
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from chess_helpers.cpp import chess_engine
from model import ChessNet
from chess_helpers.game_logic import is_game_over, get_game_result, board_to_tensor, move_to_policy_index, get_legal_moves, get_board_planes, history_to_tensor

@dataclass
class MCTSNode:
    """
    Represents a node in the MCTS tree for AlphaZero.
    """
    board: Any  # This would be your board state
    move: Any = None # The move that led to this state
    visit_count: int = 0
    value: float = 0.0
    parent: 'MCTSNode' = None
    children: list = field(default_factory=list)
    prior: float = 0.0

    def is_leaf_node(self):
        """
        Check if this state is a leaf node (i.e., has no children explored yet).
        """
        return len(self.children) == 0


def mcts_traditional(model, start_state, num_simulations=100, exploration_constant=1.41):
    """
    Traditional MCTS implementation
    - If leaf + first visit: evaluate current node
    - If leaf + not first visit: expand with one child, evaluate child  
    - If not leaf: select best child using UCB
    """
    
    current = start_state
    path = [current]
    
    # 1. Selection - traverse down using UCB until leaf
    while not current.is_leaf_node():
        current = max(current.children, key=lambda child: ucb(child, exploration_constant))
        path.append(current)
    
    # 2. Expansion + Evaluation
    if current.visit_count == 0:
        # First visit - just rollout/evaluate this node
        board_tensor = board_to_tensor(current.board)
        _, value = model.predict(board_tensor)
        rollout_result = value
    else:
        # Not first visit - expand by adding ONE child, then evaluate it
        legal_moves = get_legal_moves(current.board)
        if legal_moves and not is_game_over(current.board):
            # Pick one move (could be random or using policy)
            move = legal_moves[0]  # or use policy to select
            new_board = copy.deepcopy(current.board)
            new_board.make_move(move)
            
            child = MCTSNode(board=new_board, parent=current)
            current.children.append(child)
            path.append(child)
            
            # Evaluate the new child
            board_tensor = board_to_tensor(child.board)
            _, value = model.predict(board_tensor)
            rollout_result = value
        else:
            # Terminal node
            rollout_result = get_game_result(current.board) or 0.0
    
    # 4. Backpropagation
    v = rollout_result
    for node in reversed(path):
        node.visit_count += 1
        # Value is from the perspective of the player to move at the node.
        # We negate it at each step to reflect the alternating players.
        node.value += v
        v = -v



def mcts_alphazero(model, start_state, initial_board_planes, num_simulations=100, exploration_constant=1.41, dirichlet_alpha=0.3, dirichlet_epsilon=0.25):
    """
    AlphaZero MCTS implementation:
    - Expands ALL children at once when first visiting a leaf
    - Uses neural network policy to set prior probabilities
    - No traditional rollout - just neural network value
    """
    
    # Main MCTS loop
    for _ in range(num_simulations):
        current = start_state
        path = [current]
        
        # 1. Selection - traverse down to leaf using PUCT
        while current.children and not is_game_over(current.board):
            current = max(current.children, key=lambda child: puct(child, exploration_constant))
            path.append(current)
        
        # 2. Expansion + Evaluation
        value = None
        
        if is_game_over(current.board):
            # Terminal position
            value = get_game_result(current.board) or 0.0
        elif not current.children:
            if current == start_state:
                leaf_history = initial_board_planes
            else:
                current_planes = get_board_planes(current.board)
                parent_planes = get_board_planes(current.parent.board)
                leaf_history = [current_planes, parent_planes]

            leaf_tensor = history_to_tensor(leaf_history, current.board.white_to_move)
            policy, value = model.predict(leaf_tensor)

            legal_moves = get_legal_moves(current.board)
            
            # Add Dirichlet Noise for exploration at the root
            if current.parent is None:
                noise = np.random.dirichlet([dirichlet_alpha] * len(legal_moves))
            
            for i, move in enumerate(legal_moves):
                new_board = copy.deepcopy(current.board)
                new_board.make_move(move)
                
                # Get prior probability from neural network policy
                move_idx = move_to_policy_index(move)
                prior = policy[0, move_idx].item() if move_idx < policy.shape[1] else 0.01

                # Apply noise at the root
                if current.parent is None:
                    prior = (1 - dirichlet_epsilon) * prior + dirichlet_epsilon * noise[i]
                
                child = MCTSNode(
                    board=new_board,
                    move=move,
                    parent=current,
                    prior=prior
                )
                current.children.append(child)
            # (no rollout)
            
        # 3. Backpropagation
        # The NN value is from the perspective of the current node's player.
        v = value
        for node in reversed(path):
            node.visit_count += 1
            # Value is from the perspective of the player to move at the node.
            # We negate it at each step to reflect the alternating players.
            node.value += v
            v = -v
    
    # Return best move based on visit counts (or UCB for exploration)
    if start_state.children:
        return max(start_state.children, key=lambda child: child.visit_count)
    return None


def ucb(node, exploration_constant):
    """
    Standard Upper Confidence Bound (UCT) calculation for node selection.
    """
    if node.visit_count == 0:
        return float('inf')
    
    # Q-value from the parent's perspective.
    # A high value for the child is a low value for the parent.
    q_value = -node.value / node.visit_count
    exploration = exploration_constant * math.sqrt(math.log(node.parent.visit_count) / node.visit_count)
    return q_value + exploration


def puct(node, exploration_constant):
    """
    Polynomial Upper Confidence for Trees (PUCT) calculation for AlphaZero.
    This formula incorporates the prior probability from the neural network.
    """
    if node.visit_count == 0:
        return float('inf')
    
    # Q-value from the parent's perspective.
    # A high value for the child is a low value for the parent.
    q_value = -node.value / node.visit_count
    exploration = exploration_constant * node.prior * math.sqrt(node.parent.visit_count) / (1 + node.visit_count)
    return q_value + exploration


def get_best_move_policy(root_node):
    """
    Convert MCTS visit counts to a policy distribution for training.
    This is used in AlphaZero self-play to generate training data.
    """
    if not root_node.children:
        return None
    
    visit_counts = np.array([child.visit_count for child in root_node.children])
    
    # Temperature parameter for exploration (use 1.0 during training, 0.0 for best play)
    temperature = 1.0
    if temperature == 0:
        # Greedy selection
        policy = np.zeros_like(visit_counts)
        policy[np.argmax(visit_counts)] = 1.0
    else:
        # Boltzmann distribution
        visit_counts = visit_counts ** (1 / temperature)
        policy = visit_counts / np.sum(visit_counts)
    
    return policy


# Convenience function - you can switch between implementations
def mcts(model, start_state, num_simulations=100, exploration_constant=1.41, algorithm="a"):
    """
    Main MCTS function that delegates to either traditional or AlphaZero implementation.
    
    Args:
        algorithm: "traditional" or "alphazero"
    """
    if algorithm == "t":
        return mcts_traditional(model, start_state, num_simulations, exploration_constant)
    elif algorithm == "a":
        return mcts_alphazero(model, start_state, num_simulations, exploration_constant)
    else:
        raise ValueError("Algorithm must be flagged 't' or 'a'")


def rollout(model, board):
    """
    Traditional rollout - play random moves until game end.
    Not used in AlphaZero (neural network evaluation instead).
    """
    while not is_game_over(board):
        legal_moves = get_legal_moves(board)
        if not legal_moves:
            break
        move = np.random.choice(legal_moves)
        board.make_move(move)
    
    return get_game_result(board) or 0.0
    