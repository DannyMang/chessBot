# Chess Bot Tiny Backend

using tinygrad to write this chess engine

## Quick Start

to -do later

## API Endpoints, helpful stuff

### `POST /api/move`
Receives chess moves from frontend and returns AI move.

**Request:**
```json
{
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "move_from": "e2",
  "move_to": "e4",
  "promotion": null,
  "valid_moves": ["a3", "a4", "b3", ...],
  "is_check": false,
  "is_checkmate": false,
  "is_stalemate": false
}
```

**Response:**
```json
{
  "next_move": {
    "from": "e7",
    "to": "e5",
    "promotion": null
  },
  "message": "AI move successful",
  "new_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2"
}
```

### `GET /api/status`
Get server status and current board state.

### `POST /api/reset`
Reset the game to starting position.

## Integrating Your RL Model

Replace the `get_best_move()` method in the `ChessBot` class:

```python
def get_best_move(self):
    """
    Replace this with your RL model prediction
    """
    # 1. Convert self.board to your model's input format
    board_tensor = self.board_to_tensor(self.board)
    
    # 2. Run inference with your trained model
    move_probs = self.model.predict(board_tensor)
    
    # 3. Convert model output back to chess move format
    best_move = self.tensor_to_move(move_probs)
    
    return {
        "from": best_move.from_square,
        "to": best_move.to_square,
        "promotion": best_move.promotion
    }
```
