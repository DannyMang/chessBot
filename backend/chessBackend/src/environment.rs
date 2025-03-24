/*

Implement a chess environment that:
Maintains game state
Processes actions
Computes rewards
Determines terminal states

*/

use burn::tensor::Tensor;
use burn::backend::wgpu::Wgpu;

#[derive(Clone)]
pub enum PieceType {
    Pawn,
    Knight,
    Bishop,
    Rook,
    Queen,
    King,
}

#[derive(Clone)]
pub enum Color{
    White,
    Black,
}

#[derive(Clone, Copy)]
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
#[derive(Clone)]
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
}

impl ChessEnv{
    pub fn new() -> Self{
        let board = ChessBoard::new();
        Self{
            board,
        }
    }

    pub fn reset(&mut self){
        self.board = ChessBoard::new();
    }

    pub fn step(&mut self, action: Move) -> (GameState, GameState, bool) {
        let valid = self.board.is_valid_move(&action);

        if !valid {
            return (self.board.state.clone(), self.board.state.clone(), false);
        }
        
        // Calculate reward based on the new state
        let _reward = self.calculate_reward();
        
        // Check if the game is done
        let done = match self.board.state {
            GameState::InProgress | GameState::Check(_) => false,
            _ => true,
        };
        
        (self.board.state.clone(), self.board.state.clone(), done)
    }

    fn calculate_reward(&self) -> f32{
        // not sure how to calculate reward yet
        return 0.0;
    }

    pub fn get_observation(&self) -> Tensor<Wgpu, 2> {
        let device = Default::default();
        Tensor::<Wgpu, 2>::zeros([8, 8], &device)
    }

}

impl ChessBoard{
    pub fn new() -> Self {
        // Initialize a standard chess board
        let mut board = Self {
            squares: [[None; 8]; 8],
            current_turn: Color::White,
            state: GameState::InProgress,
            moves: Vec::new(),
            castling_rights: CastlingRights {
                white_kingside: true,
                white_queenside: true,
                black_kingside: true,
                black_queenside: true,
            },
            en_passant_target: None,
            halfmove_clock: 0,
            fullmove_number: 1,
        };
        
        // Set up the pieces
        board.setup_pieces();
        board
    }

    pub fn setup_pieces(&mut self){
        // Place pawns
        for i in 0..8 {
            self.squares[1][i] = Some(Piece { piece_type: PieceType::Pawn, color: Color::White });
            self.squares[6][i] = Some(Piece { piece_type: PieceType::Pawn, color: Color::Black });
        }
    
        // Place rooks
        self.squares[0][0] = Some(Piece { piece_type: PieceType::Rook, color: Color::White });
        self.squares[0][7] = Some(Piece { piece_type: PieceType::Rook, color: Color::White });
        self.squares[7][0] = Some(Piece { piece_type: PieceType::Rook, color: Color::Black });
        self.squares[7][7] = Some(Piece { piece_type: PieceType::Rook, color: Color::Black });
    
        // Place knights
        self.squares[0][1] = Some(Piece { piece_type: PieceType::Knight, color: Color::White });
        self.squares[0][6] = Some(Piece { piece_type: PieceType::Knight, color: Color::White });
        self.squares[7][1] = Some(Piece { piece_type: PieceType::Knight, color: Color::Black });
        self.squares[7][6] = Some(Piece { piece_type: PieceType::Knight, color: Color::Black });
    
        // Place bishops
        self.squares[0][2] = Some(Piece { piece_type: PieceType::Bishop, color: Color::White });
        self.squares[0][5] = Some(Piece { piece_type: PieceType::Bishop, color: Color::White });
        self.squares[7][2] = Some(Piece { piece_type: PieceType::Bishop, color: Color::Black });
        self.squares[7][5] = Some(Piece { piece_type: PieceType::Bishop, color: Color::Black });
    
        // Place queens
        self.squares[0][3] = Some(Piece { piece_type: PieceType::Queen, color: Color::White });
        self.squares[7][3] = Some(Piece { piece_type: PieceType::Queen, color: Color::Black });
    
        // Place kings
        self.squares[0][4] = Some(Piece { piece_type: PieceType::King, color: Color::White });
        self.squares[7][4] = Some(Piece { piece_type: PieceType::King, color: Color::Black });
    }

    pub fn make_move(&mut self, mv: Move) -> bool {
        // Validate and execute the move
        if !self.is_valid_move(&mv) {
            return false;
        }
        
        // Execute the move
        // ... (implement move execution)
        
        // Update game state
        self.update_game_state();
        
        // Add to move history
        self.moves.push(mv);
        
        // Switch turns
        self.current_turn = match self.current_turn {
            Color::White => Color::Black,
            Color::Black => Color::White,
        };
        
        true
    }
    
    fn is_valid_move(&self, _mv: &Move) -> bool {
        // Implementation here
        true  // or your actual implementation
    }
    
    fn update_game_state(&mut self) {
        // Check for check, checkmate, stalemate, etc.
        todo!("Implement game state update")
    }
    
    // to do for tmr
}




