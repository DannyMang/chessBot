from tinygrad.tensor import Tensor
from extra.models.resnet import ResNet, BasicBlock
import tinygrad.nn as nn

class ChessNet:
    def __init__(self, num_moves):
        self.resnet_body = ResNet(BasicBlock, [2, 2, 2, 2], num_classes=1000)
        
        resnet_out_features = 512

        # Policy head
        self.policy_fc = nn.Linear(resnet_out_features, num_moves)
        
        # Value head  
        self.value_fc1 = nn.Linear(resnet_out_features, 256)
        self.value_fc2 = nn.Linear(256, 1)

    def __call__(self, x: Tensor) -> tuple[Tensor, Tensor]:
        # Run the ResNet body (stop before final classification layer)
        x = self.resnet_body.conv1(x)
        x = self.resnet_body.bn1(x)
        x = x.relu()
        x = x.max_pool2d(kernel_size=3, stride=2, padding=1)
        x = self.resnet_body.layer1(x)
        x = self.resnet_body.layer2(x)
        x = self.resnet_body.layer3(x)
        x = self.resnet_body.layer4(x)
        x = self.resnet_body.avgpool(x)
        
        # The output 'x' is now the feature tensor from the ResNet body
        #x dims = [N, 512, 1, 1]
        
        x = x.reshape(x.shape[0], -1)
        #x dims now [N,512]
        
        # Policy Head - outputs move probabilities
        policy = self.policy_conv(x).relu()
        policy = policy.softmax(dim=-1)  # Convert to probabilities

        # Value Head - outputs position evaluation
        value = self.value_conv(x).relu()
        value = self.value_fc2(value).tanh()  # tanh to scale value between -1 and 1

        return policy, value
    
    def predict(self, board_tensor: Tensor) -> tuple[Tensor, float]:
        """
        Predict policy and value for a given board state.
        Used by MCTS for evaluation.
        """
        policy, value = self(board_tensor)
        return policy, value.item()

if __name__ == '__main__':
    # Example of how to use the network
    # 12 bitboards representing piece positions, each 8x8
    fake_board_tensor = Tensor.randn(1, 12, 8, 8) 
    
    model = ChessNet(num_moves=4672)
    policy_output, value_output = model(fake_board_tensor)

    print("Policy output shape:", policy_output.shape)
    print("Value output:", value_output.item())
    print("Policy sum (should be ~1.0):", policy_output.sum().item()) 