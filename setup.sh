#!/bin/bash
# Setup script for the requirement analysis system

echo "=========================================="
echo "Requirement Analysis System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if python3-venv is available
echo ""
echo "Checking for python3-venv..."
python3 -m venv --help > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo ""
    echo "python3-venv is not installed."
    echo "Installing python3-venv (requires sudo)..."
    sudo apt install -y python3-venv python3-pip
    if [ $? -ne 0 ]; then
        echo ""
        echo "Error: Could not install python3-venv"
        echo "Please run: sudo apt install python3-venv"
        exit 1
    fi
fi

# Create output directory
echo ""
echo "Creating output directory..."
mkdir -p output

# Create virtual environment
echo ""
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate and install packages
echo ""
echo "Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip -q
pip install beautifulsoup4 lxml pandas tabulate -q

if [ $? -eq 0 ]; then
    echo "✓ All packages installed successfully"
else
    echo "Error: Package installation failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To run the analysis:"
echo "  source venv/bin/activate"
echo "  python main.py --no-spacy"
echo ""
echo "Or for a quick run:"
echo "  ./run_analysis.sh"
echo ""
echo "For Google Colab, see COLAB_NOTEBOOK.md"
