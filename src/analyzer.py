"""
Analyzer Module
Main orchestrator for requirement analysis.
"""

from typing import Dict, List
from pathlib import Path
from .document_parser import DocumentParser
from .requirement_detector import RequirementDetector
from .requirement_splitter import RequirementSplitter
from .report_generator import ReportGenerator


class RequirementAnalyzer:
    """Main analyzer that orchestrates the entire analysis pipeline."""
    
    def __init__(self, use_spacy: bool = True, output_dir: str = 'output'):
        """
        Initialize analyzer.
        
        Args:
            use_spacy: Whether to use spaCy for NLP (more accurate but slower)
            output_dir: Directory to save outputs
        """
        self.parser = DocumentParser()
        self.detector = RequirementDetector(use_spacy=use_spacy)
        self.splitter = RequirementSplitter(use_spacy=use_spacy)
        self.report_generator = ReportGenerator(output_dir=output_dir)
        
        self.all_results = {}
    
    def analyze_documents(self, data_dir: str) -> Dict:
        """
        Analyze all HTML documents in a directory.
        
        Args:
            data_dir: Path to directory containing HTML files
            
        Returns:
            Dictionary with all analysis results
        """
        print("\n" + "="*70)
        print("STARTING REQUIREMENT ANALYSIS")
        print("="*70 + "\n")
        
        # Step 1: Parse HTML documents
        print("Step 1: Parsing HTML documents...")
        documents = self.parser.parse_all_documents(data_dir)
        print(f"✓ Parsed {len(documents)} documents\n")
        
        # Step 2-4: Analyze each document
        for doc_name, requirements in documents.items():
            print(f"\nAnalyzing {doc_name}...")
            print(f"  Requirements found: {len(requirements)}")
            
            # Detect comparative issues
            comparative_issues = []
            for req in requirements:
                result = self.detector.detect_comparatives(req)
                if result['has_comparative_issues']:
                    result['text'] = req['text']  # Include original text
                    comparative_issues.append(result)
            
            print(f"  Comparative issues: {len(comparative_issues)}")
            
            # Detect non-atomic issues
            non_atomic_issues = []
            proposed_splits = {}
            
            for req in requirements:
                result = self.detector.detect_non_atomic(req)
                if result['is_non_atomic']:
                    result['text'] = req['text']  # Include original text
                    non_atomic_issues.append(result)
                    
                    # Propose splits
                    splits = self.splitter.split_requirement(req, result)
                    if len(splits) > 1:
                        proposed_splits[req['req_id']] = splits
            
            print(f"  Non-atomic issues: {len(non_atomic_issues)}")
            print(f"  Proposed splits: {len(proposed_splits)}")
            
            # Store results
            self.all_results[doc_name] = {
                'requirements': requirements,
                'comparative_issues': comparative_issues,
                'non_atomic_issues': non_atomic_issues,
                'proposed_splits': proposed_splits
            }
        
        print("\n" + "="*70)
        print("ANALYSIS COMPLETE")
        print("="*70 + "\n")
        
        return self.all_results
    
    def generate_reports(self):
        """Generate all reports (JSON, CSV, Markdown)."""
        print("\nGenerating reports...")
        
        # Generate statistics
        stats_df = self.report_generator.generate_statistics(self.all_results)
        
        # Save reports
        self.report_generator.save_results_json(self.all_results)
        self.report_generator.save_statistics_csv(stats_df)
        self.report_generator.generate_markdown_report(self.all_results, stats_df)
        
        # Print summary
        self.report_generator.print_summary(stats_df)
        
        print("\n✓ All reports generated successfully!")
    
    def run_full_analysis(self, data_dir: str):
        """
        Run complete analysis pipeline.
        
        Args:
            data_dir: Path to directory containing HTML files
        """
        # Analyze documents
        self.analyze_documents(data_dir)
        
        # Generate reports
        self.generate_reports()


if __name__ == "__main__":
    # Test the analyzer
    analyzer = RequirementAnalyzer(use_spacy=False)
    analyzer.run_full_analysis('../data/req/')
