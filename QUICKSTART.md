# Quick Start Guide

## ✅ System is Ready!

Your requirement analysis system is **fully set up and working**.

---

## 🚀 How to Run (3 Ways)

### Method 1: Quick Run Script (Easiest)
```bash
./run_analysis.sh
```

### Method 2: Manual Run
```bash
source venv/bin/activate
python main.py --no-spacy
deactivate
```

### Method 3: With spaCy (More Accurate)
```bash
source venv/bin/activate
pip install spacy
python -m spacy download en_core_web_sm
python main.py --use-spacy
deactivate
```

---

## 📊 What You'll Get

After running, check the **`output/`** directory:

1. **`results.json`** - Detailed findings (all detected issues)
2. **`statistics.csv`** - Statistical summary table
3. **`report.md`** - Comprehensive analysis report

---

## 📈 Your Current Results

Last analysis results:
- **Total Requirements**: 459
- **Comparative Issues**: 8 (1.7%)
- **Non-atomic Issues**: 24 (5.2%)
- **Total Issues**: 32 (7.0%)

Files analyzed:
- `2005 - nenios.html`: 118 requirements
- `1999 - multi-mahjong.html`: 272 requirements
- `1999 - dii.htm`: 69 requirements

---

## 🔧 Troubleshooting

### "No module named 'bs4'" or similar
```bash
source venv/bin/activate
pip install beautifulsoup4 lxml pandas tabulate
```

### Virtual environment not found
```bash
./setup.sh
```

### Permission denied on scripts
```bash
chmod +x setup.sh run_analysis.sh
```

---

## 📁 Project Structure

```
NLP/
├── main.py                  # Entry point
├── setup.sh                 # Automated setup
├── run_analysis.sh          # Quick run script
├── test_setup.py            # Check if setup is correct
├── requirements.txt         # Python dependencies
├── README.md                # Full documentation
├── src/                     # Source code
│   ├── html_parser.py
│   ├── requirement_detector.py
│   ├── requirement_splitter.py
│   ├── analyzer.py
│   └── report_generator.py
├── data/req/                # Input HTML files
├── output/                  # Generated reports
└── venv/                    # Virtual environment (created)
```

---

## 💡 Tips

- Always activate virtual environment before running: `source venv/bin/activate`
- Use `--no-spacy` flag for faster execution (regex-based)
- Use `--use-spacy` for more accurate NLP-based detection
- Check `output/report.md` for detailed examples

---

## 📚 Full Documentation

For complete instructions, see:
- **README.md** - Full usage guide
- **COLAB_NOTEBOOK.md** - Google Colab instructions
- **IMPLEMENTATION_COMPLETE.md** - Project overview

---

## ✨ You're All Set!

Run `./run_analysis.sh` and check the `output/` directory for results!
