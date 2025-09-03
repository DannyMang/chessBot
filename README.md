chess bot using burn deep learning framework

-progress as out 7/1
- model is still being built out


after model is built out 
- after training 
- will see performance 



to-do:

- how to measure perforamcne of model? 
from ai(explore more later)
The Sequential Probability Ratio Test (SPRT) has become the preferred method for engine testing, providing early termination when statistical significance is reached while maintaining 95% confidence levels. ChessprogrammingChessprogramming
CCRL (Computer Chess Rating Lists) and CEGT (Chess Engines Grand Tournament) provide standardized evaluation protocols that should guide your testing approach. Chessprogramming +4 Key evaluation parameters include:

Time controls: 40/15 (40 moves in 15 minutes) for rapid assessment, 40/120 for thorough evaluation Wikipedia
Opening books: Standardized books like 8moves_v3.pgn to ensure fair comparison
Adjudication rules: Draw detection at ≤8 centipawns for 4+ moves, resignation at ≤-500 centipawns


- training on https://app.primeintellect.ai/dashboard/create-cluster?image=ubuntu_22_cuda_12&location=Cheapest&security=Cheapest&show_spot=true

=> calculate price 0of training

- integrate w/ weights and biases to track hyperparameters
- 
