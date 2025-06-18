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

        // Fast C++ move generation
    std::vector<Move> generateLegalMoves();
    void makeMove(const Move& move);
    bool isLegal(const Move& move);
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