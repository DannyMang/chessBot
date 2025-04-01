mod agent_trait;
mod minimax_agent;
mod random_agent;
mod rl_agent;

pub use agent_trait::ChessAgent;
pub use minimax_agent::MinimaxAgent;
pub use random_agent::RandomAgent;
pub use rl_agent::RLAgent;

// Factory function to create agents by name
pub fn create_agent(name: &str) -> Box<dyn ChessAgent> {
    match name {
        "random" => Box::new(RandomAgent::new()),
        "minimax" => Box::new(MinimaxAgent::new(3)), // Default depth
        "minimax-1" => Box::new(MinimaxAgent::new(1)),
        "minimax-3" => Box::new(MinimaxAgent::new(3)),
        "minimax-5" => Box::new(MinimaxAgent::new(5)),
        "rl-basic" => Box::new(RLAgent::new("basic")),
        _ => Box::new(RandomAgent::new()), // Default to random
    }
} 