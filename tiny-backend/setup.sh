#!/bin/bash

echo "🚀 Setting up Chess Bot Backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "1. cd tiny-backend"
echo "2. source venv/bin/activate"
echo "3. python server.py"
echo ""
echo "Server will run on http://localhost:8080" 