from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import chess
import chess.engine

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

class ChessBot:
    def __init__(self):
        self.board = chess.Board()
    
    def reset_board(self):
        """Reset the chess board to starting position"""
        self.board = chess.Board()
    
    def update_board(self, fen):
        """Update board state from FEN string"""
        try:
            self.board = chess.Board(fen)
            return True
        except Exception as e:
            print(f"Error updating board: {e}")
            return False
    
    def get_random_move(self):
        """Get a random legal move (placeholder for your RL model)"""
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        move = random.choice(legal_moves)
        return {
            "from": str(move)[:2],
            "to": str(move)[2:4],
            "promotion": str(move)[4:] if len(str(move)) > 4 else None
        }
    
    def get_best_move(self):
        """
        TODO: Replace this with your RL model prediction
        For now, returns a random move
        """
        # This is where you'll integrate your RL model
        # Example:
        # 1. Convert board state to your model's input format
        # 2. Run inference with your trained model
        # 3. Convert model output back to chess move format
        
        return self.get_random_move()

# Initialize the chess bot
bot = ChessBot()

@app.route('/api/move', methods=['POST'])
def handle_move():
    """Handle move requests from the frontend"""
    try:
        data = request.get_json()
        
        # Extract data from frontend
        fen = data.get('fen')
        move_from = data.get('move_from')
        move_to = data.get('move_to')
        promotion = data.get('promotion')
        valid_moves = data.get('valid_moves', [])
        is_check = data.get('is_check', False)
        is_checkmate = data.get('is_checkmate', False)
        is_stalemate = data.get('is_stalemate', False)
        
        print(f"Received move: {move_from} -> {move_to}")
        print(f"Current FEN: {fen}")
        print(f"Game status - Check: {is_check}, Checkmate: {is_checkmate}, Stalemate: {is_stalemate}")
        
        # Update bot's board state
        if not bot.update_board(fen):
            return jsonify({
                "error": "Invalid FEN string",
                "message": "Failed to update board state"
            }), 400
        
        # Check if game is over
        if is_checkmate or is_stalemate:
            return jsonify({
                "message": "Game is over",
                "game_over": True
            })
        
        # Get AI move
        ai_move = bot.get_best_move()
        
        if ai_move is None:
            return jsonify({
                "error": "No legal moves available",
                "message": "AI cannot make a move"
            }), 400
        
        # Apply the AI move to verify it's legal
        try:
            move_str = ai_move["from"] + ai_move["to"]
            if ai_move["promotion"]:
                move_str += ai_move["promotion"]
            
            move = chess.Move.from_uci(move_str)
            if move in bot.board.legal_moves:
                bot.board.push(move)
                
                return jsonify({
                    "next_move": ai_move,
                    "message": "AI move successful",
                    "new_fen": bot.board.fen()
                })
            else:
                print(f"Illegal move generated: {move_str}")
                return jsonify({
                    "error": "Illegal move generated",
                    "message": "AI generated an invalid move"
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
    print("💡 Replace get_best_move() with your RL model!")
    
    app.run(host='0.0.0.0', port=8080, debug=True) 