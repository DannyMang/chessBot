// Simple Move structure
#pragma once
#include "types.h"

struct Move {
    int from_square;
    int to_square;
    int piece_type;
    int capture_piece;
    bool is_promotion;
    int promotion_piece;
    
    Move() : from_square(0), to_square(0), piece_type(0), capture_piece(0), 
             is_promotion(false), promotion_piece(0) {}
    
    Move(int from, int to, int piece = 0) 
        : from_square(from), to_square(to), piece_type(piece), capture_piece(0),
          is_promotion(false), promotion_piece(0) {}

    Square from() const { return from_square; }
    Square to() const { return to_square; }

};
