// Simple Move structure
#pragma once
#include "types.h"
#include "piece.h"

class Move {
private:
    Square from_square;
    Square to_square;
    Piece::Type piece_type;
    uint8_t capture_piece; // Store the captured piece type
    uint8_t flags;

public:
    // Flags for special moves
    static constexpr uint8_t NO_FLAG = 0;
    static constexpr uint8_t EN_PASSANT_FLAG = 1;
    static constexpr uint8_t CASTLE_FLAG = 2;
    // Add flags for each type of promotion
    static constexpr uint8_t PROMOTION_KNIGHT_FLAG = 8;
    static constexpr uint8_t PROMOTION_BISHOP_FLAG = 9;
    static constexpr uint8_t PROMOTION_ROOK_FLAG = 10;
    static constexpr uint8_t PROMOTION_QUEEN_FLAG = 11;

    Move() : from_square(0), to_square(0), piece_type(Piece::Type::NONE), capture_piece(0), flags(NO_FLAG) {}
    Move(Square from, Square to, Piece::Type pt, uint8_t flag = NO_FLAG) : from_square(from), to_square(to), piece_type(pt), capture_piece(0), flags(flag) {}

    Square getFrom() const { return from_square; }
    Square getTo() const { return to_square; }
    Piece::Type getPieceType() const { return piece_type; }
    uint8_t getFlags() const { return flags; }
};
