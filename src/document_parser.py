"""
Universal Document Parser Module
Extracts requirements from HTML, PDF, DOC, DOCX, and RTF documents.
"""

import re
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Optional
import subprocess
import tempfile

# Try to import PDF parsing libraries
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from striprtf.striprtf import rtf_to_text
    RTF_AVAILABLE = True
except ImportError:
    RTF_AVAILABLE = False


class DocumentParser:
    """Parse multiple document formats and extract requirement statements."""
    
    # Modal verbs that indicate requirements
    MODAL_VERBS = ['shall', 'will', 'must', 'should', 'may', 'can', 'could']
    
    # Pattern to match requirement IDs
    REQ_ID_PATTERNS = [
        r'\b\d+\.\d+\.\d+\.\d+\b',      # 4.5.8.1
        r'\b\d+\.\d+\.\d+\b',           # 4.5.8
        r'\b\d+\.\d+\b',                 # 4.5
        r'\bR\d+\b',                     # R1, R23
        r'\bReq-?\d+\b',                 # Req1, Req-23
        r'\b[A-Z]{2,4}-\d+\b',          # REQ-123
        r'\b\[\d+\]',                    # [1], [23]
    ]
    
    def __init__(self):
        self.requirements = []
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check which document parsers are available."""
        self.supported_formats = ['.html', '.htm']
        
        if PDF_AVAILABLE:
            self.supported_formats.append('.pdf')
        if DOCX_AVAILABLE:
            self.supported_formats.extend(['.docx', '.doc'])
        if RTF_AVAILABLE:
            self.supported_formats.append('.rtf')
    
    def parse_document(self, filepath: str) -> List[Dict]:
        """
        Parse any supported document format and extract requirements.
        
        Args:
            filepath: Path to document file
            
        Returns:
            List of requirement dictionaries
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        suffix = path.suffix.lower()
        
        try:
            if suffix in ['.html', '.htm']:
                return self._parse_html(filepath)
            elif suffix == '.pdf':
                return self._parse_pdf(filepath)
            elif suffix == '.docx':
                return self._parse_docx(filepath)
            elif suffix == '.doc':
                return self._parse_doc(filepath)
            elif suffix == '.rtf':
                return self._parse_rtf(filepath)
            else:
                print(f"Warning: Unsupported format {suffix} for {path.name}")
                return []
        except Exception as e:
            print(f"Error parsing {path.name}: {str(e)}")
            return []
    
    def _parse_html(self, filepath: str) -> List[Dict]:
        """Parse HTML file."""
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        return self._extract_requirements(text, Path(filepath).name)
    
    def _parse_pdf(self, filepath: str) -> List[Dict]:
        """Parse PDF file."""
        if not PDF_AVAILABLE:
            print(f"Warning: PyPDF2 not installed. Skipping {Path(filepath).name}")
            return []
        
        try:
            text = ""
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return self._extract_requirements(text, Path(filepath).name)
        except Exception as e:
            print(f"Error reading PDF {Path(filepath).name}: {str(e)}")
            return []
    
    def _parse_docx(self, filepath: str) -> List[Dict]:
        """Parse DOCX file."""
        if not DOCX_AVAILABLE:
            print(f"Warning: python-docx not installed. Skipping {Path(filepath).name}")
            return []
        
        try:
            doc = DocxDocument(filepath)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return self._extract_requirements(text, Path(filepath).name)
        except Exception as e:
            print(f"Error reading DOCX {Path(filepath).name}: {str(e)}")
            return []
    
    def _parse_doc(self, filepath: str) -> List[Dict]:
        """Parse old DOC file using antiword or textutil."""
        try:
            # Try using antiword (Linux)
            result = subprocess.run(
                ['antiword', filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                text = result.stdout
                return self._extract_requirements(text, Path(filepath).name)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try textutil (Mac)
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp_path = tmp.name
            
            subprocess.run(
                ['textutil', '-convert', 'txt', '-output', tmp_path, filepath],
                check=True,
                timeout=30
            )
            
            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            Path(tmp_path).unlink()
            return self._extract_requirements(text, Path(filepath).name)
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            pass
        
        print(f"Warning: Cannot parse .doc file {Path(filepath).name}. Install 'antiword' or convert to .docx")
        return []
    
    def _parse_rtf(self, filepath: str) -> List[Dict]:
        """Parse RTF file."""
        if not RTF_AVAILABLE:
            print(f"Warning: striprtf not installed. Skipping {Path(filepath).name}")
            return []
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                rtf_content = f.read()
            
            text = rtf_to_text(rtf_content)
            return self._extract_requirements(text, Path(filepath).name)
        except Exception as e:
            print(f"Error reading RTF {Path(filepath).name}: {str(e)}")
            return []
    
    def _extract_requirements(self, text: str, source_file: str) -> List[Dict]:
        """Extract individual requirements from text."""
        requirements = []
        lines = text.split('\n')
        lines = [self._clean_text(line) for line in lines]
        lines = [line for line in lines if line]
        
        current_req = None
        req_counter = 1
        
        for i, line in enumerate(lines):
            has_modal = any(f' {verb} ' in f' {line.lower()} ' for verb in self.MODAL_VERBS)
            req_id = self._extract_requirement_id(line)
            
            if has_modal or req_id:
                if current_req and current_req['text']:
                    requirements.append(current_req)
                
                current_req = {
                    'req_id': req_id if req_id else f"REQ-{req_counter}",
                    'text': line,
                    'source_file': source_file,
                    'line_number': i + 1,
                    'has_modal': has_modal
                }
                req_counter += 1
            elif current_req and len(line) > 20:
                current_req['text'] += ' ' + line
        
        if current_req and current_req['text']:
            requirements.append(current_req)
        
        requirements = [req for req in requirements if len(req['text']) > 30]
        
        return requirements
    
    def _extract_requirement_id(self, text: str) -> Optional[str]:
        """Extract requirement ID from text."""
        for pattern in self.REQ_ID_PATTERNS:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace."""
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def parse_all_documents(self, directory: str) -> Dict[str, List[Dict]]:
        """
        Parse all supported documents in a directory.
        
        Args:
            directory: Path to directory containing requirement files
            
        Returns:
            Dictionary mapping filenames to requirement lists
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        results = {}
        
        # Find all supported files
        all_files = []
        for ext in self.supported_formats:
            all_files.extend(dir_path.glob(f'*{ext}'))
        
        print(f"\nFound {len(all_files)} files to process:")
        print(f"Supported formats: {', '.join(self.supported_formats)}\n")
        
        for doc_file in sorted(all_files):
            print(f"Parsing {doc_file.name}...")
            requirements = self.parse_document(str(doc_file))
            if requirements:
                results[doc_file.name] = requirements
                print(f"  ✓ Found {len(requirements)} requirements")
            else:
                print(f"  ⚠ No requirements found")
        
        return results


if __name__ == "__main__":
    # Test the parser
    parser = DocumentParser()
    print(f"Supported formats: {parser.supported_formats}")
    
    docs = parser.parse_all_documents('../data/req/')
    
    for filename, reqs in docs.items():
        print(f"\n{filename}: {len(reqs)} requirements")
        if reqs:
            print(f"First requirement: {reqs[0]['text'][:100]}...")
