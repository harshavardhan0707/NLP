#!/bin/bash
# Quick run script for requirement analysis

# Activate virtual environment
source venv/bin/activate

# Run analysis
python main.py --no-spacy

# Deactivate
deactivate

echo ""
echo "Analysis complete! Check the output/ directory for results."
