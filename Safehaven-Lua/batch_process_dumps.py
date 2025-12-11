import subprocess
import os
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description="Batch process SAR dumps.")
parser.add_argument("--dump", type=int, help="Dump ID to process (e.g., 65)")
args = parser.parse_args()

# List of dump IDs to process
if args.dump is not None:
    dump_ids = [args.dump]
else:
    dump_ids = [31]

# Base command parameters
script_name = "mainSARneuronauts2py_rev3_2.py"
z_start = "300"
z_end = "400"
z_step = "1"

for dump_id in dump_ids:
    folder_name = f"dumps{dump_id}"
    output_dir = f"../Safehaven-Classification/output_images/images{dump_id}"
    
    print(f"Processing {folder_name}...")
    
    command = [
        "uv", "run", script_name,
        "--folder", folder_name,
        "--z_start", z_start,
        "--z_end", z_end,
        "--zstep", z_step,
        "--sar_dump", output_dir,
        "--silent"
    ]
    
    try:
        # shell=True might be needed on Windows if uv is a batch file or similar, 
        # but usually subprocess handles executables fine. 
        # On Windows 'uv' might need 'uv.exe' or shell=True if it's not in PATH directly as an exe.
        # Assuming 'uv' works as it did in the user's terminal.
        subprocess.run(command, check=True)
        print(f"Successfully processed {folder_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {folder_name}: {e}")

print("Batch processing complete.")
