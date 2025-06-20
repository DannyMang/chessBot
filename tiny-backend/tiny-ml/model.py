from tinygrad.tensor import Tensor
import tinygrad.nn as nn

class ChessNet:
    def __init__(self):
        # Your network architecture will go here.
        # This is based on the AlphaZero-style architecture described in the README.
        # For now, it's a placeholder.
        self.conv1 = nn.Conv2d(12, 256, 3, padding=1) # 12 bitboards (6 pieces, 2 colors)
        self.bn1 = nn.BatchNorm2d(256)
        
        # ... more layers (e.g., residual blocks) ...

        # Policy head: predicts move probabilities
        self.policy_head = nn.Linear(256 * 8 * 8, 4672) # Output for all possible moves

        # Value head: evaluates the position
        self.value_head = nn.Linear(256 * 8 * 8, 1)

    def __call__(self, x: Tensor) -> tuple[Tensor, Tensor]:
        x = self.bn1(self.conv1(x)).relu()
        
        # Flatten for the final layers
        x_flat = x.reshape(x.shape[0], -1)

        policy = self.policy_head(x_flat)
        value = self.value_head(x_flat).tanh() # Value is between -1 and 1

        return policy, value

if __name__ == '__main__':
    # Example of how to use the network
    # You will get the bitboards from your C++ engine
    # For now, let's use a random tensor to simulate board state
    
    # 12 bitboards, each 8x8
    fake_board_tensor = Tensor.randn(1, 12, 8, 8) 
    
    model = ChessNet()
    policy_output, value_output = model(fake_board_tensor)

    print("Policy output shape:", policy_output.shape)
    print("Value output:", value_output.item()) 