-- SAR Data Capture Script Revision 3
-- Automates capturing 40 scans for SAR processing.
-- Based on fix_rev2.lua and rawdog.lua.
-- Fixes timing issues where the script didn't wait long enough for the frame to complete.

-- =================================================================================
-- CONFIGURATION
-- =================================================================================
local base_path = "C:\\Users\\arikrahman\\Documents\\GitHub\\SafeHaven\\Safehaven-Lua\\dumps\\"
local num_y_steps = 40         -- Number of steps in the Y direction (matches Python Y=40)
local gantry_wait_time = 242  -- Time (ms) to wait between scans for manual/gantry movement
local frame_periodicity = 18    -- ms
local num_frames = 400         -- Matches Python X=400 (if 1 chirp/frame) or just total frames
-- Note: fix_rev2.lua uses 400 frames. Total duration = 400 * 8ms = 3200ms.

-- =================================================================================
-- INITIALIZATION
-- =================================================================================
WriteToLog("Starting SAR Scan Revision 3...\n", "blue")

-- 1. Stop any running processes
ar1.StopFrame()
ar1.CaptureCardConfig_StopRecord()
RSTD.Sleep(1000)

-- 2. Configure Sensor (Profile, Chirp, Frame)
-- Using Profile Config from rawdog.lua which is safer for 81GHz limit
-- StartFreq=77, Slope=63.343, Samples=512, SampleRate=9121
-- RampEndTime=63us
if (ar1.ProfileConfig(0, 77, 7, 6, 63, 0, 0, 0, 0, 0, 0, 63.343, 0, 512, 9121, 0, 0, 30) == 0) then
    WriteToLog("ProfileConfig Success\n", "green")
else
    WriteToLog("ProfileConfig Failure\n", "red")
end

-- Chirp Config (Tx1 and Tx2 interleaved)
-- Chirp 0: Tx1
if (ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 0, 0) == 0) then
    WriteToLog("ChirpConfig 0 Success\n", "green")
end
-- Chirp 1: Tx2
if (ar1.ChirpConfig(1, 1, 0, 0, 0, 0, 0, 2, 0, 0) == 0) then
    WriteToLog("ChirpConfig 1 Success\n", "green")
end

-- Frame Config
-- StartChirp=0, EndChirp=1 (2 chirps per frame)
-- NumFrames=400
-- Periodicity=8ms
if (ar1.FrameConfig(0, 1, num_frames, 1, frame_periodicity, 0, 512, 1) == 0) then
    WriteToLog("FrameConfig Success\n", "green")
else
    WriteToLog("FrameConfig Failure\n", "red")
end

-- 3. Configure Capture Device (DCA1000)
ar1.SelectCaptureDevice("DCA1000")
ar1.CaptureCardConfig_EthInit("192.168.33.30", "192.168.33.180", "12:34:56:78:90:12", 4096, 4098)
ar1.CaptureCardConfig_Mode(1, 2, 1, 2, 3, 30)
ar1.CaptureCardConfig_PacketDelay(25)

-- =================================================================================
-- CAPTURE LOOP
-- =================================================================================
WriteToLog("Starting Capture Loop for " .. num_y_steps .. " steps.\n", "blue")

for y = 1, num_y_steps do
    local filename = base_path .. "scan" .. y .. ".bin"
    WriteToLog("--------------------------------------------------\n", "black")
    WriteToLog("Step " .. y .. " of " .. num_y_steps .. "\n", "blue")
    WriteToLog("Target File: " .. filename .. "\n", "black")
    
    -- 1. Start Recording
    ar1.CaptureCardConfig_StartRecord(filename, 1)
    RSTD.Sleep(1000) -- Wait for DCA to arm
    
    -- 2. Start Frame
    if (ar1.StartFrame() == 0) then
        WriteToLog("Frame Started...\n", "green")
    else
        WriteToLog("StartFrame Failed!\n", "red")
        break
    end
    
    -- 3. Wait for Frame Completion
    -- Duration = NumFrames * Periodicity = 400 * 8ms = 3200ms.
    -- Adding buffer to ensure completion.
    local wait_time = (num_frames * frame_periodicity) + 1000 -- 4200ms
    RSTD.Sleep(wait_time)
    
    WriteToLog("Capture Complete.\n", "green")
    
    -- 4. Prompt for Movement (if not last step)
    if y < num_y_steps then
        WriteToLog("Move the sensor/rail to position " .. (y + 1) .. "...\n", "magenta")
        WriteToLog("Waiting " .. (gantry_wait_time/1000) .. " seconds.\n", "black")
        RSTD.Sleep(gantry_wait_time)
    end
end

WriteToLog("SAR Data Capture Finished Successfully!\n", "blue")
