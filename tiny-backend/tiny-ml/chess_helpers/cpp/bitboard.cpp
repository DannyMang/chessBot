#include "bitboard.h"
#include <algorithm>

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
    MagicMoves::init();
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
            return MagicMoves::getRookAttacks(square, occupancy);
        case BISHOP:
            return MagicMoves::getBishopAttacks(square, occupancy);
        case QUEEN:
            return MagicMoves::getQueenAttacks(square, occupancy);
        default:
            return 0ULL; // Handle other pieces separately
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
        
        Bitboard attacks = MagicMoves::getRookAttacks(from, occupancy);
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
        
        Bitboard attacks = MagicMoves::getBishopAttacks(from, occupancy);
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
        
        Bitboard attacks = MagicMoves::getQueenAttacks(from, occupancy);
        attacks &= ~friendly;
        
        while (attacks) {
            Square to = __builtin_ctzll(attacks);
            attacks &= attacks - 1;
            moves.emplace_back(from, to, QUEEN);
        }
    }
    
    // TODO: Add pawn, knight, king moves
    
    return moves;
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
    Piece moving_piece = getPieceAt(move.from());
    Piece captured_piece = getPieceAt(move.to());
    
    // Move the piece
    clearSquare(move.from());
    setPiece(move.to(), moving_piece);
    
    // Update game state
    white_to_move = !white_to_move;
    
    // TODO: Handle castling, en passant, promotion
    // TODO: Update castling rights based on move
    // TODO: Update halfmove clock
    if (white_to_move) fullmove_number++;
}

bool ChessBitboard::isLegal(const Move& move) const {
    // Create a copy and make the move
    ChessBitboard temp = *this;
    temp.makeMove(move);
    
    // Check if our king is in check after the move
    Bitboard king_bb = white_to_move ? temp.white_king : temp.black_king;
    Square king_square = __builtin_ctzll(king_bb);
    
    // TODO: Check if king is attacked by opponent pieces
    // This requires implementing attack generation for all piece types
    
    return true; // Placeholder - implement proper check detection
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