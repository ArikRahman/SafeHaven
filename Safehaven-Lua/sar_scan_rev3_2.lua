-- SAR Data Capture Script Revision 4.1
-- Automates capturing 40 scans for SAR processing with integrated Gantry control.
-- Based on sar_scan_rev3.lua.
-- Executes SSH commands to drive the gantry via Raspberry Pi.
-- Fixes: Timing issues (Frame already triggered) and SSH execution (removed -t, -i).

-- =================================================================================
-- CONFIGURATION
-- =================================================================================
local base_path = "C:\\Users\\arikrahman\\Documents\\GitHub\\SafeHaven\\Safehaven-Lua\\dumps\\"
local log_file = base_path .. "gantry_log.txt"
local num_y_steps = 40         -- Number of steps in the Y direction
local frame_periodicity = 18   -- ms
local num_frames = 400         -- Total frames per scan
-- Frame Duration = 400 * 18ms = 7200ms (7.2s)

-- Gantry Configuration
local ssh_host = "corban@10.244.182.88"
local remote_dir = "/home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/GantryFunctionality/MotorTest"
local python_script = "motorTest_rev13.py"
local x_dist_mm = 280
local y_step_mm = 8
local speed_mms = 36

-- =================================================================================
-- HELPER FUNCTIONS
-- =================================================================================
function RunRemoteCommand(args)
    -- Construct the PowerShell command
    -- Using full path to pwsh.exe to avoid PATH issues
    local pwsh_exe = "C:\\Program Files\\PowerShell\\7\\pwsh.exe"
    
    -- The command we want to run on the remote machine:
    -- zsh -l -i -c 'cd <dir>; uv run <script> <args>'
    -- Added -i to force interactive mode (loads profile) as requested
    local remote_cmd_inner = string.format("cd %s; uv run %s %s", remote_dir, python_script, args)
    local remote_shell_cmd = string.format("zsh -l -i -c '%s'", remote_cmd_inner)
    
    -- The SSH command line:
    -- Added -t to allocate pseudo-tty (matches user's working command)
    local ssh_cmd_str = string.format("ssh -t %s \\\"%s\\\"", ssh_host, remote_shell_cmd)
    
    -- The full PowerShell command line:
    -- We use 'start /wait' to open a visible window and wait for it.
    -- We use 'Tee-Object' to show output AND save to log.
    -- We use 'Read-Host' to pause execution so the user can see the output.
    local full_cmd = string.format("start \"Gantry Debug\" /wait \"%s\" -Command \"%s | Tee-Object -FilePath '%s'; Read-Host 'Press Enter to continue...'\"", pwsh_exe, ssh_cmd_str, log_file)
    
    WriteToLog("Gantry Command (PWSH): " .. args .. "\n", "black")
    -- WriteToLog("Full Cmd: " .. full_cmd .. "\n", "gray")
    
    local t_start = os.clock()
    local result = os.execute(full_cmd)
    local t_end = os.clock()
    local duration = (t_end - t_start) * 1000 -- ms
    
    WriteToLog(string.format("Cmd Duration: %.2f ms. Result: %s\n", duration, tostring(result)), "gray")
    
    return result, duration
end

-- =================================================================================
-- INITIALIZATION
-- =================================================================================
WriteToLog("Starting SAR Scan Revision 4.1 (Automated Gantry)...\n", "blue")

-- 1. Stop any running processes
ar1.StopFrame()
ar1.CaptureCardConfig_StopRecord()
RSTD.Sleep(1000)

-- 2. Configure Sensor (Profile, Chirp, Frame)
-- Using Profile Config from previous revisions
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
    
    -- 1. Start Recording
    ar1.CaptureCardConfig_StartRecord(filename, 1)
    RSTD.Sleep(1000) -- Wait for DCA to arm
    
    -- 2. Start Frame (Non-blocking on hardware, returns immediately)
    if (ar1.StartFrame() == 0) then
        WriteToLog("Frame Started. Triggering Gantry...\n", "green")
    else
        WriteToLog("StartFrame Failed!\n", "red")
        break
    end
    
    -- 3. Trigger Gantry Motion (X-Axis)
    -- Determine direction: Odd = Right, Even = Left
    local move_args = ""
    if (y % 2 ~= 0) then
        move_args = string.format("right=%dmm speed=%dmms", x_dist_mm, speed_mms)
        WriteToLog("Scanning RIGHT ->\n", "magenta")
    else
        move_args = string.format("left=%dmm speed=%dmms", x_dist_mm, speed_mms)
        WriteToLog("Scanning LEFT <-\n", "magenta")
    end
    
    -- Execute Motion (Blocks script execution until motor finishes)
    -- Motor Time approx 7.8s. Frame Time 7.2s.
    local _, cmd_duration = RunRemoteCommand(move_args)
    
    -- 4. Wait for Frame Completion (Safety Buffer)
    -- Ensure we wait at least the frame duration, regardless of how fast the command returned
    local remaining_time = frame_duration_ms - cmd_duration + safety_buffer_ms
    if remaining_time > 0 then
        WriteToLog(string.format("Waiting remaining %.0f ms for frame...\n", remaining_time), "black")
        RSTD.Sleep(remaining_time)
    end
    
    WriteToLog("Capture & Scan Complete.\n", "green")
    
    -- 5. Move Y-Axis (Step Up) if not last step
    if y < num_y_steps then
        WriteToLog("Stepping UP...\n", "magenta")
        local step_args = string.format("up=%dmm speed=%dmms", y_step_mm, speed_mms)
        RunRemoteCommand(step_args)
        
        -- Small pause before next iteration
        RSTD.Sleep(500)
    end
end

WriteToLog("SAR Data Capture Finished Successfully!\n", "blue")
