import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from tinygrad import Tensor
from tinygrad.nn.state import safe_load, get_state_dict

from model import ChessNet
from mcts import MCTSNode, mcts_alphazero
from chess_helpers.cpp import chess_engine
from chess_helpers.game_logic import get_board_planes, get_legal_moves

def load_state_dict(model, state_dict):
    """
    Loads a state dictionary into a tinygrad model.
    """
    model_state_dict = get_state_dict(model)
    for k, v in state_dict.items():
        if k in model_state_dict:
            model_state_dict[k].assign(v).realize()
        else:
            print(f"Warning: key {k} from checkpoint not found in model.")

def get_human_move(board):
    """
    Prompts the human player for a move and validates it.
    """
    legal_moves = get_legal_moves(board)
    
    # We need a way to get the UCI string for each move to validate user input
    # Assuming the C++ engine doesn't have a direct conversion, we'll do it manually
    def move_to_uci(move):
        from_sq = move.get_from()
        to_sq = move.get_to()
        from_str = f"{chr(ord('a') + from_sq % 8)}{from_sq // 8 + 1}"
        to_str = f"{chr(ord('a') + to_sq % 8)}{to_sq // 8 + 1}"
        
        promo = ""
        flags = move.get_flags()
        if flags == 8: promo = 'n'
        elif flags == 9: promo = 'b'
        elif flags == 10: promo = 'r'
        elif flags == 11: promo = 'q'
        return from_str + to_str + promo

    legal_moves_str = sorted([move_to_uci(m) for m in legal_moves])

    while True:
        print("\nLegal moves:", ", ".join(legal_moves_str))
        move_str = input("Enter your move (e.g., e2e4 or e7e8q for promotion): ").lower()
        if move_str in legal_moves_str:
            move_idx = legal_moves_str.index(move_str)
            return legal_moves[move_idx]
        else:
            print(f"'{move_str}' is not a valid move. Please try again.")

def main():
    """
    Main function to run the chess game against the AI.
    """
    # --- Model Loading ---
    model = ChessNet()
    try:
        print("Loading model from checkpoint...")
        state_dict = safe_load("models/chess_net_checkpoint.safetensors")
        load_state_dict(model, state_dict)
        print("Model weights loaded successfully.")
    except FileNotFoundError:
        print("\n---")
        print("Error: Model checkpoint 'models/chess_net_checkpoint.safetensors' not found.")
        print("Please train the model first by running train.py")
        print("---\n")
        return

    # --- Game Setup ---
    board = chess_engine.ChessBitboard()
    board.set_starting_position()
    board_plane_history = []
    
    human_color_str = ""
    while human_color_str not in ['w', 'b']:
        human_color_str = input("Do you want to play as White or Black? (w/b): ").lower()
    human_is_white = (human_color_str == 'w')
    
    # --- Game Loop ---
    Tensor.training = False # Set model to evaluation mode
    move_count = 0
    while not board.is_game_over():
        # TODO: This requires a print function in the C++ engine
        # For now, we can't visually see the board this way.
        # board.print() 
        print(f"\n--- Move {move_count + 1} ---")
        
        board_plane_history.append(get_board_planes(board))
        
        is_ai_turn = (board.white_to_move and not human_is_white) or \
                     (not board.white_to_move and human_is_white)

        if is_ai_turn:
            print("\nAI is thinking...")
            root_node = MCTSNode(board=board)
            
            num_simulations = getenv("SIMS", 800)
            
            best_child_node = mcts_alphazero(
                model,
                root_node,
                list(board_plane_history),
                num_simulations=num_simulations,
                dirichlet_epsilon=0.0
            )
            
            if best_child_node is None:
                print("AI cannot find a move. This could mean the game is a stalemate or checkmate.")
                break
                
            move = best_child_node.move
            
            # Manually construct move string for printing
            from_sq, to_sq, flags = move.get_from(), move.get_to(), move.get_flags()
            from_str = f"{chr(ord('a') + from_sq % 8)}{from_sq // 8 + 1}"
            to_str = f"{chr(ord('a') + to_sq % 8)}{to_sq // 8 + 1}"
            promo = ""
            if flags == 8: promo = 'n'
            elif flags == 9: promo = 'b'
            elif flags == 10: promo = 'r'
            elif flags == 11: promo = 'q'
            
            print(f"AI plays: {from_str}{to_str}{promo}")
            board.make_move(move)
        else:
            move = get_human_move(board)
            board.make_move(move)

        move_count += 1

    # --- Game Over ---
    print("\n----------\nGAME OVER\n----------")
    result = board.get_result()
    if result == 1:
        print("\nWhite wins.")
    elif result == -1:
        print("\nBlack wins.")
    else:
        print("\nIt's a draw.")

if __name__ == "__main__":
    from tinygrad.helpers import getenv
    main() 