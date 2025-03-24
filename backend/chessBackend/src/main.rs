use axum::{
    routing::{get, post},
    http::{HeaderValue, Method},
    Json, Router,
    extract::State,
};
use serde::{Deserialize, Serialize};
use std::{net::SocketAddr, sync::{Arc, Mutex}};
use tower_http::cors::{Any, CorsLayer};

// For debugging purposes
use std::fmt::Debug;

// Import your chess environment (adjust the path as needed)
// mod environment;

#[tokio::main]
async fn main() {
    // Set up CORS to allow requests from your frontend
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods([Method::GET, Method::POST])
        .allow_headers(Any);

    // Create shared state for tracking games
    let app_state = AppState {
        move_count: Arc::new(Mutex::new(0)),
    };

    // Create the router with our routes
    let app = Router::new()
        .route("/", get(health_check))
        .route("/api/move", post(process_move))
        .with_state(app_state)
        .layer(cors);

    // Set the server address
    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    println!("Server running on http://{}", addr);

    // Start the server
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

// Application state
#[derive(Clone)]
struct AppState {
    move_count: Arc<Mutex<u32>>,
}

// Simple health check endpoint
async fn health_check() -> &'static str {
    "Chess backend is running!"
}

// Types for our API
#[derive(Deserialize, Debug)]
struct MoveRequest {
    fen: String,
    move_from: String,
    move_to: String,
    promotion: Option<String>,
    valid_moves: Vec<String>,
    is_check: bool,
    is_checkmate: bool,
    is_stalemate: bool,
}

#[derive(Serialize)]
struct MoveResponse {
    success: bool,
    message: String,
    next_move: Option<ChessMove>,
}

#[derive(Serialize)]
struct ChessMove {
    from: String,
    to: String,
    promotion: Option<String>,
}

// Endpoint to process a move and return a response
async fn process_move(
    State(state): State<AppState>,
    Json(request): Json<MoveRequest>
) -> Json<MoveResponse> {
    // Print the received data
    println!("Received move request:");
    println!("  FEN: {}", request.fen);
    println!("  From: {}", request.move_from);
    println!("  To: {}", request.move_to);
    println!("  Promotion: {:?}", request.promotion);
    println!("  Valid moves: {:?}", request.valid_moves);
    println!("  Is check: {}", request.is_check);
    println!("  Is checkmate: {}", request.is_checkmate);
    println!("  Is stalemate: {}", request.is_stalemate);
    
    // Increment move counter
    let mut count = state.move_count.lock().unwrap();
    *count += 1;
    println!("Total moves processed: {}", *count);
    
    // Here you would normally:
    // 1. Update your chess environment with the move
    // 2. Run your RL algorithm to get the next move
    // 3. Return the AI's move
    
    // For now, respond with a simple predetermined move
    // In a real implementation, you would calculate this based on the current board state
    let ai_move = determine_next_move(&request);
    
    Json(MoveResponse {
        success: true,
        message: format!("Move processed successfully ({})", *count),
        next_move: Some(ai_move),
    })
}

// Simple function to determine the next move 
// This is a placeholder for your actual AI/RL algorithm
fn determine_next_move(request: &MoveRequest) -> ChessMove {
    // This is just a dummy implementation
    // In reality, you would use your chess engine/RL model here
    
    // For testing, just make a different move based on the board state
    // This is not a real chess AI, just a demo response
    if request.fen.contains("e2e4") {
        ChessMove {
            from: "e7".to_string(),
            to: "e5".to_string(),
            promotion: None,
        }
    } else if request.fen.contains("d2d4") {
        ChessMove {
            from: "d7".to_string(),
            to: "d5".to_string(),
            promotion: None,
        }
    } else {
        // Default response
        ChessMove {
            from: "e7".to_string(),
            to: "e5".to_string(),
            promotion: None,
        }
    }
}