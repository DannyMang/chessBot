#!/usr/bin/env python3
"""
Chess Bitboard Representation for TinyGrad Chess Engine
Equivalent to C++ CBoard class with additional Python utilities
"""

import chess
from typing import Optional, List, Tuple
import numpy as np

class CBoard:
    """
    Python equivalent of C++ CBoard with 64-bit integer bitboards
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

    @classmethod
    def from_fen(cls, fen: str) -> 'CBoard':
        """Create CBoard from FEN string using python-chess for parsing"""
        board = cls()
        chess_board = chess.Board(fen)
        
        # Convert python-chess board to our bitboard representation
        for square in chess.SQUARES:
            piece = chess_board.piece_at(square)
            if piece is None:
                continue
                
            bitboard_pos = 1 << square
            
            if piece.color == chess.WHITE:
                if piece.piece_type == chess.PAWN:
                    board.white_pawns |= bitboard_pos
                elif piece.piece_type == chess.KNIGHT:
                    board.white_knights |= bitboard_pos
                elif piece.piece_type == chess.BISHOP:
                    board.white_bishops |= bitboard_pos
                elif piece.piece_type == chess.ROOK:
                    board.white_rooks |= bitboard_pos
                elif piece.piece_type == chess.QUEEN:
                    board.white_queens |= bitboard_pos
                elif piece.piece_type == chess.KING:
                    board.white_king |= bitboard_pos
            else:  # BLACK
                if piece.piece_type == chess.PAWN:
                    board.black_pawns |= bitboard_pos
                elif piece.piece_type == chess.KNIGHT:
                    board.black_knights |= bitboard_pos
                elif piece.piece_type == chess.BISHOP:
                    board.black_bishops |= bitboard_pos
                elif piece.piece_type == chess.ROOK:
                    board.black_rooks |= bitboard_pos
                elif piece.piece_type == chess.QUEEN:
                    board.black_queens |= bitboard_pos
                elif piece.piece_type == chess.KING:
                    board.black_king |= bitboard_pos
        
        # Set game state
        board.white_to_move = chess_board.turn == chess.WHITE
        board.castling_rights = 0
        if chess_board.has_kingside_castling_rights(chess.WHITE):
            board.castling_rights |= 0b1000
        if chess_board.has_queenside_castling_rights(chess.WHITE):
            board.castling_rights |= 0b0100
        if chess_board.has_kingside_castling_rights(chess.BLACK):
            board.castling_rights |= 0b0010
        if chess_board.has_queenside_castling_rights(chess.BLACK):
            board.castling_rights |= 0b0001
            
        board.en_passant_square = chess_board.ep_square
        board.halfmove_clock = chess_board.halfmove_clock
        board.fullmove_number = chess_board.fullmove_number
        
        return board

    def to_tensor_planes(self) -> np.ndarray:
        """
        Convert bitboards to 8x8x12 tensor planes for neural network input
        Standard representation used by AlphaZero and Leela Chess Zero
        
        Returns:
            np.ndarray: Shape (12, 8, 8) - 12 piece type planes
        """
        planes = np.zeros((12, 8, 8), dtype=np.float32)
        
        # Helper function to convert bitboard to 8x8 plane
        def bitboard_to_plane(bitboard: int) -> np.ndarray:
            plane = np.zeros((8, 8), dtype=np.float32)
            for square in range(64):
                if bitboard & (1 << square):
                    row = square // 8
                    col = square % 8
                    plane[row][col] = 1.0
            return plane
        
        # Convert each piece type to a plane
        piece_bitboards = [
            self.white_pawns, self.white_knights, self.white_bishops,
            self.white_rooks, self.white_queens, self.white_king,
            self.black_pawns, self.black_knights, self.black_bishops,
            self.black_rooks, self.black_queens, self.black_king
        ]
        
        for i, bitboard in enumerate(piece_bitboards):
            planes[i] = bitboard_to_plane(bitboard)
        
        return planes

    def to_tinygrad_input(self) -> 'Tensor':
        """
        Convert to TinyGrad tensor format for neural network
        
        Returns:
            Tensor: Shape (1, 12, 8, 8) - batch size 1, 12 channels, 8x8 board
        """
        # Import here to avoid circular dependencies
        import sys
        TINYGRAD_PATH = "/Users/danielung/Desktop/projects/tinygrad"
        sys.path.insert(0, TINYGRAD_PATH)
        
        from tinygrad import Tensor
        
        planes = self.to_tensor_planes()
        # Add batch dimension and convert to TinyGrad tensor
        tensor_input = Tensor(planes.reshape(1, 12, 8, 8))
        return tensor_input

    def get_all_white_pieces(self) -> int:
        """Get bitboard of all white pieces"""
        return (self.white_pawns | self.white_knights | self.white_bishops |
                self.white_rooks | self.white_queens | self.white_king)
    
    def get_all_black_pieces(self) -> int:
        """Get bitboard of all black pieces"""
        return (self.black_pawns | self.black_knights | self.black_bishops |
                self.black_rooks | self.black_queens | self.black_king)
    
    def get_all_pieces(self) -> int:
        """Get bitboard of all pieces"""
        return self.get_all_white_pieces() | self.get_all_black_pieces()

    def print_board(self):
        """Pretty print the board state (for debugging)"""
        print("\n  a b c d e f g h")
        for rank in range(7, -1, -1):  # 8 down to 1
            print(f"{rank + 1} ", end="")
            for file in range(8):  # a to h
                square = rank * 8 + file
                bit = 1 << square
                
                piece_char = '.'
                if self.white_pawns & bit:
                    piece_char = 'P'
                elif self.white_knights & bit:
                    piece_char = 'N'
                elif self.white_bishops & bit:
                    piece_char = 'B'
                elif self.white_rooks & bit:
                    piece_char = 'R'
                elif self.white_queens & bit:
                    piece_char = 'Q'
                elif self.white_king & bit:
                    piece_char = 'K'
                elif self.black_pawns & bit:
                    piece_char = 'p'
                elif self.black_knights & bit:
                    piece_char = 'n'
                elif self.black_bishops & bit:
                    piece_char = 'b'
                elif self.black_rooks & bit:
                    piece_char = 'r'
                elif self.black_queens & bit:
                    piece_char = 'q'
                elif self.black_king & bit:
                    piece_char = 'k'
                
                print(f"{piece_char} ", end="")
            print(f" {rank + 1}")
        print("  a b c d e f g h\n")

    def __str__(self) -> str:
        """String representation showing piece counts"""
        white_count = bin(self.get_all_white_pieces()).count('1')
        black_count = bin(self.get_all_black_pieces()).count('1')
        return f"CBoard: {white_count} white pieces, {black_count} black pieces, {'White' if self.white_to_move else 'Black'} to move"

# Example usage and testing
if __name__ == "__main__":
    # Test with starting position
    start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board = CBoard.from_fen(start_fen)
    
    print("Chess bitboard representation:")
    print(board)
    board.print_board()
    
    # Test tensor conversion
    tensor_planes = board.to_tensor_planes()
    print(f"Tensor planes shape: {tensor_planes.shape}")
    print(f"White pawns plane:\n{tensor_planes[0]}")
    
    # Test TinyGrad conversion (if available)
    try:
        tinygrad_input = board.to_tinygrad_input()
        print(f"TinyGrad input shape: {tinygrad_input.shape}")
    except ImportError:
        print("TinyGrad not available for testing") 