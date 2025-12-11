# System Agents & Functional Components

This document outlines the primary functional "agents" within the SafeHaven system. Each agent represents a distinct module responsible for a specific aspect of the hardware-software integration, from vision and path planning to motor control and data analysis.

## 1. The Orchestrator (Master Controller)
**Role:** Central Coordination  
**Location:** `SoftwareDemo/main.py`

The Orchestrator is the entry point of the system. It initializes all other agents, manages the state machine, and ensures the data flow between the vision system, path planner, and gantry controller.

**Responsibilities:**
-   Initializing hardware connections (Camera, Arduino/Motors).
-   Triggering the Vision Agent to scan for targets.
-   Passing target coordinates to the Navigator Agent.
-   Executing the movement plan via the Mechanic Agent.
-   Handling system interrupts and emergency stops.

## 2. The Vision Agent (PiCamera)
**Role:** Detection & Localization  
**Location:** `SoftwareDemo/PiCamera/`

This agent utilizes the Raspberry Pi Camera and AI models (YOLO) to detect persons or objects of interest within the field of view. It translates pixel data into real-world coordinates for the gantry.

**Key Files:**
-   `HeadlessPersonTracker.py`: Likely the main script for running detection without a GUI.
-   `PiCameraAI.py` / `IMX708_PiCamAI.py`: Interfaces for the camera hardware and inference logic.
-   `yolov8n.pt`: The neural network model weights used for detection.

**Responsibilities:**
-   Capturing video/images.
-   Running object detection inference.
-   Calculating bounding boxes and centroids.
-   Outputting coordinates (e.g., to `box_coords.json` or memory).

## 3. The Navigator (Path Planning)
**Role:** Path Generation  
**Location:** `SoftwareDemo/SnakepathAlgorithm/`

Once a target is identified, the Navigator calculates the optimal path for the SAR (Synthetic Aperture Radar) scan. It typically generates a "snake" or raster pattern over the region of interest.

**Responsibilities:**
-   Receiving target coordinates from the Vision Agent.
-   Generating a list of waypoints (`pathlist`) for the motors to follow.
-   Optimizing the path for coverage and speed.

## 4. The Mechanic (Gantry Control)
**Role:** Physical Movement & Safety  
**Location:** `SoftwareDemo/GantryFunctionality/`

This agent handles the low-level logic for moving the physical gantry system. It communicates with the motor drivers and monitors safety sensors.

**Sub-Components:**
-   **MotorFunc**: Handles the logic for driving stepper/servo motors.
-   **LimitSwitches**: Monitors end-stops to prevent mechanical over-travel.
-   **ShutoffSwitch**: Monitors the E-Stop or software kill switch.

**Responsibilities:**
-   Translating waypoints into motor steps/signals.
-   Sending commands to the Arduino (if used as a bridge) or GPIO.
-   Halting operations immediately if safety switches are triggered.

## 5. The Analyst (Data Processing)
**Role:** Post-Processing  
**Location:** `MATLAB/`

While the Python system handles real-time control, the Analyst agent (often running offline or on a separate timeline) processes the raw data collected during the scan to generate SAR imagery.

**Responsibilities:**
-   Ingesting raw radar/scan data.
-   Applying signal processing algorithms.
-   Reconstructing images from the scan data.

## 6. The Firmware (Embedded Control)
**Role:** Low-Level Driver  
**Location:** `Arduino/`

The C++ code running on the Arduino acts as the direct interface to the motor drivers, often receiving high-level commands from the Raspberry Pi (The Orchestrator) and handling the precise timing of pulse generation.

## 7. Utilities & Development Tools
**Role:** Support & Testing
**Location:** Various

These components support the development, testing, and maintenance of the primary agents.

**Key Components:**
-   **BoundaryBoxDetect**: Standalone testing for bounding box logic.
-   **Image Transposition**: Tools for manipulating image data.
-   **ScreenCapture**: Utilities for capturing screen output, likely for debugging or documentation.
-   **bin_examples_and_parser**: Tools for parsing binary data, possibly related to radar or sensor data formats.