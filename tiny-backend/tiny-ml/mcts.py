from dataclasses import dataclass, field
import math
from typing import Any


@dataclass
class State:
    """
    Represents a state in the MCTS tree.
    """
    board: Any  # This would be your board state
    visit_count: int = 0
    value: float = 0.0
    reward: float = 0.0
    parent: 'State' = None
    children: list = field(default_factory=list)

    def is_leaf_node(self):
        """
        Check if this state is a leaf node (i.e., has no children explored yet).
        """
        return not self.children


def mcts(model, board, start_state, exploration_constant=1.41):
    current = start_state
    
    # 1. Selection 
    while not current.is_leaf_node():
        # Find child with highest UCB value
        best_child = max(current.children, key=lambda child: ucb(child, exploration_constant))
        current = best_child
    
    # 2. Expansion 
    if current.is_leaf_node() and not is_game_over(current.board):
        for move in get_legal_moves(current.board):
            new_board = copy.deepcopy(current.board)
            new_board.make_move(move)
            child = State(board=new_board, parent=current)
            current.children.append(child)
        
        if current.children:
            current = current.children[0] 
    
    # 3. Rollout 
    rollout_result = rollout(model, copy.deepcopy(current.board))
    
    # 4. Backpropagation
    while current is not None:
        current.visit_count += 1
        current.value += rollout_result
        current = current.parent
    
        
    
    
def rollout(model, board):
    """
    Rollout the board to the end of the game.
    
    param : current board state
    
    loop forever
        if state is terminal
            return state
        else
            action = select a random move within the subset of legal moves
            simulate (action, state)

    """
    while not board.is_game_over():
        move = model.get_move(board)
        board.make_move(move)

def is_game_over(state):
    """
    Check if the game state is terminal
    """
    return False


def ucb(state, exploration_constant):
    return state.reward + exploration_constant * math.sqrt(math.log(state.parent.visit_count) / state.visit_count)