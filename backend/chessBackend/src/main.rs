use axum::{
    routing::{get, post},
    http::{HeaderValue, Method},
    Router,
};
use std::{net::SocketAddr, sync::{Arc, Mutex}};
use tower_http::cors::{Any, CorsLayer};

// Import modules
mod environment;
mod agents;
mod utils;
mod api;

use api::handlers;
use api::types::*;

#[derive(Clone)]
pub struct AppState {
    move_count: Arc<Mutex<u32>>,
}

#[tokio::main]
async fn main() {
    // Set up CORS
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods([Method::GET, Method::POST])
        .allow_headers(Any);

    // Create shared state
    let app_state = AppState {
        move_count: Arc::new(Mutex::new(0)),
    };

    // Create the router
    let app = Router::new()
        .route("/", get(handlers::health_check))
        .route("/api/move", post(handlers::process_move))
        .with_state(app_state)
        .layer(cors);

    // Set the server address
    let addr = SocketAddr::from(([127, 0, 0, 1], 8080));
    println!("Server running on http://{}", addr);

    // Start the server
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}