import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tiny-ml'))

from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import chess.engine

# tinygrad and model imports
from tinygrad import Tensor
from tinygrad.helpers import getenv
from tinygrad.nn.state import safe_load, get_state_dict

from model import ChessNet
from mcts import MCTSNode, mcts_alphazero
from chess_helpers.cpp import chess_engine as cpp_engine
from chess_helpers.game_logic import get_board_planes

app = Flask(__name__)
CORS(app)  

class ChessBot:
    def __init__(self, model_path="tiny-ml/models/chess_net_checkpoint.safetensors"):
        self.board = chess.Board() # For python-chess compatibility if needed elsewhere
        self.model = self._load_model(model_path)
        Tensor.training = False # Set model to evaluation mode

    def _load_model(self, model_path):
        """Loads the tinygrad model from a checkpoint."""
        model = ChessNet()
        try:
            print("Loading model from checkpoint...")
            state_dict = safe_load(model_path)
            model_state_dict = get_state_dict(model)
            for k, v in state_dict.items():
                if k in model_state_dict:
                    model_state_dict[k].assign(v).realize()
            print("Model weights loaded successfully.")
            return model
        except FileNotFoundError:
            print("\n---")
            print(f"Error: Model checkpoint '{model_path}' not found.")
            print("Please ensure the model is trained and the path is correct.")
            print("---\n")
            return None

    def reset_board(self):
        """Reset the chess board to starting position"""
        self.board.reset()

    def get_best_move(self, fen):
        """
        Get the best move from the AlphaZero model using MCTS.
        """
        if self.model is None:
            raise Exception("Model is not loaded.")

        # 1. Set up the board in our C++ engine
        ai_board = cpp_engine.ChessBitboard()
        ai_board.load_fen(fen)

        if ai_board.is_game_over():
            return None

        # 2. Run MCTS to find the best move
        print("AI is thinking...")
        root_node = MCTSNode(board=ai_board)
        
        num_simulations = getenv("SIMS", 800)
        
        current_planes = get_board_planes(ai_board)
        board_plane_history = [current_planes]

        best_child_node = mcts_alphazero(
            self.model,
            root_node,
            board_plane_history,
            num_simulations=num_simulations,
            dirichlet_epsilon=0.0
        )
        
        if best_child_node is None:
            return None

        # 3. Convert move to UCI format for the frontend
        move = best_child_node.move
        
        from_sq = move.get_from()
        to_sq = move.get_to()
        
        from_str = f"{chr(ord('a') + from_sq % 8)}{from_sq // 8 + 1}"
        to_str = f"{chr(ord('a') + to_sq % 8)}{to_sq // 8 + 1}"
        
        promotion = ""
        flags = move.get_flags()
        if flags == 8: promotion = 'n'
        elif flags == 9: promotion = 'b'
        elif flags == 10: promotion = 'r'
        elif flags == 11: promotion = 'q'

        return {
            "from": from_str,
            "to": to_str,
            "promotion": promotion if promotion else None
        }


# Initialize the chess bot
bot = ChessBot()

@app.route('/api/move', methods=['POST'])
def handle_move():
    """Handle move requests from the frontend"""
    try:
        data = request.get_json()
        fen = data.get('fen')

        if not fen:
            return jsonify({"error": "FEN string is required"}), 400

        bot.board.set_fen(fen)

        if bot.board.is_game_over():
             return jsonify({
                "message": "Game is over",
                "game_over": True
            })

        ai_move = bot.get_best_move(fen)
        
        if ai_move is None:
            return jsonify({
                "message": "Game is over or AI has no legal moves.",
                "game_over": True
            })
        
        try:
            move_str = ai_move["from"] + ai_move["to"]
            if ai_move["promotion"]:
                move_str += ai_move["promotion"]
            
            move = chess.Move.from_uci(move_str)
            if move in bot.board.legal_moves:
                bot.board.push(move)
                
                is_check_after_ai = bot.board.is_check()
                is_checkmate_after_ai = bot.board.is_checkmate()
                is_stalemate_after_ai = bot.board.is_stalemate()
                is_game_over = is_checkmate_after_ai or is_stalemate_after_ai
                
                game_result = None
                if is_checkmate_after_ai:
                    winner = "Black" if bot.board.turn == chess.WHITE else "White"
                    game_result = f"Checkmate! {winner} wins!"
                elif is_stalemate_after_ai:
                    game_result = "Stalemate! Game is a draw."
                
                response = {
                    "next_move": ai_move,
                    "message": "AI move successful",
                    "new_fen": bot.board.fen(),
                    "game_state": {
                        "is_check": is_check_after_ai,
                        "is_checkmate": is_checkmate_after_ai,
                        "is_stalemate": is_stalemate_after_ai,
                        "is_game_over": is_game_over,
                        "result": game_result,
                        "turn": "white" if bot.board.turn == chess.WHITE else "black"
                    }
                }
                
                print(f"✅ Move successful. Turn: {'White' if bot.board.turn == chess.WHITE else 'Black'}")
                return jsonify(response)
            else:
                print(f"Illegal move generated by AI: {move_str}")
                return jsonify({
                    "error": "Illegal move generated by AI",
                    "message": f"AI tried to make an invalid move: {move_str}"
                }), 500
                
        except Exception as e:
            print(f"Error processing AI move: {e}")
            return jsonify({
                "error": "Move processing failed",
                "message": str(e)
            }), 500
            
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({
            "error": "Server error",
            "message": str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_game():
    """Reset the game to starting position"""
    bot.reset_board()
    return jsonify({
        "message": "Game reset successfully",
        "fen": bot.board.fen()
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current server status"""
    return jsonify({
        "status": "running",
        "message": "Chess bot server is active",
        "current_fen": bot.board.fen()
    })

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        "message": "Chess Bot Backend Server",
        "status": "running",
        "endpoints": {
            "POST /api/move": "Submit a move and get AI response",
            "POST /api/reset": "Reset the game",
            "GET /api/status": "Get server status"
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Chess Bot Backend Server...")
    print("📡 Server will run on http://localhost:8080")
    print("🎯 Frontend should connect to: http://localhost:8080/api/move")
    print("💡 AI strength can be configured with the 'SIMS' environment variable.")
    
    app.run(host='0.0.0.0', port=8080, debug=True) 