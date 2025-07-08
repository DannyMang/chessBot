#pragma once
#include "types.h"
#include "piece.h"
#include "move.h"
#include "magicmoves_wrapper.h"
#include <vector>
#include <string>
#include <map>

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
    
    // Pre-computed attack tables
    Bitboard knight_attacks[64];
    Bitboard king_attacks[64];
    
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
    bool isGameOver() const;
    bool hasInsufficientMaterial() const;
    int getResult() const; // 1 if white wins, -1 if black wins, 0 if draw

    // Attack generation using magic bitboards
    Bitboard getAttacks(Square square, Piece::Type piece_type, Bitboard occupancy) const;
    
    // Check detection
    bool isInCheck(Piece::Color color) const;

    // Performance testing
    uint64_t perft(int depth) const;
    std::map<std::string, uint64_t> perft_divide(int depth);

    // FEN parsing
    void loadFen(const std::string& fen);

    void updateMailbox();

private:
    void initAttacks();
    void removePieceFromBitboard(Square square, Piece piece);
    void addPieceToBitboard(Square square, Piece piece);

    // Helper methods for move generation
    void generatePawnMoves(std::vector<Move>& moves) const;
    void generateKnightMoves(std::vector<Move>& moves) const;
    void generateKingMoves(std::vector<Move>& moves) const;
    
    // Check detection
    bool isSquareAttacked(Square square, Piece::Color by_color) const;
};
