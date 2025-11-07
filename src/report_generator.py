"""
Report Generator Module
Generates statistics, visualizations, and reports.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from collections import Counter


class ReportGenerator:
    """Generate analysis reports and statistics."""
    
    def __init__(self, output_dir: str = 'output'):
        """
        Initialize report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_statistics(self, all_results: Dict) -> pd.DataFrame:
        """
        Generate statistical summary.
        
        Args:
            all_results: Dictionary with all analysis results
            
        Returns:
            DataFrame with statistics
        """
        stats = []
        
        for doc_name, doc_data in all_results.items():
            requirements = doc_data['requirements']
            comparative_issues = doc_data['comparative_issues']
            non_atomic_issues = doc_data['non_atomic_issues']
            
            total_reqs = len(requirements)
            comp_count = len(comparative_issues)
            non_atomic_count = len(non_atomic_issues)
            
            comp_pct = (comp_count / total_reqs * 100) if total_reqs > 0 else 0
            non_atomic_pct = (non_atomic_count / total_reqs * 100) if total_reqs > 0 else 0
            
            stats.append({
                'document': doc_name,
                'total_requirements': total_reqs,
                'comparative_count': comp_count,
                'comparative_percentage': round(comp_pct, 1),
                'non_atomic_count': non_atomic_count,
                'non_atomic_percentage': round(non_atomic_pct, 1),
                'total_issues': comp_count + non_atomic_count,
                'total_issues_percentage': round((comp_count + non_atomic_count) / total_reqs * 100, 1) if total_reqs > 0 else 0
            })
        
        df = pd.DataFrame(stats)
        
        # Add overall row
        if len(df) > 0:
            overall = {
                'document': 'OVERALL',
                'total_requirements': df['total_requirements'].sum(),
                'comparative_count': df['comparative_count'].sum(),
                'comparative_percentage': round(df['comparative_count'].sum() / df['total_requirements'].sum() * 100, 1),
                'non_atomic_count': df['non_atomic_count'].sum(),
                'non_atomic_percentage': round(df['non_atomic_count'].sum() / df['total_requirements'].sum() * 100, 1),
                'total_issues': df['total_issues'].sum(),
                'total_issues_percentage': round(df['total_issues'].sum() / df['total_requirements'].sum() * 100, 1)
            }
            df = pd.concat([df, pd.DataFrame([overall])], ignore_index=True)
        
        return df
    
    def save_statistics_csv(self, stats_df: pd.DataFrame, filename: str = 'statistics.csv'):
        """
        Save statistics to CSV file.
        
        Args:
            stats_df: Statistics DataFrame
            filename: Output filename
        """
        filepath = self.output_dir / filename
        stats_df.to_csv(filepath, index=False)
        print(f"Statistics saved to {filepath}")
    
    def save_results_json(self, all_results: Dict, filename: str = 'results.json'):
        """
        Save detailed results to JSON file.
        
        Args:
            all_results: All analysis results
            filename: Output filename
        """
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"Detailed results saved to {filepath}")
    
    def generate_markdown_report(self, all_results: Dict, stats_df: pd.DataFrame, 
                                 filename: str = 'report.md'):
        """
        Generate comprehensive markdown report.
        
        Args:
            all_results: All analysis results
            stats_df: Statistics DataFrame
            filename: Output filename
        """
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("# Comparative & Non-atomic Requirement Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            overall_stats = stats_df[stats_df['document'] == 'OVERALL'].iloc[0]
            f.write(f"- **Total Requirements Analyzed:** {overall_stats['total_requirements']}\n")
            f.write(f"- **Comparative/Superlative Issues:** {overall_stats['comparative_count']} ({overall_stats['comparative_percentage']}%)\n")
            f.write(f"- **Non-atomic Issues:** {overall_stats['non_atomic_count']} ({overall_stats['non_atomic_percentage']}%)\n")
            f.write(f"- **Total Issues Found:** {overall_stats['total_issues']} ({overall_stats['total_issues_percentage']}%)\n\n")
            
            # Statistical Overview
            f.write("## Statistical Overview\n\n")
            f.write("### Summary by Document\n\n")
            f.write(stats_df.to_markdown(index=False))
            f.write("\n\n")
            
            # Most Common Issues
            f.write("## Most Common Issues\n\n")
            
            # Comparative words
            all_comp_words = []
            for doc_data in all_results.values():
                for issue in doc_data['comparative_issues']:
                    for comp_issue in issue.get('issues', []):
                        all_comp_words.append(comp_issue['problematic_word'])
            
            if all_comp_words:
                comp_counter = Counter(all_comp_words)
                f.write("### Most Common Comparative/Superlative Words\n\n")
                for word, count in comp_counter.most_common(10):
                    f.write(f"- **{word}**: {count} occurrences\n")
                f.write("\n")
            
            # Coordinators
            all_coordinators = []
            for doc_data in all_results.values():
                for issue in doc_data['non_atomic_issues']:
                    all_coordinators.extend(issue.get('coordinators', []))
            
            if all_coordinators:
                coord_counter = Counter(all_coordinators)
                f.write("### Most Common Coordinators\n\n")
                for coord, count in coord_counter.most_common(10):
                    f.write(f"- **{coord}**: {count} occurrences\n")
                f.write("\n")
            
            # Detailed Findings by Document
            f.write("## Detailed Findings by Document\n\n")
            
            for doc_name, doc_data in all_results.items():
                f.write(f"### {doc_name}\n\n")
                
                requirements = doc_data['requirements']
                comparative_issues = doc_data['comparative_issues']
                non_atomic_issues = doc_data['non_atomic_issues']
                proposed_splits = doc_data.get('proposed_splits', {})
                
                f.write(f"**Total Requirements:** {len(requirements)}\n\n")
                
                # Comparative Issues
                if comparative_issues:
                    f.write(f"#### Comparative/Superlative Issues ({len(comparative_issues)})\n\n")
                    
                    for i, issue in enumerate(comparative_issues[:5], 1):  # Show first 5
                        f.write(f"**{i}. Requirement {issue['req_id']}**\n\n")
                        f.write(f"*Original:* {issue.get('text', 'N/A')[:200]}...\n\n")
                        
                        for comp_issue in issue.get('issues', []):
                            f.write(f"- **Issue:** {comp_issue['issue_type'].title()}\n")
                            f.write(f"- **Problematic Word:** `{comp_issue['problematic_word']}`\n")
                            f.write(f"- **Context:** {comp_issue['context'][:150]}...\n")
                            f.write(f"- **Suggestion:** {comp_issue['suggestion']}\n\n")
                    
                    if len(comparative_issues) > 5:
                        f.write(f"*... and {len(comparative_issues) - 5} more issues*\n\n")
                
                # Non-atomic Issues
                if non_atomic_issues:
                    f.write(f"#### Non-atomic Issues ({len(non_atomic_issues)})\n\n")
                    
                    for i, issue in enumerate(non_atomic_issues[:5], 1):  # Show first 5
                        f.write(f"**{i}. Requirement {issue['req_id']}**\n\n")
                        f.write(f"*Original:* {issue.get('text', 'N/A')[:200]}...\n\n")
                        f.write(f"- **Coordinators Found:** {', '.join(issue.get('coordinators', []))}\n")
                        f.write(f"- **Actions Detected:** {', '.join(issue.get('actions', []))}\n")
                        
                        # Show proposed split
                        req_id = issue['req_id']
                        if req_id in proposed_splits:
                            splits = proposed_splits[req_id]
                            f.write(f"- **Proposed Split ({len(splits)} requirements):**\n")
                            for split in splits:
                                f.write(f"  - `{split['req_id']}`: {split['text']}\n")
                        f.write("\n")
                    
                    if len(non_atomic_issues) > 5:
                        f.write(f"*... and {len(non_atomic_issues) - 5} more issues*\n\n")
                
                f.write("---\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            f.write("### For Requirements Authors\n\n")
            f.write("1. **Avoid Vague Comparatives:** Replace words like 'better', 'faster', 'best' with specific, measurable criteria\n")
            f.write("2. **One Requirement Per Statement:** Split compound requirements using 'and', 'or' into separate, testable requirements\n")
            f.write("3. **Use Quantifiable Metrics:** Include specific numbers, timeframes, and thresholds\n")
            f.write("4. **Be Specific:** Define exact performance criteria rather than relative terms\n")
            f.write("5. **Make Requirements Testable:** Each requirement should have clear pass/fail criteria\n\n")
            
            f.write("### Best Practices\n\n")
            f.write("- ❌ Bad: 'The system shall provide the best performance'\n")
            f.write("- ✅ Good: 'The system shall respond to user queries within 500ms'\n\n")
            f.write("- ❌ Bad: 'The system shall validate and store user input'\n")
            f.write("- ✅ Good: Split into two requirements:\n")
            f.write("  - 'The system shall validate user input'\n")
            f.write("  - 'The system shall store validated user input'\n\n")
            
            # Conclusion
            f.write("## Conclusion\n\n")
            f.write(f"This analysis identified {overall_stats['total_issues']} problematic requirements ")
            f.write(f"out of {overall_stats['total_requirements']} total requirements ")
            f.write(f"({overall_stats['total_issues_percentage']}% issue rate).\n\n")
            
            if overall_stats['total_issues_percentage'] > 30:
                f.write("The high issue rate suggests that significant improvements are needed in requirement specification practices.\n")
            elif overall_stats['total_issues_percentage'] > 15:
                f.write("The moderate issue rate indicates that there is room for improvement in requirement quality.\n")
            else:
                f.write("The low issue rate suggests generally good requirement quality, with some areas for refinement.\n")
        
        print(f"Report generated: {filepath}")
    
    def print_summary(self, stats_df: pd.DataFrame):
        """
        Print summary to console.
        
        Args:
            stats_df: Statistics DataFrame
        """
        print("\n" + "="*70)
        print("REQUIREMENT ANALYSIS SUMMARY")
        print("="*70 + "\n")
        
        print(stats_df.to_string(index=False))
        print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    # Test report generator
    generator = ReportGenerator('../output')
    
    # Mock data
    test_results = {
        'test.html': {
            'requirements': [{'req_id': 'R1', 'text': 'Test requirement'}] * 100,
            'comparative_issues': [{'req_id': 'R1', 'issues': []}] * 10,
            'non_atomic_issues': [{'req_id': 'R2', 'coordinators': ['and']}] * 20,
            'proposed_splits': {}
        }
    }
    
    stats = generator.generate_statistics(test_results)
    generator.print_summary(stats)
