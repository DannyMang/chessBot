    use burn::{
        nn::{
            conv::{Conv2d, Conv2dConfig},
            pool::{AdaptiveAvgPool2d, AdaptiveAvgPool2dConfig},
            Dropout, DropoutConfig, Linear, LinearConfig, Relu, LogSoftmax, BatchNorm2d, BatchNorm2dConfig,

        },
        prelude::*,
    };

// alphanet 

#[derive(Module, Debug)]
pub struct ConvBlock<B: Backend> {
    conv1: Conv2d<B>,
    bn1: BatchNorm2d<B>,
}

impl<B: Backend> ConvBlock<B> {
    pub fn new() -> Self {
        let conv1 = Conv2dConfig::new(22, 256, [3, 3])
            .with_stride([1, 1])
            .with_padding([1, 1])
            .init();

        let bn1 = BatchNorm2dConfig::new(256).init();

        Self { conv1, bn1 }
    }

    pub fn forward(&self, s: Tensor<B, 4>) -> Tensor<B, 4> {
        let s = s.reshape([-1, 22, 8, 8]); // batch_size x channels x board_x x board_y
        let s = self.conv1.forward(s);
        let s = self.bn1.forward(s);
        s.relu()
    }
}


#[derive(Module, Debug)]
pub struct ResBlock<B: Backend> {
    conv1: Conv2d<B>,
    bn1: BatchNorm2d<B>,
    conv2: Conv2d<B>,
    bn2: BatchNorm2d<B>,
}

impl<B: Backend> ResBlock<B> {
    pub fn new(inplanes: usize, planes : usize, stride : usize) -> Self (
        let conv1 = Conv2d::new(Conv2dConfig (inplanes, planes, [3,3]))
            .with_stride([stride, stride])
            .with_padding([1,1])
            .with_bias(false);
            .init();

        let bn1 = BatchNorm2d::new(BatchNorm2dConfig::new(planes));
        let conv2 = Conv2d::new(Conv2dConfig (planes, planes, [3,3]))
            .with_stride([stride, stride])
            .with_padding([1,1])
            .with_bias(false);
            .init();

        let bn2 = BatchNorm2d::new(BatchNorm2dConfig::new(planes));

        Self {conv1, bn1, conv2, bn2}
    )

    //forward pass
    pub fn forward(&self, x:Tensor<B, 4>) -> Tensor<B, 4> {
        let residual = x;
        let out = self.conv1.forward(x);
        let out = self.bn1.forward(out).relu();
        let out = self.conv2.forward(x);
        let out = self.bn2.forward(out);
        let out = out + residual;
        let out = out.relu();
        return out
    }
}


#[derive(Module, Debug)]
pub struct OutBlock<B: Backend> {
    conv: Conv2d<B>,
    bn: BatchNorm2d<B>,
    fc1: Linear<B>,
    fc2: Linear<B>,
    conv1: Conv2d<B>,
    bn1: BatchNorm2d<B>,
    logsoftmax: LogSoftmax<B>,
    bn2: BatchNorm2d<B>,
}


impl<B: Backend> OutBlock<B> {
    pub fn new() -> Self (
        let conv = Conv2d::new(256, 1 , [1,1]).init(); //value heads
        let bn = BatchNorm2d::new(1).init();
        let fc1 = Linear::new(8 * 8, 64).init();
        let fc2 = Linear::new(64, 1).init();

        let conv1 = Conv2d::new(256, 1, [1,1]).init();// policy head
        let bn1 = BatchNorm2d::new(128).init();
        let logsoftmax = LogSoftmax::new(1).init();
        let bn2 = BatchNorm2d::new(1).init();
    )

    pub fn forward(&self, s:Tensor<B, 4>) -> Tensor<B, 4> {
        let v = self.conv.forward(s.clone()).relu();
        let v = self.bn.forward(v);
        let v = v.reshape([-1, 8*8]);
        let v = self.fc1.forward(v).relu();
        let v = self.fc2.forward(v).tanh();

        let p = self.conv1.forward(s).relu();
        let p = self.bn1.forward(p);
        let p = p.reshape([-1, 8 * 8 * 128]);
        let p = self.fc.forward(p);
        let p = p.log_softmax(1).exp();

        (p, v)
    }

}

#[derive(Module, Debug)]
pub struct ChessNet<B: Backend> {
    conv: ConvBlock<B>,
    res_blocks : Vec<ResBlock<B>>,
    out_block : OutBlock<B>,
}

impl<B: Backend> ChessNet<B> {
    pub fn new() -> Self {
        let conv = ConvBlock::new();
        let res_blocks = (0..19).map(|_| ResBlock::new(256, 256, 1)).collect();
        let outblock = OutBlock::new();

        Self {conv, res_blocks, out_block}
    }

    pub fn forward(&self, x:Tensor<B, 4>) -> Tensor<B, 4> {
        let mut x = self.conv.forward(x);
        for block in self.res_blocks.iter() {
            x = block.forward(x);
        }
        self.outblock.forward(s)
    }
}

#[derive(Module, Debug)]
pub struct AlphaLoss<B: Backend> {
    pub fn new() -> Self {
        Self {}
    }

    pub fn forward(
        &self,
        y_value: Tensor<B, 2>,
        value: Tensor<B, 2>,
        y_policy: Tensor<B, 2>,
        policy: Tensor<B, 2>,
    ) -> Tensor<B, 0> {
        let value_error = (value - y_value).powi(2);
        let policy_error = (-policy * (y_policy + 1e-6).log()).sum_dim(1);
        (value_error.flatten() + policy_error).mean()
    }


}








