#pragma once
#include "types.h"
#include "piece.h"
#include "move.h"
#include "magicmoves_wrapper.h"
#include <vector>

class ChessBitboard {
public:
    // Piece bitboards
    Bitboard white_pawns;
    Bitboard white_knights;
    Bitboard white_bishops;
    Bitboard white_rooks;
    Bitboard white_queens;
    Bitboard white_king;
    
    Bitboard black_pawns;
    Bitboard black_knights;
    Bitboard black_bishops;
    Bitboard black_rooks;
    Bitboard black_queens;
    Bitboard black_king;
    
    // Game state
    bool white_to_move;
    int castling_rights;
    int en_passant_square;
    int halfmove_clock;
    int fullmove_number;
    
    // Mailbox for fast piece lookup
    Piece mailbox[64];
    
    ChessBitboard();
    
    // Basic operations
    Bitboard getWhitePieces() const;
    Bitboard getBlackPieces() const;
    Bitboard getAllPieces() const;
    void setStartingPosition();
    
    // Piece operations
    Piece getPieceAt(Square square) const;
    void setPiece(Square square, Piece piece);
    void clearSquare(Square square);
    
    // Move generation
    std::vector<Move> generateLegalMoves() const;
    std::vector<Move> generatePseudoLegalMoves() const;
    
    // Move execution
    void makeMove(const Move& move);
    bool isLegal(const Move& move) const;
    
    // Attack generation using magic bitboards
    Bitboard getAttacks(Square square, PieceType piece_type, Bitboard occupancy) const;
    
private:
    void updateMailbox();
    void removePieceFromBitboard(Square square, Piece piece);
    void addPieceToBitboard(Square square, Piece piece);
};
