#!/usr/bin/env python3
"""
Main entry point for Requirement Analysis Tool with AI-only Suggestions (NO rule-based logic)
"""

import os
from pathlib import Path
from core.analyzer import RequirementAnalyzer
from utils.file_processor import FileProcessor
from utils.cache_manager import CacheManager

def main():
    print("=" * 80)
    print("Requirement Analysis Tool: Comparative & Non-Atomic Detection (AI Mode Only)")
    print("=" * 80)
    
    # ✅ Always enable AI suggestions
    use_ai = True
    print("AI-powered suggestions: ENABLED (always)")

    # Cache management option
    cache_choice = input("Use cache for faster processing? (Y/n): ").strip().lower()
    use_cache = cache_choice not in ('n', 'no')
    
    if use_cache:
        clear_cache = input("Clear existing cache and reprocess all files? (y/N): ").strip().lower()
        if clear_cache in ('y', 'yes'):
            cache_manager = CacheManager()
            cache_manager.clear_cache()
            print("Cache cleared. All files will be reprocessed.")
    
    dataset_path = input("\nEnter path to requirements folder (default: ./dat/req): ").strip()
    dataset_path = dataset_path or "./dat/req"
    
    # Initialize components
    analyzer = RequirementAnalyzer(use_ai_suggestions=True)
    cache_manager = CacheManager()
    
    # Debug: Check path and files
    req_path = Path(dataset_path)
    print(f"\nChecking path: {req_path.absolute()}")
    print(f"Path exists: {req_path.exists()}")
    
    if not req_path.exists():
        print(f"ERROR: Path '{dataset_path}' does not exist!")
        return
    
    # Find and process files
    try:
        files = FileProcessor.find_requirement_files(dataset_path)
        print(f"\nFound {len(files)} requirement files")
        print(f"Cache contains {cache_manager.get_processed_files_count()} processed files")
        
        if not files:
            print("No requirement files found!")
            return
        
        # Process files
        new_files_count = 0
        cached_files_count = 0
        
        for file_path in files:
            print(f"\nProcessing: {file_path.name} ({file_path.suffix})")
            
            # Check cache first
            if use_cache and cache_manager.is_file_processed(file_path):
                cached_results = cache_manager.get_cached_results(file_path)
                if cached_results:
                    analyzer.load_cached_results(cached_results)
                    print(f"  ✓ Loaded from cache")
                    cached_files_count += 1
                    continue
            
            # Process new or modified file
            try:
                content = FileProcessor.read_file(file_path)
                if content and not content.startswith("[Error") and not content.startswith("[PDF file") and not content.startswith("[Word document"):
                    file_results = analyzer.analyze_text_with_caching(file_path, content, file_path.name, cache_manager)
                    
                    if use_cache:
                        cache_manager.save_results(file_path, file_results)
                    
                    print(f"   Processed and cached")
                    new_files_count += 1
                else:
                    print(f"   Could not extract text content")
            except Exception as e:
                print(f"   Error processing {file_path.name}: {e}")
        
        print(f"\nProcessing Summary:")
        print(f"  - Newly processed files: {new_files_count}")
        print(f"  - Loaded from cache: {cached_files_count}")
        print(f"  - Total files analyzed: {len(analyzer.processed_files)}")
            
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Generate outputs
    generate_outputs(analyzer)

def generate_outputs(analyzer: RequirementAnalyzer):
    """Generate all output reports"""
    
    # Summary table
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    
    stats = analyzer.get_summary_stats()
    print(f"Comparative terms detected: {stats['total_comparatives']}")
    print(f"Superlative terms detected: {stats['total_superlatives']}")
    print(f"Non-atomic requirements detected: {stats['total_non_atomic']}")
    print(f"AI suggestions: Enabled")
    print(f"Files processed: {stats['processed_files']}")
    
    # Always AI suggestions report
    output_file = "ai_suggestions_report.txt"
    generate_detailed_report(analyzer, output_file)
    
    print(f"\nDetailed report saved to: {output_file}")
    print("=" * 80)

def generate_detailed_report(analyzer: RequirementAnalyzer, output_file: str):
    """Generate detailed report with ONLY AI suggestions"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("AI-POWERED REQUIREMENT ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        # Comparative terms
        if analyzer.results['comparatives']:
            f.write("COMPARATIVE TERMS\n")
            f.write("-" * 80 + "\n")
            for idx, item in enumerate(analyzer.results['comparatives'], 1):
                f.write(f"\n{idx}. [{item['document']}] Sentence #{item['sentence_num']}\n")
                f.write(f"   Term: '{item['keyword']}'\n")
                f.write(f"   Original: {item['sentence']}\n")
                
                suggestions = analyzer.generate_improvement_suggestions(item, 'comparative')
                f.write("   AI Suggestions:\n")
                for suggestion in suggestions:
                    for line in suggestion.split('\n'):
                        f.write(f"     {line}\n")
                f.write("-" * 80 + "\n")
        
        # Superlative terms
        if analyzer.results['superlatives']:
            f.write("\n\nSUPERLATIVE TERMS\n")
            f.write("-" * 80 + "\n")
            for idx, item in enumerate(analyzer.results['superlatives'], 1):
                f.write(f"\n{idx}. [{item['document']}] Sentence #{item['sentence_num']}\n")
                f.write(f"   Term: '{item['keyword']}'\n")
                f.write(f"   Original: {item['sentence']}\n")
                
                suggestions = analyzer.generate_improvement_suggestions(item, 'superlative')
                f.write("   AI Suggestions:\n")
                for suggestion in suggestions:
                    for line in suggestion.split('\n'):
                        f.write(f"     {line}\n")
                f.write("-" * 80 + "\n")
        
        # Non-atomic requirements
        if analyzer.results['non_atomic']:
            f.write("\n\nNON-ATOMIC REQUIREMENTS\n")
            f.write("-" * 80 + "\n")
            for idx, item in enumerate(analyzer.results['non_atomic'], 1):
                f.write(f"\n{idx}. [{item['document']}] Sentence #{item['sentence_num']}\n")
                f.write(f"   Coordinator: '{item['coordinator']}' (count: {item['coordinator_count']})\n")
                f.write(f"   Action verbs: {item['verb_count']}\n")
                f.write(f"   Original: {item['sentence']}\n")
                
                suggestions = analyzer.generate_improvement_suggestions(item, 'non_atomic')
                f.write("   AI Suggestions:\n")
                for suggestion in suggestions:
                    for line in suggestion.split('\n'):
                        f.write(f"     {line}\n")
                f.write("-" * 80 + "\n")
        
        # If no issues found
        if not any(analyzer.results.values()):
            f.write("\nNo issues found.\nRequirements appear to be well-written!\n")

if __name__ == "__main__":
    main()
