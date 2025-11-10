"""
File processing utilities with support for multiple file formats
"""

from pathlib import Path
from typing import List
import os
from config.settings import FILE_PATTERNS

class FileProcessor:
    @staticmethod
    def find_requirement_files(directory_path: str) -> List[Path]:
        """Find all requirement files in directory"""
        path = Path(directory_path)
        if not path.exists():
            raise FileNotFoundError(f"Directory '{directory_path}' not found")
        
        files = []
        for pattern in FILE_PATTERNS:
            files.extend(path.rglob(pattern))
            files.extend(path.rglob(pattern.upper()))  # Also check uppercase
        
        # Remove duplicates and sort
        files = list(set(files))
        files.sort()
        
        print(f"DEBUG: Found {len(files)} files with patterns: {[f.name for f in files]}")
        return files
    
    @staticmethod
    def read_file(file_path: Path) -> str:
        """Read file content with support for multiple formats"""
        try:
            file_extension = file_path.suffix.lower()
            
            if file_extension in ['.txt', '.srs', '.req', '.md', '.rtf']:
                # Text-based files
                return file_path.read_text(encoding='utf-8', errors='ignore')
            
            elif file_extension in ['.pdf']:
                # PDF files
                return FileProcessor._read_pdf(file_path)
            
            elif file_extension in ['.doc', '.docx']:
                # Word documents
                return FileProcessor._read_word_document(file_path)
            
            else:
                # Try to read as text for unknown formats
                print(f"Warning: Unknown file format {file_extension}, attempting to read as text")
                return file_path.read_text(encoding='utf-8', errors='ignore')
                
        except Exception as e:
            raise Exception(f"Error reading {file_path}: {e}")
    
    @staticmethod
    def _read_pdf(file_path: Path) -> str:
        """Extract text from PDF files"""
        try:
            # Try PyPDF2 first
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                pass
            
            # Try pdfplumber as alternative
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                return text
            except ImportError:
                pass
            
            # Fallback: use fitz (PyMuPDF)
            try:
                import fitz
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            except ImportError:
                pass
            
            # If no PDF libraries available, return empty with warning
            print(f"Warning: No PDF library installed. Install PyPDF2: pip install PyPDF2")
            return f"[PDF file: {file_path.name} - Install PyPDF2 to extract text]"
            
        except Exception as e:
            return f"[Error reading PDF {file_path.name}: {str(e)}]"
    
    @staticmethod
    def _read_word_document(file_path: Path) -> str:
        """Extract text from Word documents"""
        try:
            # Try python-docx for .docx files
            if file_path.suffix.lower() == '.docx':
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    return text
                except ImportError:
                    pass
            
            # For .doc files or if python-docx not available
            try:
                import textract
                text = textract.process(str(file_path)).decode('utf-8')
                return text
            except ImportError:
                pass
            
            # Fallback for .doc files (older format)
            try:
                import win32com.client
                if file_path.suffix.lower() == '.doc':
                    word = win32com.client.Dispatch("Word.Application")
                    word.visible = False
                    doc = word.Documents.Open(str(file_path.absolute()))
                    text = doc.Content.Text
                    doc.Close()
                    word.Quit()
                    return text
            except ImportError:
                pass
            
            # If no Word libraries available
            print(f"Warning: No Word document library installed. Install python-docx: pip install python-docx")
            return f"[Word document: {file_path.name} - Install python-docx to extract text]"
            
        except Exception as e:
            return f"[Error reading Word document {file_path.name}: {str(e)}]"
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported file formats"""
        return FILE_PATTERNS