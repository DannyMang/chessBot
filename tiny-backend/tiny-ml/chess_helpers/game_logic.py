from chess_helpers.cpp import chess_engine
from tinygrad.tensor import Tensor
import numpy as np

def is_game_over(board):
    """Check if game is over"""
    legal_moves = board.generate_legal_moves()
    
    # No legal moves = checkmate or stalemate
    if len(legal_moves) == 0:
        return True
    
    # 50-move rule
    if board.halfmove_clock >= 100:
        return True
    
    if board.has_insufficient_material(): # NOT DONE 
        return True
    
    # TODO: Add other draw conditions
    return False

def get_game_result(board):
    """Get result from current player's perspective: 1=win, -1=loss, 0=draw"""
    legal_moves = board.generate_legal_moves()
    
    if len(legal_moves) == 0:
        current_color = chess_engine.Color.WHITE if board.white_to_move else chess_engine.Color.BLACK
        if board.is_in_check(current_color):
            return -1  # Current player is checkmated = loss
        else:
            return 0   # Stalemate = draw
    
    if board.halfmove_clock >= 100:
        return 0  # 50-move rule = draw
    
    if board.has_insufficient_material(): # NOT DONE 
        return 0
    
    return None  # Game continues

def board_to_tensor(board):
    """Convert chess board to 12x8x8 tensor for neural network"""
    tensor = np.zeros((12, 8, 8), dtype=np.float32)
    
    # Map each bitboard to tensor channels
    piece_bitboards = [
        board.white_pawns, board.white_knights, board.white_bishops,
        board.white_rooks, board.white_queens, board.white_king,
        board.black_pawns, board.black_knights, board.black_bishops,
        board.black_rooks, board.black_queens, board.black_king
    ]
    
    for channel, bitboard in enumerate(piece_bitboards):
        for square in range(64):
            if bitboard & (1 << square):
                row, col = square // 8, square % 8
                tensor[channel][row][col] = 1.0
    
    return Tensor(tensor.reshape(1, 12, 8, 8))  # Add batch dimension

def get_legal_moves(board):
    """Get legal moves from board"""
    return board.generate_legal_moves()

def has_insufficient_material(board): # TO-DO
    return True

def move_to_policy_index(move):
    """Convert chess move to policy vector index (placeholder)"""
    # TODO: Implement proper move encoding based on AlphaZero's action space
    return 0