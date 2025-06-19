#include "position.cpp"
#include "bitboard.cpp"
#include "piece.cpp"
#include <cstdint>
#include <vector>
#include <iostream>

// PerftBenchmark is a class that contains the perft function
class PerftBenchmark {
public:
    uint64_t perft(const Position& pos, int depth) {
        if (depth == 0) return 1;
        
        uint64_t nodes = 0;
        auto moves = generate_all_moves(pos);
        
        for (auto move : moves) {
            Position new_pos = pos;
            new_pos.make_move(move);
            nodes += perft(new_pos, depth - 1);
        }
        
        return nodes;
    }
};