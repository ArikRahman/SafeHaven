# SafeHaven SAR Data Capture

## Goal
The goal of this project is to capture Synthetic Aperture Radar (SAR) data using an IWR1443 radar and DCA1000 capture card for a weapon classification project
We need to automate the capture process to synchronize with a gantry system that moves the radar vertically.
dear AI comment every damn lin

### `sar_scan_rev12.lua`
*   **Status:** ✅ Working (Latest Revision)
*   **Function:** Production script for automated SAR data capture with gantry synchronization.
    *   Performs a **snake scan** pattern: Alternates X-axis direction on each Y-step (right on odd steps, left on even steps) while stepping up in Y after each scan.
    *   Configures radar (Profile, Chirp, Frame) and DCA1000 capture card.
    *   Loops for `num_y_steps` (default 40) scans.
    *   Triggers gantry motion asynchronously before starting radar frame.
    *   Polls for motor start confirmation via log file.
    *   Saves each scan as `scanN.bin` in a new timestamped `dumpsN` folder.
*   **Scan Type:** Snake Scan - Bidirectional X-motion with unidirectional Y-stepping for efficient coverage.
*   **Prerequisites:** IWR1443 connected, firmware loaded, basic config done.

### `fix.lua`
*   **Status:** ✅ Working
*   **Function:** Configures Chirps, Frame, and Capture Card, then takes a **single** capture.
*   **Prerequisites:** Assumes the device is already initialized (Static Config, Data Config, Profile Config) likely via the mmWave Studio GUI or a previous script run.

### `rawdog.lua`
*   **Status:** 🚧 In Progress
*   **Function:** Intended to be the "Production" script.
    *   Configures the device (matching `fix.lua`).
    *   Loops `num_y_steps` times (e.g., 40).
    *   Triggers a capture.
    *   Saves the file as `dumps\scanN.bin`.
    *   Waits for the gantry to move.
*   **Current Issue:** `INVALID INPUT` errors on `ChirpConfig` and `FrameConfig` when running the loop.

## Usage Instructions
1.  **Initialize Device:** Ensure the IWR1443 is connected, firmware is loaded, and basic "Static Config" and "Data Config" are done (e.g., via mmWave Studio GUI).
2.  **Run `rawdog.lua`:** Execute this script to start the automated scan loop.

## Troubleshooting
*   If `rawdog.lua` fails, try running `fix.lua` to verify the device state.
*   If `fix.lua` works, `rawdog.lua` should work if the configuration commands are identical.
