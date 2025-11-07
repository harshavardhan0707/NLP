"""
Requirement Splitter Module
Proposes splits for non-atomic requirements.
"""

import re
from typing import List, Dict, Tuple

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


class RequirementSplitter:
    """Split non-atomic requirements into atomic ones."""
    
    def __init__(self, use_spacy: bool = True):
        """
        Initialize splitter.
        
        Args:
            use_spacy: Whether to use spaCy for advanced NLP
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.nlp = None
        
        if self.use_spacy:
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except (OSError, NameError):
                print("Warning: spaCy model not found. Falling back to regex-based splitting.")
                self.use_spacy = False
    
    def split_requirement(self, requirement: Dict, detection_result: Dict) -> List[Dict]:
        """
        Split a non-atomic requirement into atomic parts.
        
        Args:
            requirement: Original requirement dictionary
            detection_result: Result from non-atomic detection
            
        Returns:
            List of split requirements
        """
        if not detection_result['is_non_atomic']:
            return [requirement]  # Already atomic
        
        text = requirement['text']
        coordinators = detection_result['coordinators']
        
        if self.use_spacy and self.nlp:
            return self._split_with_spacy(requirement, coordinators)
        else:
            return self._split_with_regex(requirement, coordinators)
    
    def _split_with_spacy(self, requirement: Dict, coordinators: List[str]) -> List[Dict]:
        """
        Split requirement using spaCy NLP.
        
        Args:
            requirement: Original requirement
            coordinators: List of coordinator words found
            
        Returns:
            List of split requirements
        """
        text = requirement['text']
        doc = self.nlp(text)
        
        # Extract sentence structure
        subject = None
        modal = None
        verbs = []
        objects = []
        
        # Find subject (usually at the beginning)
        for token in doc:
            if token.dep_ in ['nsubj', 'nsubjpass']:
                subject = self._get_full_noun_phrase(token)
                break
        
        # Find modal verb
        for token in doc:
            if token.tag_ == 'MD':  # Modal verb
                modal = token.text
                break
        
        # Find main verbs and their objects
        for token in doc:
            if token.pos_ == 'VERB' and token.dep_ in ['ROOT', 'conj']:
                verb_phrase = self._extract_verb_and_object(token)
                if verb_phrase:
                    verbs.append(verb_phrase)
        
        # Create split requirements
        splits = []
        base_id = requirement['req_id']
        
        if not verbs:
            return [requirement]  # Cannot split
        
        for i, verb_phrase in enumerate(verbs):
            # Reconstruct sentence
            parts = []
            if subject:
                parts.append(subject)
            if modal:
                parts.append(modal)
            parts.append(verb_phrase)
            
            new_text = ' '.join(parts)
            
            # Clean up
            new_text = self._clean_split_text(new_text)
            
            splits.append({
                'req_id': f"{base_id}.{i+1}",
                'text': new_text,
                'source_file': requirement['source_file'],
                'parent_req_id': base_id,
                'split_index': i + 1,
                'total_splits': len(verbs)
            })
        
        return splits
    
    def _split_with_regex(self, requirement: Dict, coordinators: List[str]) -> List[Dict]:
        """
        Split requirement using regex patterns.
        
        Args:
            requirement: Original requirement
            coordinators: List of coordinator words found
            
        Returns:
            List of split requirements
        """
        text = requirement['text']
        
        # Find the main coordinator to split on
        main_coordinator = coordinators[0] if coordinators else 'and'
        
        # Split by coordinator
        pattern = rf'\s+{re.escape(main_coordinator)}\s+'
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        
        if len(parts) < 2:
            return [requirement]  # Cannot split
        
        # Try to extract common structure
        # Look for subject and modal at the beginning
        first_part = parts[0]
        subject_modal = self._extract_subject_modal(first_part)
        
        # Create split requirements
        splits = []
        base_id = requirement['req_id']
        
        for i, part in enumerate(parts):
            # If not the first part, add subject and modal
            if i > 0 and subject_modal:
                new_text = f"{subject_modal} {part}"
            else:
                new_text = part
            
            # Clean up
            new_text = self._clean_split_text(new_text)
            
            splits.append({
                'req_id': f"{base_id}.{i+1}",
                'text': new_text,
                'source_file': requirement['source_file'],
                'parent_req_id': base_id,
                'split_index': i + 1,
                'total_splits': len(parts)
            })
        
        return splits
    
    def _get_full_noun_phrase(self, token) -> str:
        """
        Get full noun phrase from a token.
        
        Args:
            token: spaCy token
            
        Returns:
            Full noun phrase
        """
        # Get all children that are part of the noun phrase
        phrase = []
        for child in token.lefts:
            if child.dep_ in ['det', 'amod', 'compound']:
                phrase.append(child.text)
        
        phrase.append(token.text)
        
        for child in token.rights:
            if child.dep_ in ['prep', 'pobj']:
                phrase.append(child.text)
        
        return ' '.join(phrase)
    
    def _extract_verb_and_object(self, verb_token) -> str:
        """
        Extract verb with its object and modifiers.
        
        Args:
            verb_token: spaCy token (verb)
            
        Returns:
            Verb phrase string
        """
        phrase = [verb_token.text]
        
        for child in verb_token.children:
            if child.dep_ in ['dobj', 'attr', 'acomp', 'prep', 'advmod', 'aux', 'auxpass']:
                phrase.append(child.text)
                # Add grandchildren
                for grandchild in child.children:
                    if grandchild.dep_ in ['pobj', 'det', 'amod']:
                        phrase.append(grandchild.text)
        
        return ' '.join(phrase)
    
    def _extract_subject_modal(self, text: str) -> str:
        """
        Extract subject and modal verb from text.
        
        Args:
            text: Text to extract from
            
        Returns:
            Subject and modal string
        """
        # Modal verbs
        modals = ['shall', 'will', 'must', 'should', 'may', 'can', 'could', 'would']
        
        text_lower = text.lower()
        
        for modal in modals:
            pattern = rf'(.+?\s+{modal})\s+'
            match = re.search(pattern, text_lower)
            if match:
                # Get the original case version
                start = match.start()
                end = match.end(1)
                return text[start:end]
        
        # If no modal found, try to get first few words (subject)
        words = text.split()
        if len(words) >= 3:
            return ' '.join(words[:3])
        
        return ''
    
    def _clean_split_text(self, text: str) -> str:
        """
        Clean up split requirement text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Capitalize first letter
        text = text.strip()
        if text:
            text = text[0].upper() + text[1:]
        
        # Ensure ends with period
        if text and not text.endswith('.'):
            text += '.'
        
        return text


if __name__ == "__main__":
    # Test the splitter
    splitter = RequirementSplitter(use_spacy=False)
    
    test_req = {
        'req_id': 'TEST-1',
        'text': 'The system shall validate and store user input.',
        'source_file': 'test.html'
    }
    
    detection = {
        'is_non_atomic': True,
        'coordinators': ['and']
    }
    
    splits = splitter.split_requirement(test_req, detection)
    for split in splits:
        print(f"{split['req_id']}: {split['text']}")
