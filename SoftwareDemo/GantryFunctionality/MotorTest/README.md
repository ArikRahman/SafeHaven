# Motor Test Script Documentation

This document outlines the usage and arguments for `motorTest_rev11.py`.

## Setup & Prerequisites

**Hardware:** Raspberry Pi 5  
**OS:** Raspberry Pi OS (Bookworm)

### Virtual Environment & Permissions
This script requires root privileges (`sudo`) to access hardware PWM and GPIO registers. It also relies on packages installed in a local virtual environment.

To run the script, use the full path to the virtual environment's Python executable with `sudo`:

```bash
sudo ./.venv/bin/python3 motorTest_rev11.py [command]
```

*Note: Ensure you are in the `MotorTest` directory.*

## Gantry Dimensions & Units
* **Physical Dimensions:** 675mm x 675mm
* **Coordinate System:** 0 to 10000 "pixels"
* **Conversion:** 1 pixel ≈ 0.0675 mm
* **Default Step:** 200 pixels ≈ 13.5 mm

## Modes

### Next Path Segment
Executes the next defined vector in the path list.
**Command:** `next`
**Usage:** `sudo ./.venv/bin/python3 motorTest_rev11.py next`

### Return to Origin
Moves the gantry to the defined starting position (0,0).
**Command:** `origin`
**Usage:** `sudo ./.venv/bin/python3 motorTest_rev11.py origin`

### Arcade Mode
Enters an interactive terminal session for live manual control.
**Command:** `arcade`
**Usage:** `sudo ./.venv/bin/python3 motorTest_rev11.py arcade`
**Controls:**
- `W` / `Up Arrow`: Move Up
- `S` / `Down Arrow`: Move Down
- `A` / `Left Arrow`: Move Left
- `D` / `Right Arrow`: Move Right
- `Q`: Quit
- `P`: Print current position

## Directional Commands

Moves the gantry a specific distance in one direction.

**Syntax:** `[direction] [distance]`
**Directions:** `up`, `down`, `left`, `right`

**Examples:**
- `sudo ./.venv/bin/python3 motorTest_rev11.py up 100`
- `sudo ./.venv/bin/python3 motorTest_rev11.py right=200`
- `sudo ./.venv/bin/python3 motorTest_rev11.py go left 50`

## Configuration Arguments

### Margin
Defines the safety buffer distance from the physical axis limits.
**Flag:** `--margin=[pixels]`
**Default:** 200
**Constraint:** Must be a positive integer.
**Example:** `sudo ./.venv/bin/python3 motorTest_rev11.py origin --margin=50`

### Step
Defines the default travel distance for directional commands when no distance is provided.
**Flag:** `--step=[pixels]`
**Default:** 200
**Constraint:** Must be a positive integer.
**Example:** `sudo ./.venv/bin/python3 motorTest_rev11.py up --step=50`

### Force
Disables safety margin constraints.
Disables position saving to disk.
**Flag:** `--force`
**Usage:** `sudo ./.venv/bin/python3 motorTest_rev11.py left 1000 --force`

## Files

### position.txt
Stores the last known X/Y coordinates.
Updated automatically after every move (unless `--force` is used).

### current_index.txt
Stores the index of the current position within the pre-defined path list.
Used by the `next` command to track progress.
