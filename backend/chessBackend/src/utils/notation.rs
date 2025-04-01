/*

notation utilities

*/

use crate::environment::{ChessBoard, Move, PieceType};
use crate::api::types::ChessMove;

// Convert algebraic notation (e.g., "e2") to coordinates (e.g., (1, 4))
pub fn algebraic_to_coords(square: &str) -> (usize, usize) {
    let chars: Vec<char> = square.chars().collect();
    let file = chars[0] as usize - 'a' as usize;
    let rank = chars[1] as usize - '1' as usize;
    (rank, file)
}

// Convert coordinates to algebraic notation
pub fn coords_to_algebraic(coords: (usize, usize)) -> String {
    let file = (coords.1 as u8 + b'a') as char;
    let rank = (coords.0 as u8 + b'1') as char;
    format!("{}{}", file, rank)
}

// Convert our internal move to chess.js format
pub fn convert_to_chess_js_move(mv: &Move) -> ChessMove {
    // Convert promotion piece
    let promotion = match &mv.special_move {
        Some(crate::environment::SpecialMove::Promotion(piece_type)) => {
            Some(match piece_type {
                PieceType::Queen => "q".to_string(),
                PieceType::Rook => "r".to_string(),
                PieceType::Bishop => "b".to_string(),
                PieceType::Knight => "n".to_string(),
                _ => "q".to_string(), // Default to queen
            })
        },
        _ => None,
    };
    
    ChessMove {
        from: coords_to_algebraic(mv.from),
        to: coords_to_algebraic(mv.to),
        promotion,
    }
}

// Parse SAN moves from chess.js into our internal format
pub fn parse_san_moves(san_moves: &[String], board: &ChessBoard) -> Vec<Move> {
    // This would be a full SAN parser
    // For now, just return an empty vector
    Vec::new()
}

