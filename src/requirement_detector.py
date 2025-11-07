"""
Requirement Detector Module
Detects comparative/superlative and non-atomic requirements.
"""

import re
from typing import List, Dict, Tuple, Set
from collections import defaultdict

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class RequirementDetector:
    """Detect problematic patterns in requirements."""
    
    # Comparative words
    COMPARATIVES = {
        'better', 'faster', 'slower', 'higher', 'lower',
        'greater', 'smaller', 'more', 'less', 'fewer',
        'improved', 'enhanced', 'optimized', 'superior',
        'worse', 'inferior', 'larger', 'shorter', 'longer',
        'cheaper', 'costlier', 'easier', 'harder', 'simpler',
        'quicker', 'wider', 'narrower', 'deeper', 'shallower',
        'stronger', 'weaker', 'richer', 'poorer', 'cleaner',
        'different', 'various', 'multiple', 'several'
    }
    
    # Superlative words
    SUPERLATIVES = {
        'best', 'worst', 'fastest', 'slowest', 'highest', 'lowest',
        'greatest', 'smallest', 'most', 'least', 'largest',
        'shortest', 'longest', 'cheapest', 'costliest',
        'easiest', 'hardest', 'simplest', 'quickest',
        'widest', 'narrowest', 'deepest', 'shallowest',
        'strongest', 'weakest', 'richest', 'poorest',
        'cleanest', 'optimal', 'optimum', 'maximum', 'minimum',
        'top', 'bottom', 'ultimate', 'supreme', 'ideal',
        'perfect', 'finest', 'premier', 'primary'
    }
    
    # Coordinators that may indicate non-atomic requirements
    COORDINATORS = {
        'and', 'or', 'as well as', 'along with', 'in addition to',
        'also', 'furthermore', 'moreover', 'plus', 'together with',
        'both', 'either', 'neither', 'nor', 'whilst', 'while'
    }
    
    # Phrases that indicate measurability (not problematic if present)
    MEASURABLE_INDICATORS = {
        'than', 'within', 'at least', 'at most', 'no more than',
        'no less than', 'exactly', 'between', 'from', 'to',
        'second', 'seconds', 'minute', 'minutes', 'hour', 'hours',
        'millisecond', 'ms', 'day', 'days', 'percent', '%',
        'user', 'users', 'item', 'items', 'level', 'levels',
        'byte', 'bytes', 'kb', 'mb', 'gb'
    }
    
    def __init__(self, use_spacy: bool = True):
        """
        Initialize detector.
        
        Args:
            use_spacy: Whether to use spaCy for advanced NLP (slower but more accurate)
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.nlp = None
        
        if self.use_spacy:
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except (OSError, NameError):
                print("Warning: spaCy model not found. Run: python -m spacy download en_core_web_sm")
                print("Falling back to regex-based detection.")
                self.use_spacy = False
    
    def detect_comparatives(self, requirement: Dict) -> Dict:
        """
        Detect comparative and superlative issues in a requirement.
        
        Args:
            requirement: Requirement dictionary with 'text' field
            
        Returns:
            Dictionary with detection results
        """
        text = requirement['text'].lower()
        words = set(text.split())
        
        # Find comparative/superlative words
        found_comparatives = words & self.COMPARATIVES
        found_superlatives = words & self.SUPERLATIVES
        
        issues = []
        
        # Check each found word for context
        for word in found_comparatives:
            context = self._get_word_context(requirement['text'], word)
            is_measurable = self._has_measurable_context(context)
            
            if not is_measurable:
                issues.append({
                    'issue_type': 'comparative',
                    'problematic_word': word,
                    'context': context,
                    'is_measurable': False,
                    'severity': 'medium',
                    'suggestion': f"Replace '{word}' with specific, measurable criteria"
                })
        
        for word in found_superlatives:
            context = self._get_word_context(requirement['text'], word)
            is_measurable = self._has_measurable_context(context)
            
            if not is_measurable:
                issues.append({
                    'issue_type': 'superlative',
                    'problematic_word': word,
                    'context': context,
                    'is_measurable': False,
                    'severity': 'high',
                    'suggestion': f"Replace '{word}' with specific, quantifiable metrics"
                })
        
        return {
            'req_id': requirement['req_id'],
            'has_comparative_issues': len(issues) > 0,
            'comparative_count': len([i for i in issues if i['issue_type'] == 'comparative']),
            'superlative_count': len([i for i in issues if i['issue_type'] == 'superlative']),
            'issues': issues
        }
    
    def detect_non_atomic(self, requirement: Dict) -> Dict:
        """
        Detect non-atomic requirements (multiple requirements combined).
        
        Args:
            requirement: Requirement dictionary with 'text' field
            
        Returns:
            Dictionary with detection results
        """
        text = requirement['text']
        
        if self.use_spacy and self.nlp:
            return self._detect_non_atomic_spacy(requirement)
        else:
            return self._detect_non_atomic_regex(requirement)
    
    def _detect_non_atomic_spacy(self, requirement: Dict) -> Dict:
        """
        Detect non-atomic requirements using spaCy NLP.
        
        Args:
            requirement: Requirement dictionary
            
        Returns:
            Detection results
        """
        text = requirement['text']
        doc = self.nlp(text)
        
        # Find verbs (actions)
        verbs = [token for token in doc if token.pos_ == 'VERB' and not token.is_stop]
        
        # Find coordinators
        coordinators_found = []
        coordinator_positions = []
        
        for token in doc:
            if token.text.lower() in self.COORDINATORS or token.dep_ == 'cc':
                coordinators_found.append(token.text.lower())
                coordinator_positions.append(token.i)
        
        # Check if coordinators are connecting verbs (actions)
        is_non_atomic = False
        connected_actions = []
        
        if len(verbs) >= 2 and coordinators_found:
            # Check if verbs are separated by coordinators
            verb_positions = [v.i for v in verbs]
            
            for coord_pos in coordinator_positions:
                verbs_before = [v for v in verb_positions if v < coord_pos]
                verbs_after = [v for v in verb_positions if v > coord_pos]
                
                if verbs_before and verbs_after:
                    is_non_atomic = True
                    # Extract verb phrases
                    for verb in verbs:
                        phrase = self._extract_verb_phrase(verb)
                        if phrase:
                            connected_actions.append(phrase)
                    break
        
        return {
            'req_id': requirement['req_id'],
            'is_non_atomic': is_non_atomic,
            'coordinators': list(set(coordinators_found)),
            'action_count': len(set(connected_actions)),
            'actions': list(set(connected_actions)),
            'confidence': 0.9 if is_non_atomic else 0.1
        }
    
    def _detect_non_atomic_regex(self, requirement: Dict) -> Dict:
        """
        Detect non-atomic requirements using regex patterns.
        
        Args:
            requirement: Requirement dictionary
            
        Returns:
            Detection results
        """
        text = requirement['text']
        text_lower = text.lower()
        
        # Find coordinators
        coordinators_found = []
        
        for coord in self.COORDINATORS:
            if f' {coord} ' in f' {text_lower} ':
                coordinators_found.append(coord)
        
        # Simple heuristic: if there are coordinators and multiple verbs, likely non-atomic
        # Find action verbs (crude approach)
        action_verbs = ['validate', 'process', 'store', 'save', 'load', 'read', 'write',
                       'create', 'delete', 'update', 'send', 'receive', 'display', 'show',
                       'calculate', 'compute', 'verify', 'check', 'execute', 'run',
                       'start', 'stop', 'pause', 'resume', 'export', 'import', 'generate']
        
        found_verbs = [verb for verb in action_verbs if verb in text_lower]
        
        is_non_atomic = len(coordinators_found) > 0 and len(found_verbs) >= 2
        
        # Special case: "and" connecting list items (not non-atomic)
        if 'and' in coordinators_found and coordinators_found == ['and']:
            # Check if it's just a list (e.g., "Windows and Mac")
            if len(found_verbs) < 2:
                is_non_atomic = False
        
        return {
            'req_id': requirement['req_id'],
            'is_non_atomic': is_non_atomic,
            'coordinators': coordinators_found,
            'action_count': len(found_verbs),
            'actions': found_verbs,
            'confidence': 0.7 if is_non_atomic else 0.3
        }
    
    def _extract_verb_phrase(self, verb_token) -> str:
        """
        Extract verb phrase from a verb token.
        
        Args:
            verb_token: spaCy token
            
        Returns:
            Verb phrase string
        """
        # Get verb and its direct object
        phrase_parts = [verb_token.text]
        
        for child in verb_token.children:
            if child.dep_ in ['dobj', 'attr', 'prep', 'pobj']:
                phrase_parts.append(child.text)
                # Get grandchildren
                for grandchild in child.children:
                    if grandchild.dep_ in ['pobj', 'attr']:
                        phrase_parts.append(grandchild.text)
        
        return ' '.join(phrase_parts)
    
    def _get_word_context(self, text: str, word: str, window: int = 50) -> str:
        """
        Get context around a word.
        
        Args:
            text: Full text
            word: Word to find context for
            window: Number of characters before/after
            
        Returns:
            Context string
        """
        text_lower = text.lower()
        word_lower = word.lower()
        
        # Find word position
        pos = text_lower.find(word_lower)
        if pos == -1:
            return text[:100]
        
        start = max(0, pos - window)
        end = min(len(text), pos + len(word) + window)
        
        context = text[start:end]
        if start > 0:
            context = '...' + context
        if end < len(text):
            context = context + '...'
        
        return context
    
    def _has_measurable_context(self, context: str) -> bool:
        """
        Check if context contains measurable indicators.
        
        Args:
            context: Text context
            
        Returns:
            True if measurable indicators found
        """
        context_lower = context.lower()
        
        # Check for numbers
        if re.search(r'\d+', context_lower):
            return True
        
        # Check for measurable indicators
        for indicator in self.MEASURABLE_INDICATORS:
            if indicator in context_lower:
                return True
        
        return False


if __name__ == "__main__":
    # Test the detector
    detector = RequirementDetector(use_spacy=False)
    
    test_req = {
        'req_id': 'TEST-1',
        'text': 'The system shall provide the best performance and validate user input.'
    }
    
    comp_result = detector.detect_comparatives(test_req)
    print("Comparative detection:", comp_result)
    
    non_atomic_result = detector.detect_non_atomic(test_req)
    print("Non-atomic detection:", non_atomic_result)
