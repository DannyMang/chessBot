#pragma once
#include "types.h"

extern "C" {
    #include "magicmoves.h"
}

class MagicMoves {
public:
    static void init() {
        initmagicmoves();
    }
    
    static Bitboard getRookAttacks(Square square, Bitboard occupancy) {
        return Rmagic(square, occupancy);
    }
    
    static Bitboard getBishopAttacks(Square square, Bitboard occupancy) {
        return Bmagic(square, occupancy);
    }
    
    static Bitboard getQueenAttacks(Square square, Bitboard occupancy) {
        return Qmagic(square, occupancy);
    }
};