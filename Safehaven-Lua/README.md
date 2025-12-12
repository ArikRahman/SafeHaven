# SafeHaven Scripts & Utilities

This directory contains the primary Lua scripts for mmWave Studio and associated Python processing scripts. Below is a list of the critical files used in the SafeHaven project ecosystem.

## Core Files

### Radar Scanning (Lua)
*   **`sar_scan_rev15.lua`**
    *   **Location:** `./` (This directory)
    *   **Purpose:** The main automation script run within TI mmWave Studio. It controls the radar parameters and triggers the scanning sequence.

### Data Processing & SAR Generation
*   **`mainSARneuronauts2py_rev3_2.py`**
    *   **Location:** `./` (This directory)
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

*   **`batch_process_dumps.py`**
    *   **Location:** `./` (This directory)
    *   **Purpose:** Handles pre-processing of data dumps (grayscaling, normalization) to prepare them for the Machine Learning pipeline.

### Motor Control
*   **`motorTest_rev13.py`**
    *   **Location:** `../SoftwareDemo/GantryFunctionality/MotorTest/`
    *   **Purpose:** The driver script for the 2-axis gantry system. It interprets commands (often from the Lua script or Main Orchestrator) to move the stepper motors.

### AI & Computer Vision
*   **`weapon_classifier.py`**
    *   **Location:** `../Safehaven-Classification/`
    *   **Purpose:** The Object Classification module. It uses a trained model to detect and classify weapons within the processed SAR images.

*   **`HeadlessPersonTracker.py`**
    *   **Location:** `../SoftwareDemo/PiCamera/`
    *   **Purpose:** Runs the computer vision logic (YOLO) to track persons and faces in real-time without requiring a display output (headless mode).