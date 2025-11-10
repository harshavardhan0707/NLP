"""
Gemini API integration for requirement suggestions and rewriting
"""

import os
from typing import Optional
from config.settings import GEMINI_API_KEY, GEMINI_MODEL

class GeminiSuggester:
    def __init__(self, api_key: str = GEMINI_API_KEY):
        self.api_key = api_key
        self.enabled = False
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client with best available library"""
        if not self.api_key:
            print("Warning: No Gemini API key provided. AI suggestions disabled.")
            return
        
        # Try google.genai (new style)
        try:
            from google import genai
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.client_style = 'genai_client'
                self.enabled = True
                print("Gemini client initialized successfully (new style)")
                return
            except Exception as e:
                print(f"Failed to initialize new Gemini client: {e}")
        except ImportError:
            pass
        
        # Try legacy google.generativeai
        try:
            import google.generativeai as genai_old
            genai_old.configure(api_key=self.api_key)
            self.client = genai_old
            self.client_style = 'generativeai_legacy'
            self.enabled = True
            print("Gemini client initialized successfully (legacy style)")
            return
        except ImportError:
            pass
        
        print("Warning: Could not initialize Gemini client. AI suggestions disabled.")
    
    def get_suggestions(self, sentence: str, issue_type: str, keyword: str) -> Optional[str]:
        """
        Get AI-powered suggestions for requirement improvement
        """
        if not self.enabled or not self.client:
            return None
        
        prompt = self._build_prompt(sentence, issue_type, keyword)
        
        try:
            if self.client_style == 'genai_client':
                response = self.client.models.generate_content(
                    model=GEMINI_MODEL, 
                    contents=prompt
                )
                return self._extract_response_text(response)
            
            elif self.client_style == 'generativeai_legacy':
                # Try different methods for legacy client
                try:
                    model = self.client.GenerativeModel(GEMINI_MODEL)
                    response = model.generate_content(prompt)
                    return response.text.strip()
                except Exception:
                    try:
                        response = self.client.generate_text(prompt)
                        return response.text.strip()
                    except Exception:
                        return None
        
        except Exception as e:
            print(f"Error getting Gemini suggestions: {e}")
            return None
    
    def _build_prompt(self, sentence: str, issue_type: str, keyword: str) -> str:
        """Build prompt for Gemini based on issue type"""
        
        if issue_type in ['comparative', 'superlative']:
            return f"""As a requirements engineering expert, analyze and improve this requirement:

ORIGINAL REQUIREMENT: "{sentence}"
ISSUE: Contains {issue_type} term "{keyword}" which makes it vague and hard to test.

Please provide:
1. IMPROVED VERSION: [Rewrite the requirement to be specific, measurable, and testable]
2. EXPLANATION: [Briefly explain why the improved version is better]
3. TEST SCENARIO: [Suggest how this could be tested]

Focus on making it quantifiable with clear metrics, thresholds, or baseline comparisons."""

        else:  # non-atomic
            return f"""As a requirements engineering expert, analyze and improve this requirement:

ORIGINAL REQUIREMENT: "{sentence}"
ISSUE: Non-atomic requirement with multiple conditions/actions joined by "{keyword}".

Please provide:
1. SPLIT REQUIREMENTS: [Split into 2-3 atomic requirements, each independently testable]
2. EXPLANATION: [Briefly explain why atomic requirements are better]
3. FORMAT: Use "REQ-1:", "REQ-2:" etc. for each atomic requirement.

Ensure each requirement is clear, concise, and independently verifiable."""
    
    def _extract_response_text(self, response) -> str:
        """Extract text from Gemini response object"""
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        
        try:
            return response.output[0].content[0].text.strip()
        except (AttributeError, IndexError, KeyError):
            pass
        
        try:
            return str(response).strip()
        except Exception:
            return "No suggestion available"