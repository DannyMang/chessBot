// python_bindings.cpp
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include "bitboard.h"

namespace py = pybind11;

PYBIND11_MODULE(chess_engine, m) {
    m.doc() = "Fast chess engine with magic bitboards";

    py::enum_<Piece::Type>(m, "PieceType")
        .value("NONE", Piece::Type::NONE)
        .value("PAWN", Piece::Type::PAWN)
        .value("KNIGHT", Piece::Type::KNIGHT)
        .value("BISHOP", Piece::Type::BISHOP)
        .value("ROOK", Piece::Type::ROOK)
        .value("QUEEN", Piece::Type::QUEEN)
        .value("KING", Piece::Type::KING)
        .export_values();

    py::enum_<Piece::Color>(m, "Color")
        .value("WHITE", Piece::Color::WHITE)
        .value("BLACK", Piece::Color::BLACK)
        .export_values();

    py::class_<Piece>(m, "Piece")
        .def(py::init<>())
        .def(py::init<Piece::Color, Piece::Type>())
        .def("type", &Piece::type)
        .def("color", &Piece::color)
        .def("is_empty", &Piece::is_empty)
        .def(py::self == py::self);

    py::class_<Move>(m, "Move")
        .def(py::init<>())
        .def(py::init<Square, Square, Piece::Type, uint8_t>(), py::arg("from"), py::arg("to"), py::arg("piece_type"), py::arg("flags") = 0)
        .def("get_from", &Move::getFrom)
        .def("get_to", &Move::getTo)
        .def("get_piece_type", &Move::getPieceType)
        .def("get_flags", &Move::getFlags);
    
    // Auto-convert camelCase to snake_case
    py::class_<ChessBitboard>(m, "ChessBitboard", py::dynamic_attr())
        .def(py::init<>())
        .def("set_starting_position", &ChessBitboard::setStartingPosition)
        .def("load_fen", &ChessBitboard::loadFen, "Load a position from a FEN string")
        .def("get_piece_at", &ChessBitboard::getPieceAt)
        .def("generate_legal_moves", &ChessBitboard::generateLegalMoves)
        .def("make_move", &ChessBitboard::makeMove)
        .def("get_white_pieces", &ChessBitboard::getWhitePieces)
        .def("get_black_pieces", &ChessBitboard::getBlackPieces)
        .def("get_all_pieces", &ChessBitboard::getAllPieces)
        .def("set_piece", &ChessBitboard::setPiece)
        .def("clear_square", &ChessBitboard::clearSquare)
        .def("is_in_check", &ChessBitboard::isInCheck)
        .def("perft", &ChessBitboard::perft)
        .def("perft_divide", &ChessBitboard::perft_divide)
        // Expose public members
        .def_readwrite("white_to_move", &ChessBitboard::white_to_move)
        .def_readwrite("fullmove_number", &ChessBitboard::fullmove_number)
        .def_readonly("en_passant_square", &ChessBitboard::en_passant_square)
        .def_readonly("white_pawns", &ChessBitboard::white_pawns)
        .def_readonly("white_knights", &ChessBitboard::white_knights)
        .def_readonly("white_bishops", &ChessBitboard::white_bishops)
        .def_readonly("white_rooks", &ChessBitboard::white_rooks)
        .def_readonly("white_queens", &ChessBitboard::white_queens)
        .def_readonly("white_king", &ChessBitboard::white_king)
        .def_readonly("black_pawns", &ChessBitboard::black_pawns)
        .def_readonly("black_knights", &ChessBitboard::black_knights)
        .def_readonly("black_bishops", &ChessBitboard::black_bishops)
        .def_readonly("black_rooks", &ChessBitboard::black_rooks)
        .def_readonly("black_queens", &ChessBitboard::black_queens)
        .def_readonly("black_king", &ChessBitboard::black_king);
}