/*
Request/response types
*/

    use serde::{Deserialize, Serialize};

#[derive(Deserialize, Debug)]
pub struct MoveRequest {
    pub fen: String,
    pub move_from: String,
    pub move_to: String,
    pub promotion: Option<String>,
    pub valid_moves: Vec<String>,
    pub is_check: bool,
    pub is_checkmate: bool,
    pub is_stalemate: bool,
    pub agent: Option<String>, // Which agent to use
}

#[derive(Serialize)]
pub struct MoveResponse {
    pub success: bool,
    pub message: String,
    pub next_move: Option<ChessMove>,
    pub agent_used: String,
}

#[derive(Serialize)]
pub struct ChessMove {
    pub from: String,
    pub to: String,
    pub promotion: Option<String>,
}
