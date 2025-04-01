/*

traits for the agents

*/
use crate::environment::(ChessBoard, Move);

pub trait ChessAgent{
    //name of agent
    fn name(&self) -> &str;

    // select the best move from the current board position 
    fn select_move(&self, board: &ChessBoard) -> Option<Move>;


    fn train(&mut self, _board: &ChessBoard, _result: f32) -> () {
        //default no training
    }
}
