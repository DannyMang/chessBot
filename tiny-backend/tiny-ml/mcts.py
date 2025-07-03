from dataclasses import dataclass, field
import math
import copy
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
from chess_helpers.cpp import chess_engine
from model import ChessNet
from chess_helpers.game_logic import is_game_over, get_game_result, board_to_tensor, move_to_policy_index, get_legal_moves

@dataclass
class MCTSNode:
    """
    Represents a node in the MCTS tree for AlphaZero.
    """
    board: Any  # This would be your board state
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
    for i, node in enumerate(path):
        node.visit_count += 1
        # Flip value for alternating players
        perspective_value = rollout_result * (1 if i % 2 == 0 else -1)
        node.value += perspective_value



def mcts_alphazero(model, start_state, num_simulations=100, exploration_constant=1.41):
    """
    AlphaZero MCTS implementation:
    - Expands ALL children at once when first visiting a leaf
    - Uses neural network policy to set prior probabilities
    - No traditional rollout - just neural network value
    """
    
    for simulation in range(num_simulations):
        current = start_state
        path = [current]
        
        # 1. Selection - traverse down to leaf using UCB
        while current.children and not is_game_over(current.board):
            current = max(current.children, key=lambda child: ucb(child, exploration_constant))
            path.append(current)
        
        # 2. Expansion + Evaluation
        value = None
        
        if is_game_over(current.board):
            # Terminal position
            value = get_game_result(current.board) or 0.0
        elif not current.children:
            # First time visiting this leaf - expand ALL children at once
            board_tensor = board_to_tensor(current.board)
            policy, value = model.predict(board_tensor)
            
            legal_moves = get_legal_moves(current.board)
            for move in legal_moves:
                new_board = copy.deepcopy(current.board)
                new_board.make_move(move)
                
                # Get prior probability from neural network policy
                move_idx = move_to_policy_index(move)
                prior = policy[0, move_idx].item() if move_idx < policy.shape[1] else 0.01
                
                child = MCTSNode(
                    board=new_board,
                    parent=current,
                    prior=prior
                )
                current.children.append(child)
            
            # Use neural network value (no rollout)
        else:
            # This shouldn't happen with proper selection, but handle it
            board_tensor = board_to_tensor(current.board)
            _, value = model.predict(board_tensor)
        
        # 3. Backpropagation
        for i, node in enumerate(path):
            node.visit_count += 1
            # Flip value for alternating players
            perspective_value = value * (1 if i % 2 == 0 else -1)
            node.value += perspective_value
    
    # Return best move based on visit counts (or UCB for exploration)
    if start_state.children:
        return max(start_state.children, key=lambda child: child.visit_count)
    return None


def ucb(node, exploration_constant):
    """
    Upper Confidence Bound calculation for node selection.
    AlphaZero uses a modified UCB formula that includes prior probabilities.
    """
    if node.visit_count == 0:
        return float('inf')
    
    # Q-value
    q_value = node.value / node.visit_count
    if hasattr(node, 'prior') and node.prior > 0:
        exploration = exploration_constant * node.prior * math.sqrt(node.parent.visit_count) / (1 + node.visit_count)
    else:
        exploration = exploration_constant * math.sqrt(math.log(node.parent.visit_count) / node.visit_count)
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
    