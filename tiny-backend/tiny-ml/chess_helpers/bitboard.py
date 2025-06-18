from typing import Optional
import numpy as np

class Bitboard:
    """
    Python equivalent of C++ bitboard   with 64-bit integer bitboards
    Each bitboard represents piece positions on 64 squares (8x8 board)
    """
    
    def __init__(self):
        # White pieces bitboards
        self.white_pawns: int = 0
        self.white_knights: int = 0
        self.white_bishops: int = 0
        self.white_rooks: int = 0
        self.white_queens: int = 0
        self.white_king: int = 0
        
        # Black pieces bitboards
        self.black_pawns: int = 0
        self.black_knights: int = 0
        self.black_bishops: int = 0
        self.black_rooks: int = 0
        self.black_queens: int = 0
        self.black_king: int = 0
        
        # Additional game state
        self.white_to_move: bool = True
        self.castling_rights: int = 0b1111  # KQkq
        self.en_passant_square: Optional[int] = None
        self.halfmove_clock: int = 0
        self.fullmove_number: int = 1
        