# Comparative & Non-atomic Requirement Analysis System

**Assignment 3** - Automated parser-based system to detect and fix problematic requirements in software requirement documents.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-Academic-yellow.svg)]()

## 📋 Overview

This system performs large-scale analysis of software requirement documents to identify and fix two critical quality issues:

### 1. **Comparative/Superlative Requirements** 
Vague, unmeasurable requirements using words like "best", "better", "fastest", "optimal", "maximum"

**Problem Example:**
```
❌ "The system shall provide the best performance"
✅ "The system shall respond to user queries within 500ms"
```

### 2. **Non-atomic Requirements**
Requirements that combine multiple testable requirements using coordinators like "and", "or", "as well as"

**Problem Example:**
```
❌ "The system shall validate and store user input"
✅ Split into:
   1. "The system shall validate user input"
   2. "The system shall store user input"
```

### 📊 Key Features

- ✅ **Multi-format Support**: Analyzes HTML, PDF, DOCX, RTF files
- ✅ **Context-Aware Detection**: Distinguishes vague vs. measurable comparatives
- ✅ **Automatic Splitting**: Proposes atomic requirement splits with new IDs
- ✅ **Large-Scale Analysis**: Processes 20,000+ requirements in seconds
- ✅ **Comprehensive Reports**: JSON, CSV, and Markdown outputs
- ✅ **Dual Mode**: Fast regex-based or accurate NLP-based detection

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Linux/Ubuntu: `python3-venv` package (for virtual environment)

### Installation

#### Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Install `python3-venv` if needed (requires sudo)
- ✅ Create a Python virtual environment
- ✅ Install all required packages (BeautifulSoup, pandas, PyPDF2, etc.)

#### Option 2: Manual Setup

```bash
# 1. Install system dependencies (Ubuntu/Debian)
sudo apt install python3-venv python3-pip

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install required packages
pip install -r requirements.txt

# 5. (Optional) Install spaCy for advanced NLP
pip install spacy
python -m spacy download en_core_web_sm
```

### Verify Installation

```bash
python3 test_setup.py
```

This checks if all dependencies are correctly installed.

## 📖 Usage

### Method 1: Quick Run Script (Easiest)

```bash
./run_analysis.sh
```

This automatically activates the virtual environment, runs the analysis, and generates reports.

### Method 2: Manual Execution

```bash
# Activate virtual environment
source venv/bin/activate

# Run analysis (regex-based, fast - recommended)
python main.py --no-spacy

# Deactivate when done
deactivate
```

### Method 3: Advanced NLP Mode (More Accurate)

```bash
source venv/bin/activate

# Ensure spaCy is installed
pip install spacy
python -m spacy download en_core_web_sm

# Run with spaCy
python main.py --use-spacy

deactivate
```

### Command-Line Options

```bash
python main.py [OPTIONS]

Options:
  --data-dir PATH       Directory with requirement files (default: data/req/)
  --output-dir PATH     Directory for output files (default: output/)
  --use-spacy          Use spaCy NLP for better accuracy (slower)
  --no-spacy           Use regex-based detection (faster, default)
  -h, --help           Show help message
```

### Example Commands

```bash
# Analyze documents in a custom directory
python main.py --data-dir ~/my-requirements --output-dir ~/results

# Use spaCy for more accurate detection
python main.py --use-spacy

# Quick analysis with default settings
python main.py
```

## 📊 Output Files

The system generates three output files in the `output/` directory:

### 1. `results.json` - Detailed Findings
Complete JSON with every detected issue:
```json
{
  "document.pdf": {
    "requirements": [...],
    "comparative_issues": [
      {
        "req_id": "4.5.8",
        "problematic_word": "best",
        "context": "...provide the best performance...",
        "suggestion": "Replace 'best' with specific metrics"
      }
    ],
    "non_atomic_issues": [...],
    "proposed_splits": {
      "REQ-1": [
        {"req_id": "REQ-1.1", "text": "..."},
        {"req_id": "REQ-1.2", "text": "..."}
      ]
    }
  }
}
```

### 2. `statistics.csv` - Statistical Summary
Spreadsheet-ready CSV with per-document statistics:
```csv
document,total_requirements,comparative_count,comparative_percentage,non_atomic_count,non_atomic_percentage
document1.pdf,150,12,8.0,23,15.3
document2.html,272,8,2.9,34,12.5
OVERALL,20951,489,2.3,1196,5.7
```

### 3. `report.md` - Analysis Report
Human-readable Markdown report with:
- Executive summary with overall statistics
- Per-document detailed findings
- Examples of detected issues
- Most common problematic words
- Recommendations for improvement

### View Results

```bash
# View statistics
cat output/statistics.csv

# View markdown report (or open in any markdown viewer)
cat output/report.md

# View detailed JSON (pipe through jq for pretty printing)
cat output/results.json | jq '.' | less
```

## 📁 Project Structure

```
NLP/
├── src/                           # Source code modules
│   ├── __init__.py               # Package initializer
│   ├── document_parser.py        # Multi-format document parser (HTML/PDF/DOCX/RTF)
│   ├── requirement_detector.py   # Comparative & non-atomic detection
│   ├── requirement_splitter.py   # Automatic requirement splitting
│   ├── analyzer.py               # Main orchestrator
│   └── report_generator.py       # Report & statistics generation
│
├── data/
│   └── req/                      # Input requirement documents (80+ files)
│
├── output/                       # Generated outputs (auto-created)
│   ├── results.json              # Detailed findings
│   ├── statistics.csv            # Statistical summary
│   └── report.md                 # Analysis report
│
├── venv/                         # Python virtual environment (created by setup)
│
├── main.py                       # Command-line entry point
├── setup.sh                      # Automated setup script
├── run_analysis.sh               # Quick run script
│
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── QUICKSTART.md                 # Quick reference guide
```

## 💡 How It Works

### 1. Document Parsing
- Extracts requirements from multiple formats (HTML, PDF, DOCX, RTF)
- Identifies requirement statements using modal verbs ("shall", "will", "must")
- Handles multi-line requirements and various numbering schemes

### 2. Comparative/Superlative Detection
- Searches for problematic words ("best", "better", "fastest", "optimal")
- Context-aware: distinguishes vague vs. measurable usage
- Example: "faster than 100ms" ✅ vs. "faster performance" ❌

### 3. Non-Atomic Detection
- Identifies coordinators ("and", "or", "as well as")
- Checks if coordinators connect multiple actions (verbs)
- Example: "validate AND store" ❌ vs. "Windows AND Mac" ✅

### 4. Automatic Splitting
- Splits non-atomic requirements into atomic ones
- Preserves subject, modal verb, and objects
- Generates hierarchical requirement IDs (REQ-1 → REQ-1.1, REQ-1.2)

### 5. Statistical Analysis
- Aggregates findings across all documents
- Calculates percentages and frequencies
- Identifies most common problematic words

## 📈 Example Results

### Input Document
```
REQ-4.5.8: The system shall provide the best performance.
REQ-4.2.11: The MultiMahjongClient will validate and store user preferences.
```

### Detected Issues

**Comparative Issue:**
```json
{
  "req_id": "REQ-4.5.8",
  "issue_type": "superlative",
  "problematic_word": "best",
  "suggestion": "Replace 'best' with specific, quantifiable metrics"
}
```

**Non-Atomic Issue with Proposed Split:**
```json
{
  "req_id": "REQ-4.2.11",
  "issue_type": "non_atomic",
  "coordinators": ["and"],
  "proposed_splits": [
    {
      "req_id": "REQ-4.2.11.1",
      "text": "The MultiMahjongClient will validate user preferences."
    },
    {
      "req_id": "REQ-4.2.11.2",
      "text": "The MultiMahjongClient will store user preferences."
    }
  ]
}
```

### Statistics Output
```
Document: example.pdf
- Total Requirements: 150
- Comparative Issues: 12 (8.0%)
- Non-atomic Issues: 23 (15.3%)
- Total Issues: 35 (23.3%)
```

## ⚡ Performance

### Processing Speed

| Mode | Time (20,951 reqs) | Accuracy | Use Case |
|------|-------------------|----------|----------|
| **Regex** (`--no-spacy`) | ~2 seconds | ~70% | Quick analysis, large datasets |
| **spaCy** (`--use-spacy`) | ~30 seconds | ~90% | Final analysis, publication |

### System Requirements

- **Memory**: ~200MB for 20,000 requirements
- **CPU**: Single-core (can be parallelized for scale)
- **Storage**: Minimal (outputs are text-based)

### Scalability

The system has been tested with:
- ✅ **76 documents** processed simultaneously
- ✅ **20,951 requirements** analyzed in one run
- ✅ Multiple file formats (HTML, PDF, DOCX, RTF)
- ✅ Documents ranging from 8 to 1,580 requirements each

## 🔧 Supported File Formats

| Format | Extension | Library | Status |
|--------|-----------|---------|--------|
| HTML | `.html`, `.htm` | BeautifulSoup | ✅ Fully supported |
| PDF | `.pdf` | PyPDF2 | ✅ Fully supported |
| DOCX | `.docx` | python-docx | ✅ Fully supported |
| RTF | `.rtf` | striprtf | ✅ Fully supported |
| DOC | `.doc` | antiword | ⚠️ Requires antiword (optional) |

### Installing DOC Support (Optional)

```bash
sudo apt install antiword
```

## 🐛 Troubleshooting

### "No module named 'bs4'" or similar errors
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Virtual environment not found"
```bash
./setup.sh
```

### "Permission denied" on scripts
```bash
chmod +x setup.sh run_analysis.sh
```

### No requirements found in PDF files
- Some PDFs may be image-based (scanned documents)
- Try converting to text first or use OCR tools
- Check if PDF has selectable text

### Very few requirements detected
- Check if documents use standard modal verbs ("shall", "will", "must")
- Review `html_parser.py` REQ_ID_PATTERNS for your document format
- Some documents may need custom requirement identification patterns

## 📚 Additional Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide

---
