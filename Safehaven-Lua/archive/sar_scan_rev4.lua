-- SAR Data Capture Script Revision 4
-- Integrates with motor control calculations from rasterscan.py.
-- Synchronizes radar capture with gantry movement.
-- REQUIRES: motorTest_rev13.py in the same directory.

-- =================================================================================
-- CONFIGURATION (Must match rasterscan.py)
-- =================================================================================
local base_path = "C:\\Users\\arikrahman\\Documents\\GitHub\\SafeHaven\\Safehaven-Lua\\dumps\\"
local project_dir = "C:\\Users\\arikrahman\\Documents\\GitHub\\SafeHaven\\Safehaven-Lua"
local script_name = "motorTest_rev13.py"
local python_cmd = "uv run python" -- Command to run python scripts (supports uv/venv)

-- Scan Dimensions
local num_y_steps = 40         -- NUM_SLICES
local x_dist_mm = 280          -- X_DIST_MM
local y_step_mm = 8            -- Y_STEP_MM

-- Motor Speeds
local x_speed_mms = 36         -- X_SPEED_MMS
local y_speed_mms = 36         -- Y_SPEED_MMS

-- Radar Timing Calculations
-- Time to move X = 280mm / 36mm/s = 7.777 seconds
-- We need the radar to capture for at least this long.
-- We use 400 frames (matches X=400 in reconstruction).
-- Periodicity = 20ms.
-- Total Capture Time = 400 * 20ms = 8000ms = 8.0 seconds.
-- This gives ~0.22s buffer after motor stops.

local num_frames = 400
local frame_periodicity = 20   -- ms

-- =================================================================================
-- INITIALIZATION
-- =================================================================================
WriteToLog("Starting SAR Scan Revision 4 (Synced)...\n", "blue")

-- 1. Stop any running processes
ar1.StopFrame()
ar1.CaptureCardConfig_StopRecord()
RSTD.Sleep(1000)

-- 2. Configure Sensor
-- Profile: StartFreq=77, Slope=63.343, Samples=512, SampleRate=9121
-- RampEndTime=63us
if (ar1.ProfileConfig(0, 77, 7, 6, 63, 0, 0, 0, 0, 0, 0, 63.343, 0, 512, 9121, 0, 0, 30) == 0) then
    WriteToLog("ProfileConfig Success\n", "green")
else
    WriteToLog("ProfileConfig Failure\n", "red")
end

-- Chirp Config (Tx1 and Tx2 interleaved)
ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 0, 0) -- Tx1
ar1.ChirpConfig(1, 1, 0, 0, 0, 0, 0, 2, 0, 0) -- Tx2

-- Frame Config
-- 400 Frames, 20ms periodicity -> 8s duration
if (ar1.FrameConfig(0, 1, num_frames, 1, frame_periodicity, 0, 512, 1) == 0) then
    WriteToLog("FrameConfig Success (8s duration)\n", "green")
else
    WriteToLog("FrameConfig Failure\n", "red")
end

-- 3. Configure Capture Device
ar1.SelectCaptureDevice("DCA1000")
ar1.CaptureCardConfig_EthInit("192.168.33.30", "192.168.33.180", "12:34:56:78:90:12", 4096, 4098)
ar1.CaptureCardConfig_Mode(1, 2, 1, 2, 3, 30)
ar1.CaptureCardConfig_PacketDelay(25)

-- =================================================================================
-- CAPTURE LOOP
-- =================================================================================
WriteToLog("Starting Synced Capture Loop...\n", "blue")

for y = 1, num_y_steps do
    local filename = base_path .. "scan" .. y .. ".bin"
    
    -- Determine Direction (Odd=Right, Even=Left)
    local direction = "right"
    if (y % 2 == 0) then direction = "left" end
    
    WriteToLog("--------------------------------------------------\n", "black")
    WriteToLog("Step " .. y .. "/" .. num_y_steps .. " Dir: " .. direction .. "\n", "blue")
    
    -- 1. Start Recording
    ar1.CaptureCardConfig_StartRecord(filename, 1)
    RSTD.Sleep(1000) -- Wait for DCA to arm
    
    -- 2. Start Frame (Async, 8s duration)
    if (ar1.StartFrame() == 0) then
        WriteToLog("Frame Started. Moving Motor...\n", "green")
    else
        WriteToLog("StartFrame Failed!\n", "red")
        break
    end
    
    -- 3. Move Motor X (Blocking call to Python)
    -- Command: cd /d PROJECT_DIR && uv run python motorTest_rev13.py right=280mm speed=36mms
    local cmd_x = string.format('cd /d "%s" && %s "%s" %s=%dmm speed=%dmms', project_dir, python_cmd, script_name, direction, x_dist_mm, x_speed_mms)
    WriteToLog("Exec: " .. cmd_x .. "\n", "black")
    os.execute(cmd_x)
    
    -- 4. Wait for Frame Completion
    -- Motor took ~7.8s. Frame takes 8.0s.
    -- We wait a bit extra to ensure frame is fully done and file is closed.
    WriteToLog("Motor done. Waiting for frame end...\n", "black")
    RSTD.Sleep(1000) 
    
    WriteToLog("Capture Complete.\n", "green")
    
    -- 5. Move Motor Y (if not last step)
    if y < num_y_steps then
        WriteToLog("Moving Y axis...\n", "magenta")
        -- Command: cd /d PROJECT_DIR && uv run python motorTest_rev13.py up=8mm speed=36mms
        local cmd_y = string.format('cd /d "%s" && %s "%s" up=%dmm speed=%dmms', project_dir, python_cmd, script_name, y_step_mm, y_speed_mms)
        WriteToLog("Exec: " .. cmd_y .. "\n", "black")
        os.execute(cmd_y)
        -- os.execute blocks, so we wait for Y move (~0.22s) to finish before next loop
    end
end

WriteToLog("SAR Data Capture Finished Successfully!\n", "blue")
