import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
from tinygrad.tensor import Tensor

# This will be your C++ engine. The .so file created from the build is a Python module.
from chess_helpers.cpp import chess_engine 

from model import ChessNet

def board_to_tensor(board: chess_engine.ChessBitboard) -> Tensor:
    """
    Convert the bitboard representation to a tensor for the model.
    The tiny-ml/README.md suggests a 12x8x8 tensor.
    """
    # The bitboards are exposed as public members in the python bindings
    bitboards = [
        board.white_pawns, board.white_knights, board.white_bishops, board.white_rooks, board.white_queens, board.white_king,
        board.black_pawns, board.black_knights, board.black_bishops, board.black_rooks, board.black_queens, board.black_king
    ]
    
    # Convert each 64-bit integer into an 8x8 numpy array
    np_bitboards = []
    for b in bitboards:
        # np.unpackbits expects uint8. We need to view the uint64 as 8 uint8s.
        byte_array = np.array([b], dtype=np.uint64).view(np.uint8)
        # Reverse the byte order to match the board representation (optional but good practice)
        # and then unpack into bits.
        unpacked = np.unpackbits(byte_array[::-1])
        np_bitboards.append(unpacked.reshape(8, 8))
    
    # Stack into a single (12, 8, 8) numpy array and then convert to a TinyGrad tensor
    board_state = np.stack(np_bitboards, axis=0).astype(np.float32)
    
    return Tensor(board_state, requires_grad=False).unsqueeze(0) # Add batch dimension

def train():
    """
    This is where the main self-play training loop will go.
    It will follow the MCTS + NN process described in the README.
    """
    board = chess_engine.ChessBitboard() # Create a new game
    board.set_starting_position()
    model = ChessNet()

    # --- Training Loop Placeholder ---
    # This is a simplified version. A full implementation would involve MCTS.
    for i in range(100): # Simulate a game of 100 moves
        # 1. Convert board state to a tensor
        board_tensor = board_to_tensor(board)
        
        # 2. Get model prediction
        policy, value = model(board_tensor)
        
        # 3. Choose a move (for now, let's just get legal moves and pick one)
        # In a real implementation, you'd use the policy to guide MCTS.
        legal_moves = board.generate_legal_moves()
        if not legal_moves:
            # Check for checkmate or stalemate
            current_player_color = chess_engine.Color.WHITE if board.white_to_move else chess_engine.Color.BLACK
            if board.is_in_check(current_player_color):
                print("Checkmate!")
            else:
                print("Stalemate!")
            break
        
        # This is a placeholder for move selection.
        # A real implementation would use the policy probabilities.
        best_move_obj = np.random.choice(legal_moves)
        
        # 4. Play the move on the board
        board.make_move(best_move_obj)
        
        # The move object doesn't have a nice __str__ yet, so we manually format it.
        # You could add a __str__ or __repr__ to the Move class in python_bindings.cpp
        from_sq = best_move_obj.get_from()
        to_sq = best_move_obj.get_to()
        
        # A simple way to convert square index to algebraic notation
        files = "abcdefgh"
        ranks = "12345678"
        move_str = f"{files[from_sq % 8]}{ranks[from_sq // 8]}{files[to_sq % 8]}{ranks[to_sq // 8]}"

        print(f"Move {i+1}: Played {move_str}.") # Board FEN not available directly, would need to implement get_fen

        # 5. Store the (board_state, policy, game_outcome) for training
        # ... (this is the experience replay buffer)

    print("Game finished!")
    # After the game, you would use the collected data to train the model
    # optimizer.zero_grad()
    # loss.backward()
    # optimizer.step()


if __name__ == "__main__":
    train() 