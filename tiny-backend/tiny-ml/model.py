from tinygrad.tensor import Tensor
from extra.models.resnet import ResNet, BasicBlock
import tinygrad.nn as nn

class ChessNet:
    def __init__(self, num_moves:int):
       self.resnet_body = ResNet(num_classes=1000)
       
       #policy head
       self.policy.head = nn.Conv2d(512, 2, kernel_size=1)
       self.policy_fc  = nn.Linear(128, num_moves)
       
       #value head
       self.value_conv = nn.Conv2d(512, 1, kernel_size=1)
       self.value_fc = nn.Linear(64,256)
       self.value_fc2 = nn.Linear(256,1)

    def __call__(self, x: Tensor) -> tuple[Tensor, Tensor]:
        # Run the ResNet body
        # We need to replicate the ResNet's forward pass, but stop before the fc layer
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

        # Policy Head
        policy = self.policy_conv(x).relu()
        policy = self.policy_fc(policy.reshape(policy.shape[0], -1))

        # Value Head
        value = self.value_conv(x).relu()
        value = self.value_fc1(value.reshape(value.shape[0], -1)).relu()
        value = self.value_fc2(value).tanh() # tanh to scale value between -1 and 1

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