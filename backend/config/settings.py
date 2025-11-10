"""
Configuration settings for the application
"""

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyCgp8ONPjotBtYxyDKejaOX3IT6Jz5sWRY"
GEMINI_MODEL = "gemini-2.5-flash"
"""
Configuration settings for the application
"""



# File patterns to analyze - UPDATED TO INCLUDE ALL DOCUMENT TYPES
FILE_PATTERNS = ['*.txt', '*.srs', '*.req', '*.md', '*.pdf', '*.doc', '*.docx', '*.rtf']

# POS Tags for comparative/superlative detection
COMPARATIVE_POS_TAGS = ['JJR', 'RBR']  # Adjective/Adverb comparative
SUPERLATIVE_POS_TAGS = ['JJS', 'RBS']  # Adjective/Adverb superlative

# Comparative keywords
COMPARATIVE_KEYWORDS = {
    'better', 'worse', 'faster', 'slower', 'larger', 'smaller',
    'higher', 'lower', 'greater', 'lesser', 'easier', 'harder',
    'stronger', 'weaker', 'cheaper', 'costlier', 'simpler',
    'more efficient', 'less efficient', 'more reliable', 'less reliable',
    'more', 'less', 'more secure', 'less secure'
}

SUPERLATIVE_KEYWORDS = {
    'best', 'worst', 'fastest', 'slowest', 'largest', 'smallest',
    'highest', 'lowest', 'greatest', 'least', 'easiest',
    'hardest', 'strongest', 'weakest', 'cheapest', 'optimal',
    'optimum', 'maximum', 'minimum', 'most efficient', 'most reliable',
    'most', 'least', 'optimal'
}

COORDINATORS = ['and', 'or', 'as well as', 'along with', 'plus']
MODAL_VERBS = ['shall', 'must', 'should', 'will', 'required', 'needs to', 'shall not']