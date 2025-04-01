use std::cmp;
use crate::environment::{ChessBoard, Move, Color, GameState};
use super::agent_trait::ChessAgent;

pub struct MinimaxAgent {
    depth: i32,
    name: String,
}

impl MinimaxAgent {
    pub fn new(depth: i32) -> Self {
        Self {
            depth,
            name: format!("Minimax(depth={})", depth),
        }
    }
    
    fn evaluate(&self, board: &ChessBoard) -> i32 {
        // Simple material evaluation
        board.evaluate()
    }
    
    fn minimax(&self, board: &ChessBoard, depth: i32, alpha: i32, beta: i32, maximizing: bool) -> i32 {
        if depth == 0 {
            return self.evaluate(board);
        }
        
        let legal_moves = board.generate_legal_moves();
        
        if legal_moves.is_empty() {
            // Handle terminal states
            return match &board.state {
                GameState::Checkmate(Color::White) => -10000,
                GameState::Checkmate(Color::Black) => 10000,
                GameState::Stalemate | GameState::Draw => 0,
                _ => self.evaluate(board),
            };
        }
        
        if maximizing {
            let mut max_eval = i32::MIN;
            for mv in legal_moves {
                let mut new_board = board.clone();
                new_board.make_move(mv);
                let eval = self.minimax(&new_board, depth - 1, alpha, beta, false);
                max_eval = cmp::max(max_eval, eval);
                let alpha = cmp::max(alpha, eval);
                if beta <= alpha {
                    break; // Beta cutoff
                }
            }
            max_eval
        } else {
            let mut min_eval = i32::MAX;
            for mv in legal_moves {
                let mut new_board = board.clone();
                new_board.make_move(mv);
                let eval = self.minimax(&new_board, depth - 1, alpha, beta, true);
                min_eval = cmp::min(min_eval, eval);
                let beta = cmp::min(beta, eval);
                if beta <= alpha {
                    break; // Alpha cutoff
                }
            }
            min_eval
        }
    }
}

impl ChessAgent for MinimaxAgent {
    fn name(&self) -> &str {
        &self.name
    }
    
    fn select_move(&self, board: &ChessBoard) -> Option<Move> {
        let legal_moves = board.generate_legal_moves();
        if legal_moves.is_empty() {
            return None;
        }
        
        let is_maximizing = matches!(board.current_turn, Color::White);
        let mut best_move = None;
        let mut best_value = if is_maximizing { i32::MIN } else { i32::MAX };
        
        for mv in legal_moves {
            let mut new_board = board.clone();
            new_board.make_move(mv.clone());
            let value = self.minimax(&new_board, self.depth - 1, i32::MIN, i32::MAX, !is_maximizing);
            
            if (is_maximizing && value > best_value) || (!is_maximizing && value < best_value) {
                best_value = value;
                best_move = Some(mv);
            }
        }
        
        best_move
    }
} 