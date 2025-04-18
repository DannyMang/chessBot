// impl MCTS

use std::collections::HashMap;
use crate::environment::{ChessBoard, Move, GameState, Color};
use std::rc::Rc;
use std::cell::RefCell;
use burn::tensor::Tensor;
use ndarray::{Array1, Array2};
use rand::distributions::{Dirichlet, Distribution};

#[derive(Debug)]
pub struct DummyNode {
    parent: Option<usize>,
    child_total_value: HashMap<usize, f32>,
    child_total_visits: HashMap<usize, f32>
}

impl DummyNode {
    pub fn new() -> Self {
        Self {
            parent: None,
            child_total_value = HashMap<usize, f32>,
            child_total_visits = HashMap<usize, f32>
        }
    }
}

//UCTNode, Upper Confidence Bound for Trees

pub struct UCTNode {
    game :ChessBoard,
    move_idx : Option<usize>,
    is_expanded : bool,
    // RC(Reference Counted) is a pointer to a UCTNode, allows multiple parts to share ownership to UCTNode
    //RefCell provides interior mutability, allows us to mutate the UCTNode even if it is borrowed, Moves borrow checking from compile time to runtime
    parent : Option<Rc<RefCell<UCTNode>>>,
    children: HashMap<usize, Rc<RefCell<UCTNode>>>,
    child_priors: Array1<f32>,
    child_total_value: Array1<f32>,
    child_number_visits: Array1<f32>,
    action_idxes: Vec<usize>,
}

impl UCTNode{

    pub fn new(game: ChessBoard, move_idx:Option<usize>, parent: Option<Rc<RefCell<UCTNode>>>) -> Self {
        Self{
            game,
            move_idx,
            is_expanded: false,
            parent,
            children: HashMap::new(),
            child_priors: Array1::zeros(4672),
            child_total_value: Array1::zeros(4672),
            child_number_visits: Array1::zeros(4672),
            action_idxes: Vec::new(),
        }
    }

    pub fn new number_visits(&self) -> f32 {
        if let Some(parent) == &self.parent{
            if let Some(move_idx) = self.move_idx {
                return parent.borrow().child_number_visits[move_idx];
            }
        }
    }
    pub fn set_number_visits(&mut self, value: f32) {
        if let Some(parent) = &self.parent {
            if let Some(move_idx) = self.move_idx {
                parent.borrow_mut().child_number_visits[move_idx] = value;
            }
        }
    }

    pub fn total_value(&self) -> f32 {
        if let Some(parent) = &self.parent {
            if let Some(move_idx) = self.move_idx {
                return parent.borrow().child_total_value[move_idx];
            }
        }
        0.0
    }

    pub fn set_total_value(&mut self, value: f32) {
        if let Some(parent) = &self.parent {
            if let Some(move_idx) = self.move_idx {
                parent.borrow_mut().child_total_value[move_idx] = value;
            }
        }
    }

     // mathemtically speaking, UCB is Q + c * sqrt(ln(parent_visits) / child_visits)

    //Q value of the child node
    // exploitation component in the UCB formula
    pub fn child_Q(&mut self) -> f32 {
        &self.child_total_value / (1.0 + &self.child_number_visits)
    }

    //U value of the child node
    // exploration component in the UCB formula
    pub fn child_U(&mut self) -> f32 {
        let sqrt_parent_visits = (self.number_visits() as f32).sqrt();
        sqrt_parent_visit * (&self.child_priors.mapv(f32::abs) / (1.0 + &self.child_number_visits))
    }

    // we then either choose to explore or exploit, choose childQ or childU

    pub fn best_child(&self) -> usize{
        // we check if action_idxes is empty, if it is, we return 0
        if !self.action_idxes.is_empty(){
            let scores = self.child_Q() + self.child_U();
            let mut best_score = f32::NEG_INFINITY;
            let mut best_move = 0;

            // we iterate through the action_idxes and find the best score  
            for &idx in &self.action_idxes {
                if scores[idx] > best_score {
                    best_score = scores[idx];
                    best_move = idx;
                }
            }
            best_move
        } else {
            let scores = self.child_q() + self.child_u();
            scores.argmax().unwrap()
        }
    }

    pub fn select_leaf(&mut self) -> Rc<RefCell<UCTNode>> {
        let mut current = Rc::new(RefCell::new(self.clone()));
        while current.borrow().is_expanded {
            let best_move = current.borrow().best_child();
            current = current.borrow_mut().maybe_add_child(best_move);
        }
        current
    }


   // Add Dirichlet noise to the child priors at the root node
    // Dirichlet noise encourages exploration by perturbing the prior probabilities
    // The formula used is: P'(s,a) = (1-ε) * P(s,a) + ε * Dir(α)
    // Where ε=0.25 and α=0.3 in this implementation
    pub fn add_dirichlet_noise(&mut self, action_idxs: &[usize], mut child_priors: Array1<f32>) -> Array1<f32> {
        // Create Dirichlet noise
        let alpha = vec![0.3; action_idxs.len()];
        let dirichlet = Dirichlet::new(&alpha).unwrap();
        let noise: Vec<f32> = dirichlet.sample(&mut rand::thread_rng());
        
        // Apply noise only to legal moves
        for (i, &idx) in action_idxs.iter().enumerate() {
            child_priors[idx] = 0.75 * child_priors[idx] + 0.25 * noise[i];
        }
        
        child_priors
    }

    // Expands a leaf node by calculating valid actions and assigning probabilities to them.
    pub fn expand(&mut self, priors: Array1<f32>, action_idxes: Vec<usize>) {
       self.is_expanded = true;
       let mut action_idxes = Vec::new();

       //TO -DO....!!!!!!!et_valid_moves does not seem to be implemented in the ChessBoard struct
       for action in self.game.get_valid_moves() {
            let (initial_pos, final_pos, promotion) = match action {
                Move { from, to, special_move } => {
                    (from, to, special_move)
                }
            };
            // TO-DO ENCODE ACTION DOES NOT EXIST, NEED TO MAKE AN ENCODER DECODER HELPER FILE 
            let encoded_action = encode_action(&self.game, initial_pos, final_pos, promotion);
            action_idxs.push(encoded_action);
        }

        if action_idxs.is_empty() {
            self.is_expanded = false;
            return;
        }

        self.action_idxes = action_idxs.clone();

        // Mask illegal actions
        for i in 0..child_priors.len() {
            if !action_idxs.contains(&i) {
                child_priors[i] = 0.0;
            }
        }

        // Add Dirichlet noise at root
        if self.parent.as_ref().map_or(true, |p| p.borrow().parent.is_none()) {
            child_priors = self.add_dirichlet_noise(&action_idxs, child_priors);
        }

        self.child_priors = child_priors;

    }

    
    
}