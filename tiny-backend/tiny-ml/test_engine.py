import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from chess_helpers.cpp import chess_engine

def test_perft():
    print('Running Perft Test...')
    board = chess_engine.ChessBitboard()
    board.set_starting_position()
    
    # Known correct values for perft from the starting position
    # See: https://www.chessprogramming.org/Perft_Results
    expected_nodes = {
        1: 20,
        2: 400,
        3: 8902,
        4: 197281,
    }
    
    depth = 3
    nodes = board.perft(depth)
    
    print(f'Perft({depth}) result: {nodes}')
    if nodes == expected_nodes[depth]:
        print('Perft test PASSED!')
    else:
        print(f'Perft test FAILED! Expected: {expected_nodes[depth]}')

if __name__ == '__main__':
    test_perft()
