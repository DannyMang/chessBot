// types.h
#pragma once
#include <cstdint>

using U64 = uint64_t;
using Square = int;
using Bitboard = uint64_t;

enum PieceType : int {
    PAWN = 0, KNIGHT = 1, BISHOP = 2, ROOK = 3, QUEEN = 4, KING = 5
};

enum Color : int {
    WHITE = 0, BLACK = 1
};