"""
Cache manager to store processed file results and avoid reprocessing
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class CacheManager:
    def __init__(self, cache_dir: str = "processed/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_file = self.cache_dir / "file_cache.json"
        self.cache_data = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file or create new cache"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save cache: {e}")
    
    def get_file_hash(self, file_path: Path) -> str:
        """Generate hash of file content and metadata"""
        try:
            stat = file_path.stat()
            # Use file size and modification time for quick comparison
            content = f"{file_path.name}_{stat.st_size}_{stat.st_mtime}"
            return hashlib.md5(content.encode()).hexdigest()
        except Exception:
            return str(file_path)
    
    def is_file_processed(self, file_path: Path) -> bool:
        """Check if file has been processed and not modified"""
        if not file_path.exists():
            return False
        
        file_hash = self.get_file_hash(file_path)
        cached = self.cache_data.get(str(file_path))
        
        if cached and cached.get('hash') == file_hash:
            return True
        return False
    
    def get_cached_results(self, file_path: Path) -> Optional[Dict]:
        """Get cached analysis results for file"""
        if self.is_file_processed(file_path):
            return self.cache_data[str(file_path)].get('results')
        return None
    
    def save_results(self, file_path: Path, results: Dict):
        """Save analysis results to cache"""
        file_hash = self.get_file_hash(file_path)
        
        self.cache_data[str(file_path)] = {
            'hash': file_hash,
            'last_processed': datetime.now().isoformat(),
            'results': results
        }
        self._save_cache()
    
    def get_processed_files_count(self) -> int:
        """Get number of files in cache"""
        return len(self.cache_data)
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache_data = {}
        self._save_cache()
        print("Cache cleared successfully")
    
    def remove_from_cache(self, file_path: Path):
        """Remove specific file from cache"""
        file_str = str(file_path)
        if file_str in self.cache_data:
            del self.cache_data[file_str]
            self._save_cache()
            print(f"Removed {file_path.name} from cache")