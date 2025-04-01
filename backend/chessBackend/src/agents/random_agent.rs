use rand::seq::SliceRandom;
use crate::environment::{ChessBoard, Move};
use super::agent_trait::ChessAgent;

pub struct RandomAgent {
    name: String,
}

impl RandomAgent {
    pub fn new() -> Self {
        Self {
            name: "Random".to_string(),
        }
    }
}

impl ChessAgent for RandomAgent {
    fn name(&self) -> &str {
        &self.name
    }
    
    fn select_move(&self, board: &ChessBoard) -> Option<Move> {
        let legal_moves = board.generate_legal_moves();
        let mut rng = rand::thread_rng();
        legal_moves.choose(&mut rng).cloned()
    }
} 