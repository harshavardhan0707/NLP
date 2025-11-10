"""
Main analyzer that coordinates detection and suggestion generation with caching support
"""

from typing import Dict, List
from core.detector import RequirementDetector
from gemini.suggester import GeminiSuggester

class RequirementAnalyzer:
    def __init__(self, use_ai_suggestions: bool = True):
        self.detector = RequirementDetector()
        self.gemini = GeminiSuggester() if use_ai_suggestions else None
        self.results = {
            'comparatives': [],
            'superlatives': [], 
            'non_atomic': []
        }
        self.processed_files = set()
    
    def analyze_text(self, text: str, doc_name: str) -> None:
        """Analyze a single text document"""
        # Detect issues
        comparatives, superlatives = self.detector.detect_comparatives_superlatives(text, doc_name)
        non_atomic = self.detector.detect_non_atomic_requirements(text, doc_name)
        
        # Store results
        self.results['comparatives'].extend(comparatives)
        self.results['superlatives'].extend(superlatives)
        self.results['non_atomic'].extend(non_atomic)
        
        self.processed_files.add(doc_name)
    
    def analyze_text_with_caching(self, file_path, text: str, doc_name: str, cache_manager) -> Dict:
        """Analyze text and return results for caching"""
        # Detect issues
        comparatives, superlatives = self.detector.detect_comparatives_superlatives(text, doc_name)
        non_atomic = self.detector.detect_non_atomic_requirements(text, doc_name)
        
        # Prepare results for caching
        file_results = {
            'comparatives': comparatives,
            'superlatives': superlatives,
            'non_atomic': non_atomic
        }
        
        # Also add to main results for reporting
        self.results['comparatives'].extend(comparatives)
        self.results['superlatives'].extend(superlatives)
        self.results['non_atomic'].extend(non_atomic)
        
        self.processed_files.add(doc_name)
        
        return file_results
    
    def get_ai_suggestions(self, item: Dict, item_type: str) -> List[str]:
        """Get AI-powered suggestions for an issue"""
        if not self.gemini or not self.gemini.enabled:
            return ["AI suggestions disabled"]
        
        keyword = item.get('keyword', item.get('coordinator', ''))
        suggestion = self.gemini.get_suggestions(item['sentence'], item_type, keyword)
        
        if suggestion:
            return [suggestion]
        else:
            return ["No AI suggestion available"]
    
    def generate_improvement_suggestions(self, item: Dict, item_type: str) -> List[str]:
        """Generate improvement suggestions (AI-powered)"""
        suggestions = []
        
        # Add AI suggestions
        ai_suggestions = self.get_ai_suggestions(item, item_type)
        suggestions.extend(ai_suggestions)
        
        return suggestions
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics"""
        return {
            'total_comparatives': len(self.results['comparatives']),
            'total_superlatives': len(self.results['superlatives']),
            'total_non_atomic': len(self.results['non_atomic']),
            'ai_enabled': self.gemini and self.gemini.enabled,
            'processed_files': len(self.processed_files)
        }
    
    def load_cached_results(self, cached_results: Dict):
        """Load results from cache"""
        if cached_results:
            self.results['comparatives'].extend(cached_results.get('comparatives', []))
            self.results['superlatives'].extend(cached_results.get('superlatives', []))
            self.results['non_atomic'].extend(cached_results.get('non_atomic', []))