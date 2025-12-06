#!/usr/bin/env python3
import subprocess

# Scan parameters (from your mmWave config)
X_DIST_MM    = 280       # total X travel per line
Y_STEP_MM    = 8         # Y increment per slice
NUM_SLICES   = 40        # number of Y slices
X_SPEED_MMS  = 36      # required X speed in mm/s (280 mm in 16 s)
Y_SPEED_MMS  = 36         # choose Y speed; Y motion is between frames

MOTOR_SCRIPT = "motorTest_rev13.py"

def run_motor(**kwargs):
    """
    Wrapper for: python motorTest_rev13.py down=10mm speed=1mms style args
    """
    args = ["python", MOTOR_SCRIPT]
    for k, v in kwargs.items():
        args.append(f"{k}={v}")
    print("Running:", " ".join(args))
    subprocess.run(args, check=True)

def raster_line(direction="right"):
    """
    One measurement line:
    - Move full X span at 17.5 mm/s in the given direction
    - Do NOT return; next line will scan opposite way
    """
    if direction == "right":
        run_motor(right=f"{X_DIST_MM}mm", speed=f"{X_SPEED_MMS}mms")
    else:
        run_motor(left=f"{X_DIST_MM}mm", speed=f"{X_SPEED_MMS}mms")

def main():
    try:
        direction = "right"  # first line: left -> right
        for i in range(NUM_SLICES):
            print(f"Slice {i+1}/{NUM_SLICES}, direction={direction}")
            raster_line(direction=direction)

            # Move up for next Y slice, except after last
            if i < NUM_SLICES - 1:
                run_motor(up=f"{Y_STEP_MM}mm", speed=f"{Y_SPEED_MMS}mms")

            # Flip X direction for classic raster
            direction = "left" if direction == "right" else "right"
    except KeyboardInterrupt:
        print("\nInterrupted! Stopping motors...")
        subprocess.run(["python", MOTOR_SCRIPT, "stop"])
        print("Motors stopped.")

if __name__ == "__main__":
    main()
