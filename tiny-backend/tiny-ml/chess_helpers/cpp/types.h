// types.h
#pragma once
#include <cstdint>

using U64 = uint64_t;
using Square = int;
using Bitboard = uint64_t;

enum CastlingRights {
    NO_CASTLING = 0,
    WHITE_KINGSIDE = 1,
    WHITE_QUEENSIDE = 2,
    BLACK_KINGSIDE = 4,
    BLACK_QUEENSIDE = 8
};