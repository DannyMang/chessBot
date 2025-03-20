/*

Implement a chess environment that:
Maintains game state
Processes actions
Computes rewards
Determines terminal states

*/

use burn::prelude::*;


pub enum PieceType {
    Pawn,
    Knight,
    Bishop,
    Rook,
    Queen,
    King,
}

pub enum Color{
    White,
    Black,
}

pub struct Piece{
    pub piece_type: PieceType,
    pub color: Color,
}

pub enum SpecialMove{
    Castle,
    EnPassant,
    Promotion,
}

pub enum CastleSide {
    Kingside,
    Queenside,
}

pub struct Move{
    pub from: (usize, usize),
    pub to: (usize, usize),
    pub special_move: Option<SpecialMove>,
}

pub enum GameState {
    InProgress,
    Check(Color),
    Checkmate(Color),
    Stalemate,
    Draw,
}

// The main chess board representation
pub struct ChessBoard {
    pub squares: [[Option<Piece>; 8]; 8],
    pub current_turn: Color,
    pub state: GameState,
    pub moves: Vec<Move>,
    pub castling_rights: CastlingRights,
    pub en_passant_target: Option<(usize, usize)>,
    pub halfmove_clock: u32,  // For 50-move rule
    pub fullmove_number: u32,
}

pub struct CastlingRights {
    pub white_kingside: bool,
    pub white_queenside: bool,
    pub black_kingside: bool,
    pub black_queenside: bool,
}

pub struct ChessEnv{
    board: ChessBoard,
   //ub reward_scale:f32,

}


impl struct ChessEnv{
    pub fn new() -> Self{
        let board = ChessBoard::new();
        Self{
            board,
            reward_scale: 1.0,
        }
    }

    pub fn reset(&mut self){
        self.board = ChessBoard::new();
    }

    pub fn step(&mut self, action: Move) -> (f32, GameState, bool){
      // to do for tmr
        
        
    }
}

impl ChessBoard{

    // to do for tmr
}




