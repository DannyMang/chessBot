#include "bitboard.cpp"
#include "piece.cpp"

class Position {
    private:
        Bitboard piece_bb[6];
        Bitboard color_bb[2];
        Piece board[64]; // mailbox , double check if this is actually efficient later
        Color side_to_move;

    public:
        Piece get_piece(int square) const {
            return board[square];
        }
        Color get_side_to_move() const {
            return side_to_move;
        }
        



}