use axum::{
    routing::{get, post},
    http::{HeaderValue, Method},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};

// Import your chess environment (adjust the path as needed)
mod environment;
use environment::ChessEnv;

#[tokio::main]
async fn main() {
    // Set up CORS to allow requests from your frontend
    let cors = CorsLayer::new()
        .allow_origin("http://localhost:3000".parse::<HeaderValue>().unwrap())
        .allow_methods([Method::GET, Method::POST])
        .allow_headers(Any);

    // Create the router with our routes
    let app = Router::new()
        .route("/", get(health_check))
        .route("/api/move", post(process_move))
        .layer(cors);

    // Set the server address
    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    println!("Server running on http://{}", addr);

    // Start the server
    axum::Server::bind(&addr)
        .serve(app.into_make_service())
        .await
        .unwrap();
}

// Simple health check endpoint
async fn health_check() -> &'static str {
    "Chess backend is running!"
}

// Types for our API
#[derive(Deserialize)]
struct MoveRequest {
    fen: String,
    move_from: String,
    move_to: String,
    promotion: Option<String>,
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
async fn process_move(Json(request): Json<MoveRequest>) -> Json<MoveResponse> {
    println!("Received move: {} to {}", request.move_from, request.move_to);
    
    // Here you would normally:
    // 1. Update your chess environment with the move
    // 2. Run your RL algorithm to get the next move
    // 3. Return the AI's move
    
    // For now, just return a dummy response
    Json(MoveResponse {
        success: true,
        message: "Move processed successfully".to_string(),
        next_move: Some(ChessMove {
            from: "e7".to_string(),
            to: "e5".to_string(),
            promotion: None,
        }),
    })
} 