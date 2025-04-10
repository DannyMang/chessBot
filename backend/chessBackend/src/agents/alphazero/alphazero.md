# alphazero algorithm

3 - parts

MCTS-
Monte Carlo Tree Search 

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