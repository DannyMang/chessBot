// python_bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "bitboard.h"

namespace py = pybind11;

PYBIND11_MODULE(chess_engine, m) {
    m.doc() = "Fast chess engine with magic bitboards";
    
    py::class_<Move>(m, "Move")
        .def(py::init<>())
        .def(py::init<int, int, int>())
        .def_readwrite("from_square", &Move::from_square)
        .def_readwrite("to_square", &Move::to_square)
        .def_readwrite("piece_type", &Move::piece_type);

    py::class_<ChessBitboard>(m, "ChessBitboard")
        .def(py::init<>())
        .def("set_starting_position", &ChessBitboard::setStartingPosition)
        .def("get_piece_at", &ChessBitboard::getPieceAt)
        .def("generate_legal_moves", &ChessBitboard::generateLegalMoves)
        .def("make_move", &ChessBitboard::makeMove)
        .def("get_white_pieces", &ChessBitboard::getWhitePieces)
        .def("get_black_pieces", &ChessBitboard::getBlackPieces);
}