# SafeHaven SAR Data Capture

## Goal
The goal of this project is to capture Synthetic Aperture Radar (SAR) data using an IWR1443 radar and DCA1000 capture card.
We need to automate the capture process to synchronize with a gantry system that moves the radar vertically.
dear AI comment every damn lin
## Scripts

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
