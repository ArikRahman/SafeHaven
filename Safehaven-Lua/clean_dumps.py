import os
import shutil
import re
from pathlib import Path
from datetime import datetime

# CONFIGURATION
DUMPS_DIR = Path(r"./dumps")  # Adjust path to your dumps folder
TIME_THRESHOLD_SEC = 60       # Files older than this (relative to newest file) are considered 'old'

def get_scan_index(filename):
    """Extracts index from 'scanX_Raw_0.bin'."""
    match = re.search(r'scan(\d+)_Raw_0\.bin', filename.name)
    return int(match.group(1)) if match else None

def main():
    if not DUMPS_DIR.exists():
        print(f"Error: Directory {DUMPS_DIR} not found.")
        return

    # 1. Gather all scan files
    all_files = list(DUMPS_DIR.glob("scan*_Raw_0.bin"))
    if not all_files:
        print("No scan files found.")
        return

    # 2. Identify the 'Fresh' Timestamp
    # We assume the newest file represents the current valid session.
    newest_file = max(all_files, key=lambda f: f.stat().st_mtime)
    latest_mtime = newest_file.stat().st_mtime
    print(f"Latest scan detected: {newest_file.name} ({datetime.fromtimestamp(latest_mtime)})")

    # 3. Identify and Remove Old Files
    valid_files = []
    
    # Sort by index to process sequentially
    sorted_files = sorted(all_files, key=get_scan_index)
    
    # We need the range of indices to know where holes are
    max_index = get_scan_index(sorted_files[-1])
    min_index = get_scan_index(sorted_files[0])

    print("\n--- Cleaning Stale Files ---")
    for file_path in sorted_files:
        mtime = file_path.stat().st_mtime
        age_diff = latest_mtime - mtime

        if age_diff > TIME_THRESHOLD_SEC:
            print(f"[DELETE] {file_path.name}: {int(age_diff)}s older than latest.")
            file_path.unlink()  # Delete the file
        else:
            valid_files.append(file_path)

    # 4. Pad Missing Scans (Forward Fill)
    print("\n--- Padding Missing Scans ---")
    
    # We iterate through the expected sequence 
    for i in range(min_index, max_index + 1):
        current_file = DUMPS_DIR / f"scan{i}_Raw_0.bin"
        prev_file = DUMPS_DIR / f"scan{i-1}_Raw_0.bin"

        if not current_file.exists():
            if prev_file.exists():
                print(f"[PAD] Missing {current_file.name}. Copying from {prev_file.name}...")
                shutil.copy2(prev_file, current_file)
            else:
                print(f"[WARN] Cannot pad {current_file.name}. Previous file {prev_file.name} is also missing.")

    print("\nDataset repair complete.")

if __name__ == "__main__":
    main()
