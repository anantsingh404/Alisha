#!/bin/bash
# FaceVault Assistant Launcher

echo "🔐 Starting FaceVault Assistant..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.x"
    exit 1
fi

# Install requirements
echo "📦 Installing requirements..."
cd "$(dirname "$0")/backend"
pip install -r requirements.txt -q

# Create known_faces directory
mkdir -p known_faces

echo ""
echo "🚀 Starting backend server..."
echo "📡 API running at: http://localhost:5000"
echo "🌐 Open frontend/index.html in your browser"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 app.py
