# alphazero algorithm

3 - parts
MCTS-Monte Carlo Tree Search 
- The policy neural network

- build a tree based on states

- Root node contains initial state ( empty board for tic tac toe, etc)

Each node stores :
- state,W ( total # of FUTURE wins we see when we get to this node), and variable n ( # visit count)
- actions decide what the next state is 
 

 How do you build the tree?
4 Phases
1. Selection ( Walk down until leaf node)
2. Expansion (Create new Node)
3. Simulation (Play randomly)
4. Backpropagation


1) Selection
How is a decision made?
-> Choose child with highest UCB ( Upper Confidence Bound)
-> Basically choose child that tends to win more + choose child that has not been chosen as often (Exploration)


w_i/n_i + c * sqrt((ln(N_i))/ni)  where c is an exploration parameter, bigger c is, the more the model will explore

w_i/n_i = winning ratio

 c * sqrt((ln(N_i))/ni) = choosing node that is less freq visited


 2) Expansions
 - Create new node with w= 0 and ni = 0.

 3) Simulation
 - Play randomly into the future 
 - Check win/loss, use for backprop

 4) Backprop
 - update # wins + visits for each node


 How does it apply to AlphaZero?

 Alpha MCTS

 - Two Key changes
    - Implement policy from the model into search process
    - updated UCB function

- We perform selection, expansion + backprop but no simulation for AMCTS

- updated UCB function

w_i/n_i + p_i *c * sqrt((ln(N_i)) /1+n)  where c is a param

w_i/n_i is the winning ratio for node i (value estimate from experience)
p_i is the prior probability of selecting this move according to the neural network
c is an exploration parameter
N_i is the total number of visits to the parent node
n_i is the number of visits to this specific node


from neural network, we feed state => outputs policy p + value v
f(s_n) = (p,v)


Self-Play

Players alternate turns, each turn, MCTS computes next move.

After an episode, we want to store (state,mcts distribution, and reward) tuples to training data

Training?

s, pi , z = Sample 

f_theta(s) = (p,v) => output from model

minimize loss function = (z-v)^2 - pi^T log(p) + c||theta||^2

 (z-v)^2  MSE 
 pi^T log(p) + c||theta||^2  Multi-Target Cross-Entropy loss




