#!/usr/bin/env python3
"""
Test script to verify local tinygrad is working
"""

import sys
import os

# Add your local tinygrad to Python path
TINYGRAD_PATH = "/Users/danielung/Desktop/projects/tinygrad"
sys.path.insert(0, TINYGRAD_PATH)

def test_tinygrad():
    """Test that we can import and use local tinygrad"""
    print("🧪 Testing local tinygrad...")
    
    try:
        # Import tinygrad
        import tinygrad
        from tinygrad import Tensor, dtypes
        
        print(f"✅ tinygrad imported from: {tinygrad.__file__}")
        print(f"✅ tinygrad version info: {getattr(tinygrad, '__version__', 'unknown')}")
        
        # Test basic tensor operations
        print("\n🔬 Testing tensor operations...")
        x = Tensor([[1.0, 2.0], [3.0, 4.0]], dtype=dtypes.float32)
        y = x + 1
        result = y.numpy()
        
        print(f"✅ Tensor creation: {x.shape}")
        print(f"✅ Tensor math: {result}")
        
        # Test neural network components
        print("\n🧠 Testing neural network components...")
        from tinygrad import nn
        
        # Simple conv layer test
        conv = nn.Conv2d(3, 16, 3)
        test_input = Tensor.randn(1, 3, 8, 8)
        output = conv(test_input)
        
        print(f"✅ Conv2d: {test_input.shape} → {output.shape}")
        
        print("\n🎉 All tests passed! Your local tinygrad is working perfectly.")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import tinygrad: {e}")
        print("Make sure the path is correct and tinygrad is properly installed there.")
        return False
    except Exception as e:
        print(f"❌ Error testing tinygrad: {e}")
        return False

if __name__ == "__main__":
    success = test_tinygrad()
    if success:
        print("\n🚀 Ready to build chess AI with your local tinygrad!")
    else:
        print("\n❌ Please fix the tinygrad setup first.")
        sys.exit(1) 