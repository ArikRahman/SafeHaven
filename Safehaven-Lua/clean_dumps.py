import shutil
import re
import os
from pathlib import Path

# --- CONFIGURATION ---
DUMPS_DIR = Path(r"./dumps")
ANCHOR_FILE_NAME = "scan1_Raw_0.bin"

def get_scan_index(filename):
    match = re.search(r'scan(\d+)_Raw_0\.bin', filename.name)
    return int(match.group(1)) if match else None

def main():
    if not DUMPS_DIR.exists():
        print(f"Error: Directory {DUMPS_DIR} not found.")
        return

    anchor_file = DUMPS_DIR / ANCHOR_FILE_NAME

    # 1. Establish the Timeline Anchor
    if not anchor_file.exists():
        print(f"[ERROR] Anchor file '{ANCHOR_FILE_NAME}' not found!")
        print("Cannot determine the 'new' session time without scan1. Aborting.")
        return

    anchor_mtime = anchor_file.stat().st_mtime
    print(f"Anchor found: {anchor_file.name}")
    print(f"Session Start Time: {os.path.getmtime(anchor_file)}")
    
    # 2. Delete Older Files
    all_files = list(DUMPS_DIR.glob("scan*_Raw_0.bin"))
    
    print("\n--- Cleaning Files Older than scan1 ---")
    deleted_count = 0
    
    for f in all_files:
        # Skip the anchor itself
        if f.name == ANCHOR_FILE_NAME:
            continue
            
        # If file is strictly older than scan1, delete it
        if f.stat().st_mtime < anchor_mtime:
            # Check difference to avoid sub-second jitter issues if necessary, 
            # but usually 'stale' files are seconds/minutes older.
            time_diff = anchor_mtime - f.stat().st_mtime
            print(f"[DELETE] {f.name} (Older by {time_diff:.2f}s)")
            f.unlink()
            deleted_count += 1
    
    if deleted_count == 0:
        print("No old files found.")

    # 3. Forward Fill (Pad Missing)
    # Re-scan directory to see what's left
    valid_files = list(DUMPS_DIR.glob("scan*_Raw_0.bin"))
    if not valid_files:
        return

    indices = [get_scan_index(f) for f in valid_files if get_scan_index(f) is not None]
    if not indices: 
        return
        
    max_idx = max(indices)
    
    print(f"\n--- Padding Gaps (Up to scan{max_idx}) ---")
    
    # Start from 2 because 1 is our anchor and must exist for this script to run
    for i in range(2, max_idx + 1):
        curr_file = DUMPS_DIR / f"scan{i}_Raw_0.bin"
        prev_file = DUMPS_DIR / f"scan{i-1}_Raw_0.bin"
        
        if not curr_file.exists():
            if prev_file.exists():
                print(f"[PAD] Missing {curr_file.name}. Copying from {prev_file.name}...")
                shutil.copy2(prev_file, curr_file)
            else:
                print(f"[WARN] Cannot pad {curr_file.name}. Predecessor {prev_file.name} is also missing.")

    print("\nDone.")

if __name__ == "__main__":
    main()
