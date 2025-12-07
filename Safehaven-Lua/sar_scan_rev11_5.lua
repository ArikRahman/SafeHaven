-- SAR Data Capture Script Revision 12
-- Automates capturing 100 scans for SAR processing with integrated Gantry control.
-- Based on sar_scan_rev11.lua.
-- Changes:
--   - High-Resolution Mode: Reduced Y-step to 2mm (<= lambda/2) to prevent aliasing.
--   - Increased num_y_steps to 100 to maintain 200mm vertical coverage.
--   - Optimized for weapon classification with IWR1443/DCA1000EVM.

-- =================================================================================
-- CONFIGURATION
-- =================================================================================
local base_path = "C:\\Users\\arikrahman\\Documents\\GitHub\\SafeHaven\\Safehaven-Lua\\dumps\\"
local log_file = base_path .. "gantry_log.txt"
local num_y_steps = 100        -- Number of steps in the Y direction (Increased for resolution)
local frame_periodicity = 18   -- ms
local num_frames = 400         -- Total frames per scan
-- Frame Duration = 400 * 18ms = 7200ms (7.2s)

-- Gantry Configuration
local ssh_host = "corban@10.244.182.88"
local remote_dir = "/home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/GantryFunctionality/MotorTest"
local python_script = "motorTest_rev13.py"
local x_dist_mm = 280
local y_step_mm = 2            -- Reduced to 2mm (<= lambda/2) to prevent aliasing
local speed_mms = 36

-- =================================================================================
-- HELPER FUNCTIONS
-- =================================================================================
function RunRemoteCommandAsync(args)
    -- Construct the PowerShell command
    -- Using full path to pwsh.exe to avoid PATH issues
    local pwsh_exe = "C:\\Program Files\\PowerShell\\7\\pwsh.exe"
    
    -- Add 'silent' to the python arguments
    local args_with_flag = args .. " silent"
    
    -- The command we want to run on the remote machine:
    -- zsh -l -i -c 'cd <dir>; uv run <script> <args>'
    local remote_cmd_inner = string.format("cd %s; uv run %s %s", remote_dir, python_script, args_with_flag)
    local remote_shell_cmd = string.format("zsh -l -i -c '%s'", remote_cmd_inner)
    
    -- The SSH command line:
    -- Added -t to allocate pseudo-tty
    local ssh_cmd_str = string.format("ssh -t %s \\\"%s\\\"", ssh_host, remote_shell_cmd)
    
    -- The full PowerShell command line:
    -- Uses 'start /min' WITHOUT /wait. Returns immediately.
    local full_cmd = string.format("start \"Gantry\" /min \"%s\" -NoProfile -Command \"%s | Tee-Object -FilePath '%s'\"", pwsh_exe, ssh_cmd_str, log_file)
    
    WriteToLog("Gantry Async (PWSH): " .. args .. "\n", "black")
    os.execute(full_cmd)
end

-- =================================================================================
-- INITIALIZATION
-- =================================================================================
WriteToLog("Starting SAR Scan Revision 12 (High-Res Mode)...\n", "blue")

-- 1. Stop any running processes
ar1.StopFrame()
ar1.CaptureCardConfig_StopRecord()
RSTD.Sleep(200)

-- 2. Configure Sensor (Profile, Chirp, Frame)
if (ar1.ProfileConfig(0, 77, 7, 6, 63, 0, 0, 0, 0, 0, 0, 63.343, 0, 512, 9121, 0, 0, 30) == 0) then
    WriteToLog("ProfileConfig Success\n", "green")
else
    WriteToLog("ProfileConfig Failure\n", "red")
end

-- Chirp Config (Tx1 and Tx2 interleaved)
if (ar1.ChirpConfig(0, 0, 0, 0, 0, 0, 0, 1, 0, 0) == 0) then
    WriteToLog("ChirpConfig 0 Success\n", "green")
end
if (ar1.ChirpConfig(1, 1, 0, 0, 0, 0, 0, 2, 0, 0) == 0) then
    WriteToLog("ChirpConfig 1 Success\n", "green")
end

-- Frame Config
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

local frame_duration_ms = num_frames * frame_periodicity
local safety_buffer_ms = 1000

for y = 1, num_y_steps do
    local filename = base_path .. "scan" .. y .. ".bin"
    WriteToLog("--------------------------------------------------\n", "black")
    WriteToLog("Step " .. y .. " of " .. num_y_steps .. "\n", "blue")
    WriteToLog("Target File: " .. filename .. "\n", "black")
    
    -- 1. Start Recording (Arm DCA1000)
    ar1.CaptureCardConfig_StartRecord(filename, 1)
    RSTD.Sleep(1000) -- Wait for DCA to arm
    
    -- 2. Trigger Gantry Motion (X-Axis) - ASYNC
    local move_args = ""
    if (y % 2 ~= 0) then
        move_args = string.format("right=%dmm speed=%dmms", x_dist_mm, speed_mms)
        WriteToLog("Scanning RIGHT ->\n", "magenta")
    else
        move_args = string.format("left=%dmm speed=%dmms", x_dist_mm, speed_mms)
        WriteToLog("Scanning LEFT <-\n", "magenta")
    end
    
    -- Execute Motion (Non-Blocking)
    RunRemoteCommandAsync(move_args)
    
    -- Poll for motor start confirmation
    WriteToLog("Waiting for motor to start...\n", "black")
    local poll_count = 0
    local max_polls = 100 -- 1 second at 10ms intervals
    local motor_started = false
    while poll_count < max_polls and not motor_started do
        local file = io.open(log_file, "r")
        if file then
            local content = file:read("*all")
            file:close()
            if string.find(content, "MOTOR_STARTED") then
                motor_started = true
                WriteToLog("Motor started confirmed!\n", "green")
            end
        end
        if not motor_started then
            RSTD.Sleep(10) -- Poll every 10ms
            poll_count = poll_count + 1
        end
    end
    if not motor_started then
        WriteToLog("Timeout waiting for motor start! Proceeding anyway.\n", "red")
    end
    
    -- 3. Start Frame (Trigger Radar)
    -- Trigger Radar AFTER Gantry
    if (ar1.StartFrame() == 0) then
        WriteToLog("Frame Started.\n", "green")
    else
        WriteToLog("StartFrame Failed!\n", "red")
        break
    end
    
    -- 4. Wait for Frame Completion
    -- We wait for the Frame Duration + Buffer.
    local wait_time = frame_duration_ms + safety_buffer_ms
    WriteToLog(string.format("Waiting %d ms for frame & motor...\n", wait_time), "black")
    RSTD.Sleep(wait_time)
    
    WriteToLog("Capture & Scan Complete.\n", "green")
    
    -- 5. Move Y-Axis (Step Up) if not last step
    if y < num_y_steps then
        WriteToLog("Stepping UP (Async)...\n", "magenta")
        local step_args = string.format("up=%dmm speed=%dmms", y_step_mm, speed_mms)
        
        -- Use Async command here to avoid waiting
        RunRemoteCommandAsync(step_args)
        
        -- No sleep needed here; next loop setup covers the time.
    end
end

WriteToLog("SAR Data Capture Finished Successfully!\n", "blue")