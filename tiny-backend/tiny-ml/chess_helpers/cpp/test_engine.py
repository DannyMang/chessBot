import pytest
import chess_engine

PERFT_SUITE = [
    # FEN, depth, nodes
    ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 1, 20),
    ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 2, 400),
    ("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", 3, 8902),
    ("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", 1, 48),
    ("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1", 2, 2039),
    ("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", 1, 14),
    ("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", 2, 191),
    ("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", 1, 44),
    ("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8", 2, 1486),
    ("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10", 1, 46),
    ("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10", 2, 2079),
]

@pytest.fixture
def board():
    """Provides a chess board instance for each test."""
    return chess_engine.ChessBitboard()

def test_initial_board_setup(board):
    """Test that the board is empty upon creation."""
    assert board.get_all_pieces() == 0
    for i in range(64):
        piece = board.get_piece_at(i)
        assert piece.is_empty()

def test_starting_position(board):
    """Verify the standard starting position."""
    board.set_starting_position()
    
    # White pieces
    assert board.get_piece_at(0).type() == chess_engine.PieceType.ROOK
    assert board.get_piece_at(1).type() == chess_engine.PieceType.KNIGHT
    assert board.get_piece_at(2).type() == chess_engine.PieceType.BISHOP
    assert board.get_piece_at(3).type() == chess_engine.PieceType.QUEEN
    assert board.get_piece_at(4).type() == chess_engine.PieceType.KING
    for i in range(8, 16):
        assert board.get_piece_at(i).type() == chess_engine.PieceType.PAWN
        assert board.get_piece_at(i).color() == chess_engine.Color.WHITE

    # Black pieces
    assert board.get_piece_at(56).type() == chess_engine.PieceType.ROOK
    assert board.get_piece_at(57).type() == chess_engine.PieceType.KNIGHT
    assert board.get_piece_at(58).type() == chess_engine.PieceType.BISHOP
    assert board.get_piece_at(59).type() == chess_engine.PieceType.QUEEN
    assert board.get_piece_at(60).type() == chess_engine.PieceType.KING
    for i in range(48, 56):
        assert board.get_piece_at(i).type() == chess_engine.PieceType.PAWN
        assert board.get_piece_at(i).color() == chess_engine.Color.BLACK
        
    assert board.white_to_move
    assert board.fullmove_number == 1

def test_set_and_get_piece(board):
    """Test setting and getting a piece."""
    piece = chess_engine.Piece(chess_engine.Color.WHITE, chess_engine.PieceType.QUEEN)
    board.set_piece(27, piece) # d4
    retrieved_piece = board.get_piece_at(27)
    assert retrieved_piece.type() == piece.type()
    assert retrieved_piece.color() == piece.color()
    
    # Verify bitboard is updated
    assert board.white_queens & (1 << 27) != 0

def test_clear_square(board):
    """Test clearing a square."""
    board.set_starting_position()
    board.clear_square(8) # Clear pawn on a2
    assert board.get_piece_at(8).is_empty()
    assert board.white_pawns & (1 << 8) == 0

def test_initial_legal_moves(board):
    """Test the number of legal moves from the starting position."""
    board.set_starting_position()
    moves = board.generate_legal_moves()
    # A fully correct engine should yield 20.
    assert len(moves) == 20

def test_make_move(board):
    """Test making a simple move."""
    board.set_starting_position()
    # e2-e4
    moves = board.generate_legal_moves()
    e4_move = next((m for m in moves if m.get_from() == 12 and m.get_to() == 28), None)
    
    assert e4_move is not None, "Move e2-e4 not found"
    
    board.make_move(e4_move)
    
    assert board.get_piece_at(12).is_empty()
    pawn = board.get_piece_at(28)
    assert pawn.type() == chess_engine.PieceType.PAWN
    assert pawn.color() == chess_engine.Color.WHITE
    assert not board.white_to_move
    # Fullmove number should increment after black's move, so it's still 1
    assert board.fullmove_number == 1

def test_is_in_check(board):
    """Test check detection. (currently partial impl)."""
    # Set up a check position (Fool's Mate)
    # 1. f3 e5 2. g4 Qh4#
    # Manually setting up because make_move is not fully implemented
    board.set_starting_position()
    board.clear_square(13) # f2 pawn
    board.clear_square(14) # g2 pawn
    board.clear_square(52) # e7 pawn
    board.clear_square(59) # d8 queen
    board.set_piece(21, chess_engine.Piece(chess_engine.Color.WHITE, chess_engine.PieceType.PAWN)) # f3
    board.set_piece(30, chess_engine.Piece(chess_engine.Color.WHITE, chess_engine.PieceType.PAWN)) # g4
    board.set_piece(36, chess_engine.Piece(chess_engine.Color.BLACK, chess_engine.PieceType.PAWN)) # e5
    board.set_piece(31, chess_engine.Piece(chess_engine.Color.BLACK, chess_engine.PieceType.QUEEN)) # h4
    
    board.white_to_move = True # White's turn to move out of check
    assert board.is_in_check(chess_engine.Color.WHITE)
    assert not board.is_in_check(chess_engine.Color.BLACK)

def test_perft_1(board):
    """Performance test at depth 1. Should be 20."""
    board.set_starting_position()
    assert board.perft(1) == 20

def test_perft_2(board):
    """Performance test at depth 2. Should be 400."""
    board.set_starting_position()
    assert board.perft(2) == 400

@pytest.mark.parametrize("fen,depth,nodes", PERFT_SUITE)
def test_perft_suite(board, fen, depth, nodes):
    """Run a battery of performance tests from various positions."""
    board.load_fen(fen)
    assert board.perft(depth) == nodes

def test_castling(board):
    """Test legal castling moves."""
    # Setup for white kingside castling
    board.set_starting_position()
    board.clear_square(1)  # Clear knight on b1
    board.clear_square(2)  # Clear bishop on c1
    board.clear_square(3)  # Clear queen on d1
    board.clear_square(5)  # Clear bishop on f1
    board.clear_square(6)  # Clear knight on g1

    moves = board.generate_legal_moves()
    # Kingside castling move is from e1 (4) to g1 (6)
    castle_move = next((m for m in moves if m.get_from() == 4 and m.get_to() == 6), None)
    assert castle_move is not None, "Kingside castling move not found"
    
    board.make_move(castle_move)
    assert board.get_piece_at(6).type() == chess_engine.PieceType.KING
    assert board.get_piece_at(5).type() == chess_engine.PieceType.ROOK
    assert board.get_piece_at(4).is_empty()
    assert board.get_piece_at(7).is_empty()

def test_en_passant(board):
    """Test a valid en passant capture."""
    # Set up pieces for the test
    board.set_piece(4, chess_engine.Piece(chess_engine.Color.WHITE, chess_engine.PieceType.KING))
    board.set_piece(60, chess_engine.Piece(chess_engine.Color.BLACK, chess_engine.PieceType.KING))
    board.set_piece(36, chess_engine.Piece(chess_engine.Color.WHITE, chess_engine.PieceType.PAWN)) # White pawn on e5
    board.set_piece(51, chess_engine.Piece(chess_engine.Color.BLACK, chess_engine.PieceType.PAWN)) # Black pawn on d7
    
    board.white_to_move = False # Black's turn
    
    # Black pushes pawn d7-d5, creating an en passant opportunity
    d5_move = next(m for m in board.generate_legal_moves() if m.get_from() == 51 and m.get_to() == 35)
    board.make_move(d5_move)
    
    # Now it's white's turn. The en passant square should be d6 (43)
    assert board.en_passant_square == 43
    
    # Check if the en passant capture e5xd6 is available
    moves = board.generate_legal_moves()
    ep_move = next((m for m in moves if m.get_from() == 36 and m.get_to() == 43), None)
    
    assert ep_move is not None, "En passant move not found"
    assert ep_move.get_flags() == 1 # EN_PASSANT_FLAG is 1 in C++
    
    # Make the en passant move
    board.make_move(ep_move)
    
    # Verify the board state
    assert board.get_piece_at(43).type() == chess_engine.PieceType.PAWN # White pawn on d6
    assert board.get_piece_at(43).color() == chess_engine.Color.WHITE
    assert board.get_piece_at(35).is_empty() # Black pawn on d5 is captured
    assert board.get_piece_at(36).is_empty() # White pawn moved from e5

def test_promotion(board):
    """Test that pawn promotion generates correct moves and updates the board."""
    # Set up a pawn about to promote
    board.set_piece(4, chess_engine.Piece(chess_engine.Color.WHITE, chess_engine.PieceType.KING))
    board.set_piece(60, chess_engine.Piece(chess_engine.Color.BLACK, chess_engine.PieceType.KING))
    board.set_piece(55, chess_engine.Piece(chess_engine.Color.WHITE, chess_engine.PieceType.PAWN)) # White pawn on h7
    
    board.white_to_move = True
    
    # Generate moves, expecting 4 promotion moves
    moves = board.generate_legal_moves()
    promotion_moves = [m for m in moves if m.get_from() == 55 and m.get_to() == 63]
    assert len(promotion_moves) == 4, "Should be 4 promotion moves"
    
    # Find the queen promotion
    # PROMOTION_QUEEN_FLAG = 11 in C++
    queen_promo = next((m for m in promotion_moves if m.get_flags() == 11), None)
    assert queen_promo is not None, "Queen promotion move not found"
    
    # Make the move
    board.make_move(queen_promo)
    
    # Verify the promotion
    promoted_piece = board.get_piece_at(63)
    assert promoted_piece.type() == chess_engine.PieceType.QUEEN
    assert promoted_piece.color() == chess_engine.Color.WHITE
    assert board.get_piece_at(55).is_empty()