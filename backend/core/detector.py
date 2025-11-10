"""
SpaCy-based POS tagger and requirement detector
"""

import re
import spacy
from typing import List, Dict, Tuple
from config.settings import *

class RequirementDetector:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            print("Error loading spaCy model. Please install: python -m spacy download en_core_web_sm")
            raise e
        
        # Regex patterns for quantified comparatives
        number = r'(?:\d+(?:\.\d+)?)'
        unit = r'(?:ms|s|sec|secs|seconds|minutes|mins|hours|hr|hrs|mb|gb|kb|%|percent|bps|tps|requests/s|rps)'
        
        self.quantified_patterns = [
            re.compile(rf'\b(?:more|less|greater|fewer|higher|lower)\s+than\s+{number}\s*{unit}\b', re.I),
            re.compile(rf'\b(?:more|less|greater|fewer|higher|lower)\s+than\s+{number}\b', re.I),
            re.compile(rf'\b(?:>|<|>=|<=)\s*{number}\s*{unit}\b'),
            re.compile(rf'\b(?:>|<|>=|<=)\s*{number}\b'),
            re.compile(rf'\bwithin\s+{number}\s*{unit}\b', re.I),
            re.compile(rf'\bat\s+(?:least|most)\s+{number}\s*{unit}\b', re.I),
        ]

    def is_quantified_comparative(self, text: str) -> bool:
        """Check if text contains quantified comparative expressions"""
        for pattern in self.quantified_patterns:
            if pattern.search(text):
                return True
        return False

    def detect_comparatives_superlatives(self, text: str, doc_name: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Detect comparative and superlative terms using POS tagging
        Returns: (comparatives_list, superlatives_list)
        """
        doc = self.nlp(text)
        comparatives = []
        superlatives = []
        
        for sent_idx, sent in enumerate(doc.sents, 1):
            sent_text = sent.text.strip()
            
            for token in sent:
                token_lower = token.text.lower()
                
                # Check for multi-word expressions
                bigram = None
                if token.i < len(sent) - 1:
                    bigram = f"{token.text.lower()} {token.nbor(1).text.lower()}"
                
                # Comparative detection
                if (token_lower in COMPARATIVE_KEYWORDS or 
                    (bigram and bigram in COMPARATIVE_KEYWORDS) or
                    token.tag_ in COMPARATIVE_POS_TAGS):
                    
                    keyword = bigram if (bigram and bigram in COMPARATIVE_KEYWORDS) else token_lower
                    
                    if self._is_valid_comparative_context(token, sent):
                        comparatives.append({
                            'document': doc_name,
                            'sentence_num': sent_idx,
                            'sentence': sent_text,
                            'keyword': keyword,
                            'type': 'comparative',
                            'pos_tag': token.tag_
                        })
                
                # Superlative detection
                if (token_lower in SUPERLATIVE_KEYWORDS or 
                    (bigram and bigram in SUPERLATIVE_KEYWORDS) or
                    token.tag_ in SUPERLATIVE_POS_TAGS):
                    
                    keyword = bigram if (bigram and bigram in SUPERLATIVE_KEYWORDS) else token_lower
                    
                    if self._is_valid_superlative_context(token, sent):
                        superlatives.append({
                            'document': doc_name,
                            'sentence_num': sent_idx,
                            'sentence': sent_text,
                            'keyword': keyword,
                            'type': 'superlative',
                            'pos_tag': token.tag_
                        })
        
        return comparatives, superlatives

    def detect_non_atomic_requirements(self, text: str, doc_name: str) -> List[Dict]:
        """Detect non-atomic requirements using coordinators and verb counting"""
        doc = self.nlp(text)
        non_atomic = []
        
        for sent_idx, sent in enumerate(doc.sents, 1):
            sent_text = sent.text.strip()
            sent_lower = sent_text.lower()
            
            # Check if it's a requirement (contains modal verbs)
            has_modal = any(modal in sent_lower for modal in MODAL_VERBS)
            if not has_modal:
                continue
            
            # Check for coordinators
            for coord in COORDINATORS:
                pattern = r'\b' + re.escape(coord) + r'\b'
                matches = list(re.finditer(pattern, sent_lower))
                
                if matches:
                    # Count action verbs
                    action_verbs = [
                        t for t in sent 
                        if t.pos_ == 'VERB' and t.dep_ not in ('aux', 'auxpass')
                    ]
                    
                    if len(action_verbs) >= 2 or len(matches) >= 2:
                        non_atomic.append({
                            'document': doc_name,
                            'sentence_num': sent_idx,
                            'sentence': sent_text,
                            'coordinator': coord,
                            'coordinator_count': len(matches),
                            'verb_count': len(action_verbs)
                        })
                        break
        
        return non_atomic

    def _is_valid_comparative_context(self, token, sent) -> bool:
        """Check if comparative is problematic (vague)"""
        sent_text = sent.text.lower()
        
        # If quantified, it's acceptable
        if self.is_quantified_comparative(sent_text):
            return False
        
        # POS-based detection
        if token.tag_ in COMPARATIVE_POS_TAGS:
            return True
        
        # Handle 'more', 'less' + adjective/adverb
        if token.text.lower() in ['more', 'less']:
            try:
                next_token = token.nbor(1)
                if next_token.pos_ in ['ADJ', 'ADV']:
                    return True
            except IndexError:
                pass
        
        return False

    def _is_valid_superlative_context(self, token, sent) -> bool:
        """Check if superlative is problematic (vague)"""
        sent_text = sent.text.lower()
        
        # If quantified, it's acceptable
        if self.is_quantified_comparative(sent_text):
            return False
        
        # POS-based detection
        if token.tag_ in SUPERLATIVE_POS_TAGS:
            return True
        
        # Handle 'most', 'least' + adjective/adverb
        if token.text.lower() in ['most', 'least']:
            try:
                next_token = token.nbor(1)
                if next_token.pos_ in ['ADJ', 'ADV']:
                    return True
            except IndexError:
                pass
        
        # Specific superlative keywords
        if token.text.lower() in ['optimal', 'optimum', 'best', 'worst']:
            return True
        
        return False