from chess_helpers.cpp import chess_engine
from tinygrad.tensor import Tensor
import numpy as np

def is_game_over(board):
    """Check if game is over (delegates to C++ method)"""
    return board.is_game_over()

def get_game_result(board):
    """Get result from current player's perspective"""
    result = board.get_result()
    return None if result == 999 else result  # 999 means game continues

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

def move_to_policy_index(move):
    """Convert chess move to policy vector index following AlphaZero encoding"""
    from_square = move.get_from()
    to_square = move.get_to()
    
    from_row, from_col = from_square // 8, from_square % 8
    to_row, to_col = to_square // 8, to_square % 8
    
    # Calculate direction and distance
    row_diff = to_row - from_row
    col_diff = to_col - from_col
    
    # Queen moves (56 planes: 7 distances × 8 directions)
    if abs(row_diff) == abs(col_diff) or row_diff == 0 or col_diff == 0:
        # Calculate direction (0-7 for N, NE, E, SE, S, SW, W, NW)
        if row_diff > 0 and col_diff == 0: direction = 0  # North
        elif row_diff > 0 and col_diff > 0: direction = 1  # NorthEast
        elif row_diff == 0 and col_diff > 0: direction = 2  # East
        elif row_diff < 0 and col_diff > 0: direction = 3  # SouthEast
        elif row_diff < 0 and col_diff == 0: direction = 4  # South
        elif row_diff < 0 and col_diff < 0: direction = 5  # SouthWest
        elif row_diff == 0 and col_diff < 0: direction = 6  # West
        else: direction = 7  # NorthWest
        
        distance = max(abs(row_diff), abs(col_diff)) - 1  # 0-6
        plane_index = direction * 7 + distance
        return from_square * 73 + plane_index
    
    # Knight moves (8 planes)
    knight_moves = [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]
    if (row_diff, col_diff) in knight_moves:
        knight_index = knight_moves.index((row_diff, col_diff))
        return from_square * 73 + 56 + knight_index
    
    # Underpromotions (9 planes) - only for pawn moves to 1st/8th rank
    if move.get_piece_type() == chess_engine.PieceType.PAWN:
        if to_row == 0 or to_row == 7:  # Promotion
            if move.get_flags() >= 12:  # Underpromotion flags
                # Map promotion type to index (0-8)
                return from_square * 73 + 64 + (move.get_flags() - 12)
    
    return 0  # Default fallback