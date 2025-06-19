import pytest
import chess_engine

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

@pytest.mark.xfail(reason="Perft not fully implemented yet")
def test_perft_1(board):
    """Performance test at depth 1. Should be 20."""
    board.set_starting_position()
    assert board.perft(1) == 20

@pytest.mark.xfail(reason="Perft not fully implemented yet")
def test_perft_2(board):
    """Performance test at depth 2. Should be 400."""
    board.set_starting_position()
    assert board.perft(2) == 400

@pytest.mark.xfail(reason="Castling not implemented")
def test_castling():
    """Test castling. Not implemented yet."""
    assert False, "Test for castling not implemented."
    
@pytest.mark.xfail(reason="En passant not implemented")
def test_en_passant():
    """Test en passant. Not implemented yet."""
    assert False, "Test for en passant not implemented."

@pytest.mark.xfail(reason="Promotion not implemented")
def test_promotion():
    """Test pawn promotion. Not implemented yet."""
    assert False, "Test for pawn promotion not implemented." 