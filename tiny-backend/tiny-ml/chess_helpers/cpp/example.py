import chess_engine

# Create board and set starting position
board = chess_engine.ChessBitboard()
board.set_starting_position()

# Generate legal moves
moves = board.generate_legal_moves()
print(f"Found {len(moves)} legal moves")

# Make a move
if moves:
    board.make_move(moves[0])
    print("Made first legal move")