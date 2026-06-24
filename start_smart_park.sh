#!/bin/bash
# Quick start script for Smart Park System

echo "🅿️  Smart Park System - Quick Start"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip is not installed"
    echo "Please install pip"
    exit 1
fi

echo "✅ pip found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r reqiuirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🚀 Starting Smart Park System..."
echo ""
echo "The application will open in your default browser."
echo "If it doesn't, navigate to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
streamlit run smart_park.py
