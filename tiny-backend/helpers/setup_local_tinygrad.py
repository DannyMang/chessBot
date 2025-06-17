#!/usr/bin/env python3
"""
Setup script to use local tinygrad from /Users/danielung/Desktop/projects/tinygrad
"""

import sys
import os

# Add local tinygrad to Python path
# change this to your local tinygrad path if you want to use local tinygrad, otherwise just use pip install tinygrad  
TINYGRAD_PATH = "/Users/danielung/Desktop/projects/tinygrad"

def setup_tinygrad_path():
    """Add local tinygrad to sys.path"""
    if TINYGRAD_PATH not in sys.path:
        sys.path.insert(0, TINYGRAD_PATH)
        print(f"✅ Added tinygrad path: {TINYGRAD_PATH}")
    
    # Verify tinygrad can be imported
    try:
        import tinygrad
        print(f"✅ tinygrad imported successfully from: {tinygrad.__file__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import tinygrad: {e}")
        return False

if __name__ == "__main__":
    success = setup_tinygrad_path()
    if success:
        print("🎉 Local tinygrad setup complete!")
    else:
        print("❌ Setup failed")
        sys.exit(1) 