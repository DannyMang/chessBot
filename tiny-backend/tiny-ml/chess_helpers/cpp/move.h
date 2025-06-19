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
    static constexpr uint8_t PROMOTION_FLAG = 3;

    Move() : from_square(0), to_square(0), piece_type(Piece::Type::NONE), capture_piece(0), flags(NO_FLAG) {}
    Move(Square from, Square to, Piece::Type pt) : from_square(from), to_square(to), piece_type(pt), capture_piece(0), flags(NO_FLAG) {}

    Square getFrom() const { return from_square; }
    Square getTo() const { return to_square; }
    Piece::Type getPieceType() const { return piece_type; }
};
