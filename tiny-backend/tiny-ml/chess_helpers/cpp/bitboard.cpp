#include "bitboard.h"
#include <algorithm>
#include "magicmoves.h"

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

Bitboard ChessBitboard::getAttacks(Square square, PieceType piece_type, Bitboard occupancy) const {
    switch (piece_type) {
        case ROOK:
            return Rmagic(square, occupancy);
        case BISHOP:
            return Bmagic(square, occupancy);
        case QUEEN:
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
            moves.emplace_back(from, to, ROOK);
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
            moves.emplace_back(from, to, BISHOP);
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
            moves.emplace_back(from, to, QUEEN);
        }
    }
    
    generatePawnMoves(moves);
    generateKnightMoves(moves);
    generateKingMoves(moves);
    
    return moves;
}
void ChessBitboard::generatePawnMoves(std::vector<Move>& moves) const {
    // TO-DO double check this method 
    Bitboard pawns = white_to_move ? white_pawns : black_pawns;
    int direction = white_to_move ? 8 : -8;
    
    while (pawns) {
        Square from = __builtin_ctzll(pawns);
        pawns &= pawns - 1;
        
        Square to = from + direction;
        if (to >= 0 && to < 64 && getPieceAt(to).is_empty()) {
            moves.emplace_back(from, to, PAWN);
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
                    moves.emplace_back(from, to, KNIGHT);
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
                moves.emplace_back(from, to, KING);
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
    Color our_color = white_to_move ? WHITE : BLACK;
    return !temp.isInCheck(our_color);
}

bool ChessBitboard::isInCheck(Color color) const {
    Bitboard king_bb = (color == WHITE) ? white_king : black_king;
    Square king_square = __builtin_ctzll(king_bb);
    Color enemy_color = (color == WHITE) ? BLACK : WHITE;
    
    return isSquareAttacked(king_square, enemy_color);
}
bool ChessBitboard::isSquareAttacked(Square square, Color by_color) const {
    // Simple attack detection - implement properly later
    Bitboard occupancy = getAllPieces();
    
    // Check for rook/queen attacks
    Bitboard rook_attacks = Rmagic(square, occupancy);
    Bitboard enemy_rooks_queens = (by_color == WHITE) ? 
        (white_rooks | white_queens) : (black_rooks | black_queens);
    if (rook_attacks & enemy_rooks_queens) return true;
    
    // Check for bishop/queen attacks  
    Bitboard bishop_attacks = Bmagic(square, occupancy);
    Bitboard enemy_bishops_queens = (by_color == WHITE) ? 
        (white_bishops | white_queens) : (black_bishops | black_queens);
    if (bishop_attacks & enemy_bishops_queens) return true;
    
    // TODO: Check for pawn, knight, king attacks
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
        
        if (white_pawns & mask) mailbox[square] = Piece(Piece::WHITE, Piece::PAWN);
        else if (white_knights & mask) mailbox[square] = Piece(Piece::WHITE, Piece::KNIGHT);
        else if (white_bishops & mask) mailbox[square] = Piece(Piece::WHITE, Piece::BISHOP);
        else if (white_rooks & mask) mailbox[square] = Piece(Piece::WHITE, Piece::ROOK);
        else if (white_queens & mask) mailbox[square] = Piece(Piece::WHITE, Piece::QUEEN);
        else if (white_king & mask) mailbox[square] = Piece(Piece::WHITE, Piece::KING);
        
        else if (black_pawns & mask) mailbox[square] = Piece(Piece::BLACK, Piece::PAWN);
        else if (black_knights & mask) mailbox[square] = Piece(Piece::BLACK, Piece::KNIGHT);
        else if (black_bishops & mask) mailbox[square] = Piece(Piece::BLACK, Piece::BISHOP);
        else if (black_rooks & mask) mailbox[square] = Piece(Piece::BLACK, Piece::ROOK);
        else if (black_queens & mask) mailbox[square] = Piece(Piece::BLACK, Piece::QUEEN);
        else if (black_king & mask) mailbox[square] = Piece(Piece::BLACK, Piece::KING);
    }
}

void ChessBitboard::addPieceToBitboard(Square square, Piece piece) {
    Bitboard mask = 1ULL << square;
    
    if (piece.color() == Piece::WHITE) {
        switch (piece.type()) {
            case Piece::PAWN: white_pawns |= mask; break;
            case Piece::KNIGHT: white_knights |= mask; break;
            case Piece::BISHOP: white_bishops |= mask; break;
            case Piece::ROOK: white_rooks |= mask; break;
            case Piece::QUEEN: white_queens |= mask; break;
            case Piece::KING: white_king |= mask; break;
        }
    } else {
        switch (piece.type()) {
            case Piece::PAWN: black_pawns |= mask; break;
            case Piece::KNIGHT: black_knights |= mask; break;
            case Piece::BISHOP: black_bishops |= mask; break;
            case Piece::ROOK: black_rooks |= mask; break;
            case Piece::QUEEN: black_queens |= mask; break;
            case Piece::KING: black_king |= mask; break;
        }
    }
}

void ChessBitboard::removePieceFromBitboard(Square square, Piece piece) {
    Bitboard mask = ~(1ULL << square);
    
    if (piece.color() == Piece::WHITE) {
        switch (piece.type()) {
            case Piece::PAWN: white_pawns &= mask; break;
            case Piece::KNIGHT: white_knights &= mask; break;
            case Piece::BISHOP: white_bishops &= mask; break;
            case Piece::ROOK: white_rooks &= mask; break;
            case Piece::QUEEN: white_queens &= mask; break;
            case Piece::KING: white_king &= mask; break;
        }
    } else {
        switch (piece.type()) {
            case Piece::PAWN: black_pawns &= mask; break;
            case Piece::KNIGHT: black_knights &= mask; break;
            case Piece::BISHOP: black_bishops &= mask; break;
            case Piece::ROOK: black_rooks &= mask; break;
            case Piece::QUEEN: black_queens &= mask; break;
            case Piece::KING: black_king &= mask; break;
        }
    }
}