from tinygrad import Tensor, TinyJit
from tinygrad.nn import Conv2d, Linear
from extra.models.resnet import ResNet

class ChessNet:
    """
    A ResNet-based neural network for chess, inspired by AlphaZero.
    It has a common ResNet body and two heads:
    1. Policy Head: Outputs move probabilities.
    2. Value Head: Outputs a single value evaluating the position [-1, 1].
    """
    def __init__(self, num_moves=4672):
        self.resnet_body = ResNet(18) #resnet-18
        #(1, 12, 8, 8) → (1, 64, 8, 8)
        #self.resnet_body.conv1 = Conv2d(12, 64, kernel_size=3, stride=1, padding=1, bias=False)
        
        #  2 previous board states + a color plane. 12 pieces * 2 states + 1 color = 25 channels.
        self.resnet_body.conv1 = Conv2d(25, 64, kernel_size=3, stride=1, padding=1, bias=False)
        self.resnet_body.fc = None
        resnet_out_features = 512 * self.resnet_body.block.expansion

        # Policy Head 
        # Input: (batch_size, 512) - Output: (batch_size, num_moves)
        self.policy_fc = Linear(resnet_out_features, num_moves)
        
        # Value Head 
        # Input: (batch_size, 512) - Output: (batch_size, 256)
        self.value_fc1 = Linear(resnet_out_features, 256)
        # Input: (batch_size, 256) - Output: (batch_size, 1)
        self.value_fc2 = Linear(256, 1)

    def _forward_resnet_body(self, x: Tensor) -> Tensor:
        x = self.resnet_body.bn1(self.resnet_body.conv1(x)).relu()
        x = x.sequential(self.resnet_body.layer1)
        x = x.sequential(self.resnet_body.layer2)
        x = x.sequential(self.resnet_body.layer3)
        x = x.sequential(self.resnet_body.layer4)
        x = x.mean((2,3)) 
        return x

    @TinyJit
    def __call__(self, x: Tensor) -> tuple[Tensor, Tensor]:
        features = self._forward_resnet_body(x)
        policy = self.policy_fc(features)
        value = self.value_fc1(features).relu()
        value = self.value_fc2(value).tanh()
        return policy, value
    
    def predict(self, board_tensor: Tensor) -> tuple[Tensor, float]:
        with Tensor.train(False):
            policy_logits, value = self(board_tensor)
            return policy_logits.softmax(), value.item()

if __name__ == '__main__':
    fake_board_tensor = Tensor.randn(1, 25, 8, 8) 
    model = ChessNet(num_moves=4672)
    
    policy_output, value_output = model.predict(fake_board_tensor)

    print("Policy output shape:", policy_output.shape)
    print("Value output:", value_output)
    print("Policy sum (should be ~1.0):", policy_output.sum().item())