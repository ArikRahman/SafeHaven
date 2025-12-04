# Motor Test Script Documentation

This document outlines the usage and arguments for `motorTest_rev10.py`.

## Modes

### Next Path Segment
Executes the next defined vector in the path list.
**Command:** `next`
**Usage:** `python3 motorTest_rev10.py next`

### Return to Origin
Moves the gantry to the defined starting position (0,0).
**Command:** `origin`
**Usage:** `python3 motorTest_rev10.py origin`

### Arcade Mode
Enters an interactive terminal session for live manual control.
**Command:** `arcade`
**Usage:** `python3 motorTest_rev10.py arcade`
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
- `python3 motorTest_rev10.py up 100`
- `python3 motorTest_rev10.py right=200`
- `python3 motorTest_rev10.py go left 50`

## Configuration Arguments

### Margin
Defines the safety buffer distance from the physical axis limits.
**Flag:** `--margin=[pixels]`
**Default:** 200
**Constraint:** Must be a positive integer.
**Example:** `python3 motorTest_rev10.py origin --margin=50`

### Step
Defines the default travel distance for directional commands when no distance is provided.
**Flag:** `--step=[pixels]`
**Default:** 200
**Constraint:** Must be a positive integer.
**Example:** `python3 motorTest_rev10.py up --step=50`

### Force
Disables safety margin constraints.
Disables position saving to disk.
**Flag:** `--force`
**Usage:** `python3 motorTest_rev10.py left 1000 --force`

## Files

### position.txt
Stores the last known X/Y coordinates.
Updated automatically after every move (unless `--force` is used).

### current_index.txt
Stores the index of the current position within the pre-defined path list.
Used by the `next` command to track progress.
