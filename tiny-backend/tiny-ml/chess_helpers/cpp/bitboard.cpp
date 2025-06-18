// bitboard.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <vector>
#include <cstdint>

namespace py = pybind11;

// Simple Move structure
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
};

class Bitboard {
    public:
        uint64_t white_pawns;
        uint64_t white_knights;
        uint64_t white_bishops;
        uint64_t white_rooks;
        uint64_t white_queens;
        uint64_t white_king;

        uint64_t black_pawns;
        uint64_t black_knights;
        uint64_t black_bishops;
        uint64_t black_rooks;
        uint64_t black_queens;
        uint64_t black_king;

        bool white_to_move;
        uint64_t castling_rights;
        uint64_t en_passant_square;
        int halfmove_clock;
        int fullmove_number;

        // construtor
        Bitboard() {
            white_pawns = 0;
            white_knights = 0;
            white_bishops = 0;
            white_rooks = 0;
            white_queens = 0;
            white_king = 0;
            black_pawns = 0;
            black_knights = 0;
            black_bishops = 0;
            black_rooks = 0;
            black_queens = 0;
            black_king = 0;
            white_to_move = true;
            //4 possible castling rights ( queen side, king side on both sides, so we use 4 bits)
            castling_rights = 0b1111; 
            en_passant_square = 0;
            //halfmove clock is the number of halfmoves since the last capture or pawn move
            halfmove_clock = 0;
            //fullmove number is the number of full moves since the beginning of the game
            fullmove_number = 1;
        }

        // get white pieces, use bitwise OR.
        uint64_t getWhitePieces() const {
           return white_pawns | white_knights | white_bishops | white_rooks | white_queens | white_king;
        }

        // get black pieces
        uint64_t getBlackPieces() const {
            return black_pawns | black_knights | black_bishops | black_rooks | black_queens | black_king;
        }

        uint64_t getAllPieces() const {
            return getWhitePieces() | getBlackPieces();
        }

        // set starting position
        // remember there are 64 squares, so we use 64 bits to represent the board
        // easy to represent with hexadecimal representation
        void setStartingPosition() {
            white_pawns = 0x000000000000FF00ULL;
            white_rooks = 0x0000000000000081ULL;
            white_knights = 0x0000000000000042ULL;
            white_bishops = 0x0000000000000024ULL;
            white_queens = 0x0000000000000008ULL;
            white_king = 0x0000000000000010ULL;
            
            // Black pieces
            black_pawns = 0x00FF000000000000ULL;
            black_rooks = 0x8100000000000000ULL;
            black_knights = 0x4200000000000000ULL;
            black_bishops = 0x2400000000000000ULL;
            black_queens = 0x0800000000000000ULL;
            black_king = 0x1000000000000000ULL;

            white_to_move = true;
            castling_rights = 0b1111;
            en_passant_square = -1;
            halfmove_clock = 0;
            fullmove_number = 1;
        }

};

// Python binding
PYBIND11_MODULE(chess_engine, m) {
    m.doc() = "Fast chess engine with bitboard representation";
    
    py::class_<Move>(m, "Move")
        .def(py::init<>())
        .def(py::init<int, int, int>())
        .def_readwrite("from_square", &Move::from_square)
        .def_readwrite("to_square", &Move::to_square)
        .def_readwrite("piece_type", &Move::piece_type)
        .def_readwrite("capture_piece", &Move::capture_piece)
        .def_readwrite("is_promotion", &Move::is_promotion)
        .def_readwrite("promotion_piece", &Move::promotion_piece);

    py::class_<Bitboard>(m, "Bitboard")
        .def(py::init<>())
        .def_readwrite("white_pawns", &Bitboard::white_pawns)
        .def_readwrite("white_knights", &Bitboard::white_knights)
        .def_readwrite("white_bishops", &Bitboard::white_bishops)
        .def_readwrite("white_rooks", &Bitboard::white_rooks)
        .def_readwrite("white_queens", &Bitboard::white_queens)
        .def_readwrite("white_king", &Bitboard::white_king)
        .def_readwrite("black_pawns", &Bitboard::black_pawns)
        .def_readwrite("black_knights", &Bitboard::black_knights)
        .def_readwrite("black_bishops", &Bitboard::black_bishops)
        .def_readwrite("black_rooks", &Bitboard::black_rooks)
        .def_readwrite("black_queens", &Bitboard::black_queens)
        .def_readwrite("black_king", &Bitboard::black_king)
        .def_readwrite("white_to_move", &Bitboard::white_to_move)
        .def_readwrite("castling_rights", &Bitboard::castling_rights)
        .def_readwrite("en_passant_square", &Bitboard::en_passant_square)
        .def_readwrite("halfmove_clock", &Bitboard::halfmove_clock)
        .def_readwrite("fullmove_number", &Bitboard::fullmove_number)
        .def("get_white_pieces", &Bitboard::getWhitePieces)
        .def("get_black_pieces", &Bitboard::getBlackPieces)
        .def("get_all_pieces", &Bitboard::getAllPieces)
        .def("set_starting_position", &Bitboard::setStartingPosition)
        .def("generate_legal_moves", &Bitboard::generateLegalMoves)
        .def("make_move", &Bitboard::makeMove)
        .def("is_legal", &Bitboard::isLegal)
        .def("get_piece_at", &Bitboard::getPieceAt);
}