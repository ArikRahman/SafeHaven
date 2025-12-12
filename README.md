# SafeHaven

SafeHaven is an automated system designed to detect human presence using computer vision and perform targeted Synthetic Aperture Radar (SAR) scans using a 2-axis gantry system.

## Project Overview

The system operates in the following sequence:
1.  **Detection**: A camera (PiCamera) captures the scene.
2.  **Identification**: YOLO (You Only Look Once) object detection identifies people in the frame.
3.  **Path Generation**: A "Snake Path" algorithm calculates an optimal scanning route for the gantry to cover the detected area.
4.  **Scanning**: The gantry moves a SAR sensor along the calculated path to acquire data.
5.  **Processing**: MATLAB scripts process the raw radar data to reconstruct images.

## Directory Structure

*   **SoftwareDemo/**: The main application code.
    *   `main.py`: Entry point for the integrated system.
    *   `PiCamera/`: Camera control and AI detection logic.
    *   `GantryFunctionality/`: Motor control, limit switches, and safety stop mechanisms.
    *   `SnakepathAlgorithm/`: Path generation logic.
*   **Arduino/**: Firmware for the microcontroller driving the stepper motors.
*   **MATLAB/**: Algorithms for SAR signal processing and image reconstruction.
*   **BoundaryBoxDetect/**: Standalone scripts for testing object detection and coordinate mapping.
*   **SnakePathAlgorithm/**: Standalone development of the path planning algorithm.

## Core Files & Key Scripts

### Radar Scanning (Lua)
*   **`Safehaven-Lua/sar_scan_rev15.lua`**
    *   **Purpose:** The main automation script run within TI mmWave Studio. It controls the radar parameters and triggers the scanning sequence.

### Data Processing & SAR Generation
*   **`Safehaven-Lua/mainSARneuronauts2py_rev3_2.py`**
    *   **Purpose:** The primary script for processing raw binary radar data into visual Synthetic Aperture Radar (SAR) images.
    *   **Arguments:**
        *   `--folder`: Folder containing scan data (default: 'dumps').
        *   `--zindex`: Single Z slice to process (e.g., '300', '300mm', '0.3m').
        *   `--zstep`: Step size for Z sweep (e.g., '3', '3mm', '0.003m').
        *   `--zstart` / `--z_start`: Start Z value for sweep (e.g., '300', '300mm', '0.3m').
        *   `--zend` / `--z_end`: End Z value for sweep (e.g., '800', '800mm', '0.8m').
        *   `--xyonly`: Only generate the X-Y image; skip X-Z and Y-Z heatmaps.
        *   `--3d_scatter`: Generate interactive 3D scatter plot.
        *   `--3d_scatter_intensity`: Initial percentile threshold for 3D scatter plot (0-100, default: 95.0).
        *   `--plotly`: Generate interactive Plotly HTML with Z-slider instead of Matplotlib window.
        *   `--mat_plot_lib`: Force use of Matplotlib for visualization, overriding --plotly.
        *   `--sar_dump`: Directory to dump processed SAR images (Z-slices).
        *   `--silent`: Suppress all graphical output and heatmap generation.
        *   `--algo`: Reconstruction algorithm: 'mf' (Matched Filter), 'fista', or 'bpa' (default: 'mf').
        *   `--fista_iters`: Number of FISTA iterations (default: 20).
        *   `--fista_lambda`: FISTA regularization ratio (0.0 to 1.0) (default: 0.05).
        *   `--frames_in_x`: Number of frames in X dimension (default: 800).
        *   `--frames_in_y`: Number of frames in Y dimension (default: 40).

*   **`Safehaven-Lua/batch_process_dumps.py`**
    *   **Purpose:** Handles pre-processing of data dumps (grayscaling, normalization) to prepare them for the Machine Learning pipeline.

### Motor Control
*   **`SoftwareDemo/GantryFunctionality/MotorTest/motorTest_rev13.py`**
    *   **Purpose:** The driver script for the 2-axis gantry system. It interprets commands (often from the Lua script or Main Orchestrator) to move the stepper motors.

### AI & Computer Vision
*   **`Safehaven-Classification/weapon_classifier.py`**
    *   **Purpose:** The Object Classification module. It uses a trained model to detect and classify weapons within the processed SAR images.

*   **`SoftwareDemo/PiCamera/HeadlessPersonTracker.py`**
    *   **Purpose:** Runs the computer vision logic (YOLO) to track persons and faces in real-time without requiring a display output (headless mode).

## Installation

### Prerequisites
*   Python 3.9+
*   Raspberry Pi (for the main controller)
*   Arduino (for motor control)
*   MATLAB (for data processing)

### Python Dependencies
Install the required packages using pip:

```bash
pip install matplotlib numpy opencv-python pynput ultralytics torch torchvision torchaudio pandas requests
```

*Note: See `SoftwareDemo/pyproject.toml` for the specific dependencies of the main demo.*

## Usage

### Running the Main System
To start the full detection and scanning sequence:

```bash
python SoftwareDemo/main.py
```

## Changing Scan Speed

To adjust the scanning speed (e.g., slowing down from 36mm/s to 18mm/s), updates are required in the automation script and data processing script. The motor control script (`motorTest_rev13.py`) accepts a speed argument and does not need to be modified directly.

### 1. Automation Script (`Safehaven-Lua/sar_scan_rev15.lua`)
Update the speed variable, frame count, and return wait time.
*   **Speed**: Set `speed_mms` to the new value. This value is passed to the motor script automatically.
*   **Frame Count**: Ensure the total duration covers the scan distance.
    *   `num_frames = Distance / (Speed * Periodicity)`
    *   *Example*: `280mm / (18mm/s * 0.018s) ≈ 864 frames` (Round to nearest convenient number, e.g., 800 or 864).
*   **Return Wait**: Calculate time to return to start.
    *   `return_wait = (Distance / Speed) * 1000 + Buffer`

```lua
-- sar_scan_rev15.lua
local speed_mms = 18 -- This is passed to motorTest_rev13.py
local num_frames = 800 -- Update based on new speed
-- Update return wait time (e.g., 17000ms for 18mm/s)
local return_wait = 17000 
```

### 2. Data Processing (`Safehaven-Lua/mainSARneuronauts2py_rev3_2.py`)
Update the reconstruction parameters to match the new data format.
*   **X Dimension**: Set `X` to the new `num_frames`.
*   **Step Size (dx)**: Update the spatial step size.
    *   `dx = Speed (mm/s) * Periodicity (s)`
    *   *Example*: `18 * 0.018 = 0.324 mm`

```python
# mainSARneuronauts2py_rev3_2.py
X = 800 # Must match num_frames from Lua script
dx = 18 * 0.018 # Update dx calculation
```

Ensure you are in the root directory or adjust paths accordingly.

### Hardware Setup
*   **Motors**: Connected via Arduino. Ensure the Arduino is flashed with the code in `Arduino/simpleMain.cpp` (or relevant file).
*   **Camera**: Raspberry Pi Camera Module.
*   **Safety**: Ensure Emergency Stop and Limit Switches are connected.

### Coordinate System
*   **Origin**: The system assumes the starting position is the **Top-Left** corner.
*   **Coordinates**: In the user's Cartesian system, this Top-Left corner is defined as **(0, 0)**.

## Development

*   **AI/ML**: The project uses YOLOv5/v8/v11 models (`yolov5s.pt`, `yolov8n.pt`).
*   **Pathing**: The Snake Path algorithm ensures efficient coverage of the bounding box area.
