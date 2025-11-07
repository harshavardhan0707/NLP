"""
Main Entry Point
Run the requirement analysis system.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.analyzer import RequirementAnalyzer


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Comparative & Non-atomic Requirement Analysis System'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/req/',
        help='Directory containing HTML requirement files (default: data/req/)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Directory to save output files (default: output)'
    )
    
    parser.add_argument(
        '--use-spacy',
        action='store_true',
        help='Use spaCy for advanced NLP (slower but more accurate)'
    )
    
    parser.add_argument(
        '--no-spacy',
        action='store_true',
        help='Disable spaCy and use regex-based detection (faster)'
    )
    
    args = parser.parse_args()
    
    # Determine whether to use spaCy
    use_spacy = args.use_spacy and not args.no_spacy
    
    # Print configuration
    print("\n" + "="*70)
    print("REQUIREMENT ANALYSIS CONFIGURATION")
    print("="*70)
    print(f"Data Directory:   {args.data_dir}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Using spaCy:      {'Yes' if use_spacy else 'No (regex-based)'}")
    print("="*70 + "\n")
    
    # Check if data directory exists
    data_path = Path(args.data_dir)
    if not data_path.exists():
        print(f"Error: Data directory not found: {args.data_dir}")
        print("Please provide a valid directory containing HTML requirement files.")
        sys.exit(1)
    
    # Count HTML files
    html_files = list(data_path.glob('*.html')) + list(data_path.glob('*.htm'))
    if not html_files:
        print(f"Error: No HTML files found in {args.data_dir}")
        sys.exit(1)
    
    print(f"Found {len(html_files)} HTML files to analyze:")
    for html_file in html_files:
        print(f"  - {html_file.name}")
    print()
    
    # Create analyzer and run analysis
    try:
        analyzer = RequirementAnalyzer(
            use_spacy=use_spacy,
            output_dir=args.output_dir
        )
        
        # Run full analysis
        analyzer.run_full_analysis(args.data_dir)
        
        print("\n" + "="*70)
        print("SUCCESS!")
        print("="*70)
        print(f"\nCheck the '{args.output_dir}' directory for:")
        print("  - results.json       (detailed findings)")
        print("  - statistics.csv     (statistical summary)")
        print("  - report.md          (comprehensive analysis report)")
        print()
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
