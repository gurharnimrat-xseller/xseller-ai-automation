#!/bin/bash

# Setup script for backend virtual environment
# This script handles Python 3.13 compatibility issues

set -e

echo "════════════════════════════════════════════════════════════════════"
echo "🔧 BACKEND VENV SETUP"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Detect Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
echo "📋 Python version: $(python3 --version)"

# Check if venv exists
if [ -d "venv" ]; then
    echo ""
    echo "⚠️  Virtual environment already exists"
    echo "🗑️  Removing existing venv to recreate..."
    rm -rf venv
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETE!"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the backend server:"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""

