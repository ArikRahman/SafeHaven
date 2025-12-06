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

Ensure you are in the root directory or adjust paths accordingly.

### Hardware Setup
*   **Motors**: Connected via Arduino. Ensure the Arduino is flashed with the code in `Arduino/simpleMain.cpp` (or relevant file).
*   **Camera**: Raspberry Pi Camera Module.
*   **Safety**: Ensure Emergency Stop and Limit Switches are connected.

## Development

*   **AI/ML**: The project uses YOLOv5/v8/v11 models (`yolov5s.pt`, `yolov8n.pt`).
*   **Pathing**: The Snake Path algorithm ensures efficient coverage of the bounding box area.
