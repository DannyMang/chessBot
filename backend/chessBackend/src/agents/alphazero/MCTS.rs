// impl MCTS

use std::collections::HashMap;
use crate::environment::{ChessBoard, Move, GameState, Color};
use std::rc::Rc;
use std::cell::RefCell;
use burn::tensor::Tensor;
use ndarray::{Array1, Array2};


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
    is_terminal : bool,
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
}