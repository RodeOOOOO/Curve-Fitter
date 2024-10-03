import os
import glob

class FileSearcher:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.preloaded_files = self.preload_files()

    def preload_files(self):
        print(f"Preloading files from {self.base_dir}...")
        search_path = os.path.join(self.base_dir, '**', '*.xlsx')
        print(f"Using search pattern: {search_path}")
        
        preloaded_files = glob.glob(search_path, recursive=True)
        
        if not preloaded_files:
            print(f"No files found with pattern: {search_path}")
        else:
            print(f"Found {len(preloaded_files)} files.")
        
        return preloaded_files

    def search_files(self, pattern):
        print(f"Searching for files with pattern: {pattern}")
        matched_files = [f for f in self.preloaded_files if os.path.basename(f) == pattern]
        print(f"Found {len(matched_files)} files matching pattern: {pattern}")
        return matched_files
