from dataclasses import dataclass, field
from typing import Any


@dataclass
class State:
    """
    Represents a state in the MCTS tree.
    """
    board: Any  # This would be your board state
    visit_count: int = 0
    value: float = 0.0
    parent: 'State' = None
    children: list = field(default_factory=list)

    def is_leaf_node(self):
        """
        Check if this state is a leaf node (i.e., has no children explored yet).
        """
        return not self.children


def mcts(model, board, start_state, num_simulations=100):
    """
    Run Monte Carlo Tree Search to find the best move.
    """
    
    current = start_state
    
    if (current.is_leaf_node()):
        pass
        
    
    
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