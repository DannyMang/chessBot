/*
API endpoint handlers

*/

use axum::{extract::State, Json};
use crate::{
    agents::{self, ChessAgent},
    environment::ChessBoard,
    utils::fen::parse_fen,
    utils::notation::{convert_to_chess_js_move, parse_san_moves},
    AppState,
};
use super::types::{MoveRequest, MoveResponse, ChessMove};

// Health check endpoint
pub async fn health_check() -> &'static str {
    "Chess backend is running!"
}

// Process move endpoint
pub async fn process_move(
    State(state): State<AppState>,
    Json(request): Json<MoveRequest>
) -> Json<MoveResponse> {
    // Log the request
    println!("Received move request:");
    println!("  FEN: {}", request.fen);
    println!("  From: {}", request.move_from);
    println!("  To: {}", request.move_to);
    println!("  Agent requested: {:?}", request.agent);
    
    // Increment move counter
    let mut count = state.move_count.lock().unwrap();
    *count += 1;
    println!("Total moves processed: {}", *count);
    
    // Parse the FEN to create a board
    let board = match parse_fen(&request.fen) {
        Ok(board) => board,
        Err(err) => {
            return Json(MoveResponse {
                success: false,
                message: format!("Failed to parse FEN: {}", err),
                next_move: None,
                agent_used: "none".to_string(),
            });
        }
    };
    
    // Create the requested agent (or use default)
    let agent_name = request.agent.as_deref().unwrap_or("minimax");
    let agent = agents::create_agent(agent_name);
    
    // Get the agent's move
    let best_move = agent.select_move(&board);
    
    // If no move is found, try to use the valid moves from chess.js
    let chess_move = match best_move {
        Some(mv) => convert_to_chess_js_move(&mv),
        None => {
            // Fallback to using the valid moves from chess.js
            if !request.valid_moves.is_empty() {
                let moves = parse_san_moves(&request.valid_moves, &board);
                if let Some(mv) = moves.first() {
                    convert_to_chess_js_move(mv)
                } else {
                    return Json(MoveResponse {
                        success: false,
                        message: "No valid moves available".to_string(),
                        next_move: None,
                        agent_used: agent.name().to_string(),
                    });
                }
            } else {
                return Json(MoveResponse {
                    success: false,
                    message: "No valid moves available".to_string(),
                    next_move: None,
                    agent_used: agent.name().to_string(),
                });
            }
        }
    };
    
    Json(MoveResponse {
        success: true,
        message: format!("Move processed successfully ({})", *count),
        next_move: Some(chess_move),
        agent_used: agent.name().to_string(),
    })
}