#include "bitboard.h"
#include <algorithm>
#include "magicmoves.h"
#include "bitmasks.h"

void ChessBitboard::initAttacks() {
    for (int sq = 0; sq < 64; sq++) {
        Bitboard b = 1ULL << sq;
        // Knight attacks
        Bitboard knight_atks = 0ULL;
        knight_atks |= (b & Bitmasks::NOT_GH_FILE) << 6;
        knight_atks |= (b & Bitmasks::NOT_G_FILE) << 15;
        knight_atks |= (b & Bitmasks::NOT_A_FILE) << 17;
        knight_atks |= (b & Bitmasks::NOT_AB_FILE) << 10;
        knight_atks |= (b & Bitmasks::NOT_AB_FILE) >> 6;
        knight_atks |= (b & Bitmasks::NOT_A_FILE) >> 15;
        knight_atks |= (b & Bitmasks::NOT_H_FILE) >> 17;
        knight_atks |= (b & Bitmasks::NOT_GH_FILE) >> 10;
        knight_attacks[sq] = knight_atks;

        // King attacks
        Bitboard king_atks = 0ULL;
        king_atks |= (b & Bitmasks::NOT_A_FILE) << 7;
        king_atks |= (b) << 8;
        king_atks |= (b & Bitmasks::NOT_H_FILE) << 9;
        king_atks |= (b & Bitmasks::NOT_H_FILE) << 1;
        king_atks |= (b & Bitmasks::NOT_H_FILE) >> 7;
        king_atks |= (b) >> 8;
        king_atks |= (b & Bitmasks::NOT_A_FILE) >> 9;
        king_atks |= (b & Bitmasks::NOT_A_FILE) >> 1;
        king_attacks[sq] = king_atks;
    }
}

ChessBitboard::ChessBitboard() {
    // Initialize all bitboards to 0
    white_pawns = white_knights = white_bishops = 0;
    white_rooks = white_queens = white_king = 0;
    black_pawns = black_knights = black_bishops = 0;
    black_rooks = black_queens = black_king = 0;
    
    white_to_move = true;
    //use 4 bits here since only 4 possible castles: queenside, kingside etc
    castling_rights = 0b1111;
    en_passant_square = -1;
    halfmove_clock = 0;
    fullmove_number = 1;
    
    // Clear mailbox
    for (int i = 0; i < 64; i++) {
        mailbox[i] = Piece();
    }
    
    // Initialize attack tables
    initAttacks();

    // Initialize magic bitboards
    initmagicmoves();
}

Bitboard ChessBitboard::getWhitePieces() const {
    return white_pawns | white_knights | white_bishops | white_rooks | white_queens | white_king;
}

Bitboard ChessBitboard::getBlackPieces() const {
    return black_pawns | black_knights | black_bishops | black_rooks | black_queens | black_king;
}

Bitboard ChessBitboard::getAllPieces() const {
    return getWhitePieces() | getBlackPieces();
}

void ChessBitboard::setStartingPosition() {
    // White pieces
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
    
    updateMailbox();
}

Piece ChessBitboard::getPieceAt(Square square) const {
    return mailbox[square];
}

void ChessBitboard::setPiece(Square square, Piece piece) {
    // Clear the square first
    clearSquare(square);
    
    // Set the piece in mailbox
    mailbox[square] = piece;
    
    // Set the corresponding bitboard
    if (!piece.is_empty()) {
        addPieceToBitboard(square, piece);
    }
}

void ChessBitboard::clearSquare(Square square) {
    Piece old_piece = mailbox[square];
    if (!old_piece.is_empty()) {
        removePieceFromBitboard(square, old_piece);
    }
    mailbox[square] = Piece();
}

Bitboard ChessBitboard::getAttacks(Square square, Piece::Type piece_type, Bitboard occupancy) const {
    switch (piece_type) {
        case Piece::Type::ROOK:
            return Rmagic(square, occupancy);
        case Piece::Type::BISHOP:
            return Bmagic(square, occupancy);
        case Piece::Type::QUEEN:
            return Qmagic(square, occupancy);
        default:
            return 0ULL;
    }
}

std::vector<Move> ChessBitboard::generatePseudoLegalMoves() const {
    std::vector<Move> moves;
    moves.reserve(256); // Pre-allocate for performance
    
    Bitboard occupancy = getAllPieces();
    Bitboard friendly = white_to_move ? getWhitePieces() : getBlackPieces();
    Bitboard enemy = white_to_move ? getBlackPieces() : getWhitePieces();
    
    // Generate moves for each piece type
    Bitboard pieces = white_to_move ? white_rooks : black_rooks;
    while (pieces) {
        Square from = __builtin_ctzll(pieces); // Get LSB
        pieces &= pieces - 1; // Clear LSB
        
        Bitboard attacks = Rmagic(from, occupancy);
        attacks &= ~friendly; // Can't capture own pieces
        
        while (attacks) {
            Square to = __builtin_ctzll(attacks);
            attacks &= attacks - 1;
            moves.emplace_back(from, to, Piece::Type::ROOK);
        }
    }
    
    // Similar for bishops
    pieces = white_to_move ? white_bishops : black_bishops;
    while (pieces) {
        Square from = __builtin_ctzll(pieces);
        pieces &= pieces - 1;
        
        Bitboard attacks = Bmagic(from, occupancy);
        attacks &= ~friendly;
        
        while (attacks) {
            Square to = __builtin_ctzll(attacks);
            attacks &= attacks - 1;
            moves.emplace_back(from, to, Piece::Type::BISHOP);
        }
    }
    
    // Queens
    pieces = white_to_move ? white_queens : black_queens;
    while (pieces) {
        Square from = __builtin_ctzll(pieces);
        pieces &= pieces - 1;
        
        Bitboard attacks = Qmagic(from, occupancy);
        attacks &= ~friendly;
        
        while (attacks) {
            Square to = __builtin_ctzll(attacks);
            attacks &= attacks - 1;
            moves.emplace_back(from, to, Piece::Type::QUEEN);
        }
    }
    
    generatePawnMoves(moves);
    generateKnightMoves(moves);
    generateKingMoves(moves);
    
    return moves;
}

void ChessBitboard::generatePawnMoves(std::vector<Move>& moves) const {
    Bitboard pawns = white_to_move ? white_pawns : black_pawns;
    Bitboard enemy_pieces = white_to_move ? getBlackPieces() : getWhitePieces();
    
    int direction = white_to_move ? 8 : -8;
    Bitboard promotion_rank = white_to_move ? Bitmasks::RANK_7 : Bitmasks::RANK_2;

    while (pawns) {
        Square from = __builtin_ctzll(pawns);
        pawns &= pawns - 1;

        // 1. Pushes (single and double)
        Square to = from + direction;
        if (to >= 0 && to < 64 && getPieceAt(to).is_empty()) {
            if ((1ULL << to) & promotion_rank) {
                // This is a promotion push
                moves.emplace_back(from, to, Piece::Type::PAWN, Move::PROMOTION_QUEEN_FLAG);
                moves.emplace_back(from, to, Piece::Type::PAWN, Move::PROMOTION_ROOK_FLAG);
                moves.emplace_back(from, to, Piece::Type::PAWN, Move::PROMOTION_BISHOP_FLAG);
                moves.emplace_back(from, to, Piece::Type::PAWN, Move::PROMOTION_KNIGHT_FLAG);
            } else {
                // Regular single push
                moves.emplace_back(from, to, Piece::Type::PAWN);
            }

            // Double push from starting rank
            bool is_on_start_rank = (1ULL << from) & (white_to_move ? Bitmasks::RANK_2 : Bitmasks::RANK_7);
            if (is_on_start_rank) {
                Square double_to = from + 2 * direction;
                if (double_to >= 0 && double_to < 64 && getPieceAt(double_to).is_empty()) {
                    moves.emplace_back(from, double_to, Piece::Type::PAWN);
                }
            }
        }
        
        // 2. Captures
        Bitboard from_bb = 1ULL << from;
        Bitboard attacks = 0ULL;
        if (white_to_move) {
            attacks = (((from_bb & Bitmasks::NOT_A_FILE) << 7) | ((from_bb & Bitmasks::NOT_H_FILE) << 9));
        } else {
            attacks = (((from_bb & Bitmasks::NOT_H_FILE) >> 7) | ((from_bb & Bitmasks::NOT_A_FILE) >> 9));
        }
        attacks &= enemy_pieces;

        while (attacks) {
            Square capture_to = __builtin_ctzll(attacks);
            attacks &= attacks - 1;
            if ((1ULL << capture_to) & promotion_rank) {
                // This is a promotion capture
                moves.emplace_back(from, capture_to, Piece::Type::PAWN, Move::PROMOTION_QUEEN_FLAG);
                moves.emplace_back(from, capture_to, Piece::Type::PAWN, Move::PROMOTION_ROOK_FLAG);
                moves.emplace_back(from, capture_to, Piece::Type::PAWN, Move::PROMOTION_BISHOP_FLAG);
                moves.emplace_back(from, capture_to, Piece::Type::PAWN, Move::PROMOTION_KNIGHT_FLAG);
            } else {
                // Regular capture
                moves.emplace_back(from, capture_to, Piece::Type::PAWN);
            }
        }
    }
}

void ChessBitboard::generateKnightMoves(std::vector<Move>& moves) const {
    // TO-DO double check this method (ai generated)
    static const int knight_moves[8] = {-17, -15, -10, -6, 6, 10, 15, 17};
    
    Bitboard knights = white_to_move ? white_knights : black_knights;
    Bitboard friendly = white_to_move ? getWhitePieces() : getBlackPieces();
    
    while (knights) {
        Square from = __builtin_ctzll(knights);
        knights &= knights - 1;
        
        for (int offset : knight_moves) {
            Square to = from + offset;
            if (to >= 0 && to < 64 && !(friendly & (1ULL << to))) {
                // Check if move is valid (not wrapping around board)
                int from_file = from % 8;
                int to_file = to % 8;
                if (abs(from_file - to_file) <= 2) {
                    moves.emplace_back(from, to, Piece::Type::KNIGHT);
                }
            }
        }
    }
}

void ChessBitboard::generateKingMoves(std::vector<Move>& moves) const {
    // TO-DO double check this method (ai generated)
    static const int king_moves[8] = {-9, -8, -7, -1, 1, 7, 8, 9};
    
    Bitboard king = white_to_move ? white_king : black_king;
    Bitboard friendly = white_to_move ? getWhitePieces() : getBlackPieces();
    
    Square from = __builtin_ctzll(king);
    
    for (int offset : king_moves) {
        Square to = from + offset;
        if (to >= 0 && to < 64 && !(friendly & (1ULL << to))) {
            // Check if move is valid (not wrapping around board)
            int from_file = from % 8;
            int to_file = to % 8;
            if (abs(from_file - to_file) <= 1) {
                moves.emplace_back(from, to, Piece::Type::KING);
            }
        }
    }
}

std::vector<Move> ChessBitboard::generateLegalMoves() const {
    std::vector<Move> pseudo_legal = generatePseudoLegalMoves();
    std::vector<Move> legal_moves;
    legal_moves.reserve(pseudo_legal.size());
    
    for (const Move& move : pseudo_legal) {
        if (isLegal(move)) {
            legal_moves.push_back(move);
        }
    }
    
    return legal_moves;
}

void ChessBitboard::makeMove(const Move& move) {
    Piece moving_piece = getPieceAt(move.getFrom());
    Piece captured_piece = getPieceAt(move.getTo());
    
    // Move the piece
    clearSquare(move.getFrom());
    setPiece(move.getTo(), moving_piece);
    
    // Update game state
    white_to_move = !white_to_move;
    
    // TODO: Handle castling, en passant, promotion
    // TODO: Update castling rights based on move
    // TODO: Update halfmove clock
    if (white_to_move) fullmove_number++;
}

bool ChessBitboard::isLegal(const Move& move) const {
     // Simple legality check - implement properly later
    ChessBitboard temp = *this;
    temp.makeMove(move);
    
    // Check if our king is in check after the move
    Piece::Color our_color = white_to_move ? Piece::Color::WHITE : Piece::Color::BLACK;
    return !temp.isInCheck(our_color);
}

bool ChessBitboard::isInCheck(Piece::Color color) const {
    Bitboard king_bb = (color == Piece::Color::WHITE) ? white_king : black_king;
    Square king_square = __builtin_ctzll(king_bb);
    Piece::Color enemy_color = (color == Piece::Color::WHITE) ? Piece::Color::BLACK : Piece::Color::WHITE;
    
    return isSquareAttacked(king_square, enemy_color);
}

bool ChessBitboard::isSquareAttacked(Square square, Piece::Color by_color) const {
    Bitboard occupancy = getAllPieces();
    
    // Check for rook/queen attacks
    Bitboard rook_attacks = Rmagic(square, occupancy);
    Bitboard enemy_rooks_queens = (by_color == Piece::Color::WHITE) ? 
        (white_rooks | white_queens) : (black_rooks | black_queens);
    if (rook_attacks & enemy_rooks_queens) return true;
    
    // Check for bishop/queen attacks  
    Bitboard bishop_attacks = Bmagic(square, occupancy);
    Bitboard enemy_bishops_queens = (by_color == Piece::Color::WHITE) ? 
        (white_bishops | white_queens) : (black_bishops | black_queens);
    if (bishop_attacks & enemy_bishops_queens) return true;
    
    // Check for pawn attacks
    Bitboard enemy_pawns = (by_color == Piece::Color::WHITE) ? white_pawns : black_pawns;
    Bitboard square_bb = 1ULL << square;
    if (by_color == Piece::Color::WHITE) {
        // White pawns attack from NW and NE relative to the piece at 'square'
        if ((((square_bb & Bitmasks::NOT_A_FILE) >> 9) & enemy_pawns) || (((square_bb & Bitmasks::NOT_H_FILE) >> 7) & enemy_pawns)) {
            return true;
        }
    } else { // Black attacks
        if ((((square_bb & Bitmasks::NOT_H_FILE) << 9) & enemy_pawns) || (((square_bb & Bitmasks::NOT_A_FILE) << 7) & enemy_pawns)) {
            return true;
        }
    }

    // Check for knight attacks
    Bitboard enemy_knights = (by_color == Piece::Color::WHITE) ? white_knights : black_knights;
    if (knight_attacks[square] & enemy_knights) return true;

    // Check for king attacks
    Bitboard enemy_king = (by_color == Piece::Color::WHITE) ? white_king : black_king;
    if (king_attacks[square] & enemy_king) return true;

    return false;
}

uint64_t ChessBitboard::perft(int depth) const {
    if (depth == 0) return 1;
    
    uint64_t nodes = 0;
    auto moves = generateLegalMoves();
    
    for (const Move& move : moves) {
        ChessBitboard temp = *this;
        temp.makeMove(move);
        nodes += temp.perft(depth - 1);
    }
    
    return nodes;
}



// Helper methods
void ChessBitboard::updateMailbox() {
    // Clear mailbox
    for (int i = 0; i < 64; i++) {
        mailbox[i] = Piece();
    }
    
    // Update from bitboards
    for (int square = 0; square < 64; square++) {
        Bitboard mask = 1ULL << square;
        
        if (white_pawns & mask) mailbox[square] = Piece(Piece::Color::WHITE, Piece::Type::PAWN);
        else if (white_knights & mask) mailbox[square] = Piece(Piece::Color::WHITE, Piece::Type::KNIGHT);
        else if (white_bishops & mask) mailbox[square] = Piece(Piece::Color::WHITE, Piece::Type::BISHOP);
        else if (white_rooks & mask) mailbox[square] = Piece(Piece::Color::WHITE, Piece::Type::ROOK);
        else if (white_queens & mask) mailbox[square] = Piece(Piece::Color::WHITE, Piece::Type::QUEEN);
        else if (white_king & mask) mailbox[square] = Piece(Piece::Color::WHITE, Piece::Type::KING);
        
        else if (black_pawns & mask) mailbox[square] = Piece(Piece::Color::BLACK, Piece::Type::PAWN);
        else if (black_knights & mask) mailbox[square] = Piece(Piece::Color::BLACK, Piece::Type::KNIGHT);
        else if (black_bishops & mask) mailbox[square] = Piece(Piece::Color::BLACK, Piece::Type::BISHOP);
        else if (black_rooks & mask) mailbox[square] = Piece(Piece::Color::BLACK, Piece::Type::ROOK);
        else if (black_queens & mask) mailbox[square] = Piece(Piece::Color::BLACK, Piece::Type::QUEEN);
        else if (black_king & mask) mailbox[square] = Piece(Piece::Color::BLACK, Piece::Type::KING);
    }
}

void ChessBitboard::addPieceToBitboard(Square square, Piece piece) {
    Bitboard mask = 1ULL << square;
    
    if (piece.color() == Piece::Color::WHITE) {
        switch (piece.type()) {
            case Piece::Type::PAWN: white_pawns |= mask; break;
            case Piece::Type::KNIGHT: white_knights |= mask; break;
            case Piece::Type::BISHOP: white_bishops |= mask; break;
            case Piece::Type::ROOK: white_rooks |= mask; break;
            case Piece::Type::QUEEN: white_queens |= mask; break;
            case Piece::Type::KING: white_king |= mask; break;
            case Piece::Type::NONE: break;
        }
    } else {
        switch (piece.type()) {
            case Piece::Type::PAWN: black_pawns |= mask; break;
            case Piece::Type::KNIGHT: black_knights |= mask; break;
            case Piece::Type::BISHOP: black_bishops |= mask; break;
            case Piece::Type::ROOK: black_rooks |= mask; break;
            case Piece::Type::QUEEN: black_queens |= mask; break;
            case Piece::Type::KING: black_king |= mask; break;
            case Piece::Type::NONE: break;
        }
    }
}

void ChessBitboard::removePieceFromBitboard(Square square, Piece piece) {
    Bitboard mask = ~(1ULL << square);
    
    if (piece.color() == Piece::Color::WHITE) {
        switch (piece.type()) {
            case Piece::Type::PAWN: white_pawns &= mask; break;
            case Piece::Type::KNIGHT: white_knights &= mask; break;
            case Piece::Type::BISHOP: white_bishops &= mask; break;
            case Piece::Type::ROOK: white_rooks &= mask; break;
            case Piece::Type::QUEEN: white_queens &= mask; break;
            case Piece::Type::KING: white_king &= mask; break;
            case Piece::Type::NONE: break;
        }
    } else {
        switch (piece.type()) {
            case Piece::Type::PAWN: black_pawns &= mask; break;
            case Piece::Type::KNIGHT: black_knights &= mask; break;
            case Piece::Type::BISHOP: black_bishops &= mask; break;
            case Piece::Type::ROOK: black_rooks &= mask; break;
            case Piece::Type::QUEEN: black_queens &= mask; break;
            case Piece::Type::KING: black_king &= mask; break;
            case Piece::Type::NONE: break;
        }
    }
}