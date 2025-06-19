#include "bitboard.cpp"
#include "piece.h"

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

        std::vector<Move> Position::generateLegalMoves() const {
            //use magic bitboard to generate pseudo legal moves
            // we then check if the move is legal, and if it is, we add it to the list of legal moves
            std::vector<Move> pseudo_legal = generatePseudoLegalMoves();
            std::vector<Move> legal_moves;
            legal_moves.reserve(pseudo_legal.size());
            
            Square king_square = __builtin_ctzll(pieces_bb[KING] & color_bb[side_to_move]);
            Bitboard pinned_pieces = getPinnedPieces(side_to_move);
            Bitboard checkers = getCheckers();
            
            for (const Move& move : pseudo_legal) {
                if (isLegalMove(move, king_square, pinned_pieces, checkers)) {
                    legal_moves.push_back(move);
                }
            }
            
            return legal_moves;
        }

        template<PieceType PT>
        void Position::generatePieceMoves(std::vector<Move>& moves, Bitboard targets) const {
            Bitboard pieces = pieces_bb[PT] & color_bb[side_to_move];
            Bitboard occupied = color_bb[WHITE] | color_bb[BLACK];
            
            while (pieces) {
                Square from = pop_lsb(pieces);
                Bitboard attacks;
                
                if constexpr (PT == BISHOP) {
                    attacks = BishopAttacks[from][magic_index<BISHOP>(from, occupied)];
                } else if constexpr (PT == ROOK) {
                    attacks = RookAttacks[from][magic_index<ROOK>(from, occupied)];
                } else {  // QUEEN
                    attacks = BishopAttacks[from][magic_index<BISHOP>(from, occupied)] |
                            RookAttacks[from][magic_index<ROOK>(from, occupied)];
                }
                
                attacks &= targets;
                while (attacks) {
                    Square to = pop_lsb(attacks);
                    moves.emplace_back(from, to, NORMAL);
                }
            }
        }

        void Position::makeMove(const Move& move){
            StateInfo* new_state = ++state_info;
            *new_state = *(new_state-1);

            int from = move.from_square;
            int to = move.to_square;
            Piece move_piece = board[from];
            Piece captured_piece = board[to];

            // Incremental hash update
            // TO-DO
            uint64_t& hash_key = new_state->hash_key;
            hash_key ^= zobrist_psq[moving_piece][from];
            hash_key ^= zobrist_psq[moving_piece][to];
            
            if (captured_piece != NO_PIECE) {
                remove_piece(to, captured_piece);
                hash_key ^= zobrist_psq[captured_piece][to];
            }
            
            move_piece(from, to, moving_piece);
            
            // Handle special moves (castling, en passant, promotion)
            //TO-DO
            handle_special_moves(move);
            
            side_to_move = ~side_to_move;
            hash_key ^= zobrist_side;
            new_state->checkers = getAttackers(king_square(side_to_move), ~side_to_move);
        }


}