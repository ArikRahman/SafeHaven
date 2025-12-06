-- SAR Data Capture Script for IWR1443 + DCA1000
-- Matches parameters for mainSARneuronauts2py.py

-- =================================================================================
-- USER CONFIGURATION
-- =================================================================================
local base_path = "C:\\Users\\arikrahman\\Documents\\GitHub\\SafeHaven\\Safehaven-Lua\\dumps\\" -- Ensure this folder exists!
local num_y_steps = 40         -- Matches Y=40 in your Python script
local gantry_wait_time = 3000  -- Time (ms) to wait between scans for gantry movement
local start_freq = 77          -- GHz
local slope = 63.343           -- MHz/us
local samples = 512
local sample_rate = 9121       -- ksps
local chirps_per_frame = 400   -- Matches X=400 in your Python script
-- =================================================================================

-- 1. CALCULATE TIMING PARAMETERS
-- Ramp time = samples / sample_rate = 512 / 9121 = 56.13 us
-- Ramp End Time needs to include ADC Start Time (6us) + Ramp Time + Excess
local ramp_end_time = 63.3 -- 6 + 56.13 + ~2.37 overhead
local idle_time = 7        -- us

-- [FIX 1] STOP PREVIOUS STATE
-- The error "Stop the already running process" indicates the DCA1000 is still active from a previous run.
-- We explicitly stop the frame and the recording to clear the state before re-configuring.
WriteToLog("Resetting Device State...\n", "blue")
ar1.StopFrame()
ar1.CaptureCardConfig_StopRecord()
RSTD.Sleep(2000) -- Wait 2s for the card to fully stop.

-- 2. SYSTEM RESET & CONNECTION (Optional if manual, uncomment if needed)
-- ar1.FullReset()
-- ar1.SOPControl(2)
-- ar1.Connect(4, 921600, 1000)

-- 3. LOAD FIRMWARE (Assuming SDK 2.x path, adjust if using SDK 3.x/LTS)
-- ar1.DownloadBSSFw("C:\\ti\\firmware\\radarss\\xwr12xx_xwr14xx_radarss_rprc.bin")
-- ar1.DownloadMSSFw("C:\\ti\\firmware\\masterss\\xwr12xx_xwr14xx_masterss_rprc.bin")
-- ar1.PowerOn(0, 1000, 0, 0)

-- 4. STATIC CONFIGURATION (Commented out as they fail and might be pre-configured)
-- ar1.ChanNAdcConfig(1, 1, 0, 1, 1, 1, 1, 2, 1, 0)
-- ar1.LPModConfig(0, 0)
-- ar1.RfInit()

-- 5. DATA CONFIGURATION (Commented out as they fail and might be pre-configured)
-- ar1.DataFmtConfig_Multimode(0, 1, 2, 1, 2)
-- ar1.DataPathConfig(513, 121, 0)
-- ar1.LvdsClkConfig(1, 1)
-- ar1.LvdsLaneConfig(0, 1, 1, 0, 0, 1, 0, 0)

-- 6. SENSOR CONFIGURATION (Profile, Chirp, Frame)
WriteToLog("Configuring Sensor...\n", "blue")

-- [FIX 2] DEFINE PROFILE
-- The error "INVALID INPUT" on ChirpConfig happens because Profile 0 is undefined.
-- fix.lua works because it relies on a pre-existing profile (from GUI).
-- rawdog.lua must define it explicitly to be self-contained and recover from failed states.
-- Changed ramp_end_time to 63us (was 65us) to keep End Freq < 81 GHz.
-- Calculation: 77GHz + (63.343MHz/us * 63us) = 77 + 3.99GHz = 80.99GHz (Valid < 81)
if (ar1.ProfileConfig(0, start_freq, idle_time, 6, 63, 0, 0, 0, 0, 0, 0, slope, 0, samples, sample_rate, 0, 0, 30) == 0) then
    WriteToLog("ProfileConfig Success\n", "green")
else
    WriteToLog("ProfileConfig Failure\n", "red")
end

-- Chirp Config: Use Profile 0, all TX enabled
if (ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 0, 0) == 0) then
    WriteToLog("ChirpConfig 0 Success\n", "green")
end
if (ar1.ChirpConfig(1, 1, 0, 0, 0, 0, 0, 2, 0, 0) == 0) then
    WriteToLog("ChirpConfig 1 Success\n", "green")
end

-- Frame Config: 400 Frames, 1 Loop, 8ms periodicity
ar1.FrameConfig(0, 1, 400, 1, 8, 0, 512, 1)

-- 7. SELECT DCA1000 MODE
ar1.SelectCaptureDevice("DCA1000")
ar1.CaptureCardConfig_EthInit("192.168.33.30", "192.168.33.180", "12:34:56:78:90:12", 4096, 4098)
ar1.CaptureCardConfig_Mode(1, 2, 1, 2, 3, 30)
ar1.CaptureCardConfig_PacketDelay(25)

-- 8. CAPTURE LOOP
WriteToLog("Starting SAR Scan Loop...\n", "blue")

for y = 1, num_y_steps do
    -- Construct filename: "scan1.bin", "scan2.bin" ...
    -- DCA1000 will append "_Raw_0.bin", resulting in "scan1_Raw_0.bin" which matches Python
    local filename = base_path .. "scan" .. y .. ".bin"
    
    WriteToLog("Starting Capture: " .. filename .. "\n", "black")
    
    -- Configure Capture Card for this specific file
    ar1.CaptureCardConfig_StartRecord(filename, 1)
    RSTD.Sleep(1000) -- Wait for DCA to arm
    
    -- Trigger Frame
    if (ar1.StartFrame() == 0) then
        WriteToLog("StartFrame Success\n", "green")
    else
        WriteToLog("StartFrame Failed! Stopping Loop.\n", "red")
        break
    end
    
    -- Wait for frame duration + transfer time
    -- Frame active time = 400 * (7+64.5)us = ~28.6ms. 
    -- Transfer 512*400*4 bytes = ~800KB. Fast.
    RSTD.Sleep(1000) 
    
    WriteToLog("Capture " .. y .. " Complete.\n", "green")
    
    if y < num_y_steps then
        WriteToLog("Waiting " .. (gantry_wait_time/1000) .. "s for gantry movement...\n", "blue")
        RSTD.Sleep(gantry_wait_time)
    end
end

WriteToLog("SAR Data Capture Finished!\n", "blue")
