-- SAR Data Capture Script Revision 14 (Infinite Loop)
-- Automates capturing 40 scans for SAR processing with integrated Gantry control.
-- Repeats infinitely, creating new folders (dumpsN) and resetting position.

-- =================================================================================
-- CONFIGURATION
-- =================================================================================
local root_path = "C:\\Users\\arikrahman\\Documents\\GitHub\\SafeHaven\\Safehaven-Lua\\"
local num_y_steps = 40         -- Number of steps in the Y direction
local frame_periodicity = 18   -- ms
local num_frames = 400         -- Total frames per scan
-- Frame Duration = 400 * 18ms = 7200ms (7.2s)

-- Gantry Configuration
local ssh_host = "corban@10.244.182.88"
local remote_dir = "/home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/GantryFunctionality/MotorTest"
local python_script = "motorTest_rev13.py"
local x_dist_mm = 280
local y_step_mm = 1
local speed_mms = 36

-- Log file variable (updated in loop)
local log_file = ""

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

function ResetGantryPosition()
    WriteToLog("Resetting Gantry Position (Origin=Bottom, then Right 200mm, Up 70mm)...\n", "magenta")
    
    local pwsh_exe = "C:\\Program Files\\PowerShell\\7\\pwsh.exe"
    
    -- The exact command requested by user
    local remote_cmd = "cd /home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/GantryFunctionality/MotorTest; uv run motorTest_rev13.py origin=bottom; cd /home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/GantryFunctionality/MotorTest; uv run motorTest_rev13.py right=200mm up=70mm"
    
    local remote_shell_cmd = string.format("zsh -l -i -c '%s'", remote_cmd)
    local ssh_cmd_str = string.format("ssh -t %s \\\"%s\\\"", ssh_host, remote_shell_cmd)
    
    -- Blocking command using start /wait /min to ensure it finishes before scanning starts
    -- We do NOT pipe to log_file here because log_file is not yet set for the new iteration
    local full_cmd = string.format("start \"GantryReset\" /wait /min \"%s\" -NoProfile -Command \"%s\"", pwsh_exe, ssh_cmd_str)
    
    WriteToLog("Executing Reset Command: " .. full_cmd .. "\n", "black")
    os.execute(full_cmd)
    
    WriteToLog("Reset Complete.\n", "green")
    RSTD.Sleep(1000)
end

-- =================================================================================
-- INITIALIZATION (Sensor Setup - Run Once)
-- =================================================================================
WriteToLog("Starting SAR Scan Revision 14 (Infinite Loop)...\n", "blue")

-- 1. Stop any running processes
ar1.StopFrame()
ar1.CaptureCardConfig_StopRecord()
RSTD.Sleep(20)

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

-- Frame Config
if (ar1.FrameConfig(0, 0, num_frames, 1, frame_periodicity, 0, 512, 1) == 0) then
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
-- MAIN LOOP
-- =================================================================================
while true do
    -- 1. Reset Position FIRST
    ResetGantryPosition()

    -- 2. Prepare Directory
    local max_index = -1
    local p = io.popen('dir "' .. root_path .. '" /b /ad')
    if p then
        for filename in p:lines() do
            local index_str = string.match(filename, "^dumps(%d+)")
            if index_str then
                local index = tonumber(index_str)
                if index > max_index then
                    max_index = index
                end
            end
        end
        p:close()
    end

    local new_index = max_index + 1
    local new_folder_name = "dumps" .. new_index
    local base_path = root_path .. new_folder_name .. "\\"

    os.execute('mkdir "' .. root_path .. new_folder_name .. '"')
    if WriteToLog then
        WriteToLog("Created new output directory: " .. base_path .. "\n", "blue")
    end

    log_file = base_path .. "gantry_log.txt"

    -- 3. Capture Loop
    WriteToLog("Starting Capture Loop for " .. num_y_steps .. " steps.\n", "blue")

    local frame_duration_ms = num_frames * frame_periodicity
    local safety_buffer_ms = 1000

    for y = 1, num_y_steps do
        local filename = base_path .. "scan" .. y .. ".bin"
        WriteToLog("--------------------------------------------------\n", "black")
        WriteToLog("Step " .. y .. " of " .. num_y_steps .. "\n", "blue")
        WriteToLog("Target File: " .. filename .. "\n", "black")
        
        -- Arm DCA1000
        if (ar1.CaptureCardConfig_StartRecord(filename, 1) == 0) then
            WriteToLog("DCA1000 Armed Successfully.\n", "green")
        else
            WriteToLog("DCA1000 Arm Failed!\n", "red")
        end
        RSTD.Sleep(0)
        
        -- Trigger Gantry Motion (X-Axis) - ASYNC
        local move_args = string.format("right=%dmm speed=%dmms", x_dist_mm, speed_mms)
        WriteToLog("Scanning RIGHT ->\n", "magenta")
        RunRemoteCommandAsync(move_args)
        
        -- Poll for motor start
        WriteToLog("Waiting for motor to start...\n", "black")
        local poll_count = 0
        local max_polls = 100
        local motor_started = false
        while poll_count < max_polls and not motor_started do
            local file = io.open(log_file, "r")
            if file then
                local content = file:read("*all")
                file:close()
                if string.find(content, "MOTOR_STARTED") then
                    motor_started = true
                    WriteToLog("Motor started confirmed!\n", "green")
                    WriteToLog("Waiting 0.5s for motor stabilization...\n", "black")
                    RSTD.Sleep(500)
                end
            end
            if not motor_started then
                RSTD.Sleep(10)
                poll_count = poll_count + 1
            end
        end
        if not motor_started then
            WriteToLog("Timeout waiting for motor start! Proceeding anyway.\n", "red")
        end
        
        -- Trigger Radar
        if (ar1.StartFrame() == 0) then
            WriteToLog("Frame Started.\n", "green")
        else
            WriteToLog("StartFrame Failed!\n", "red")
            break
        end
        
        -- Wait for Frame
        local wait_time = frame_duration_ms + safety_buffer_ms
        WriteToLog(string.format("Waiting %d ms for frame & motor...\n", wait_time), "black")
        RSTD.Sleep(wait_time)
        
        WriteToLog("Capture & Scan Complete.\n", "green")
        
        -- Return X-Axis (Left)
        WriteToLog("Returning LEFT <-\n", "magenta")
        local return_args = string.format("left=%dmm speed=%dmms", x_dist_mm, speed_mms)
        RunRemoteCommandAsync(return_args)
        
        local return_wait = 8500
        WriteToLog(string.format("Waiting %d ms for return...\n", return_wait), "black")
        RSTD.Sleep(return_wait)

        -- Step UP
        if y < num_y_steps then
            WriteToLog("Stepping UP (Async)...\n", "magenta")
            local step_args = string.format("up=%dmm speed=%dmms", y_step_mm, speed_mms)
            RunRemoteCommandAsync(step_args)
        end
    end

    WriteToLog("SAR Data Capture Finished for " .. new_folder_name .. "!\n", "blue")
    WriteToLog("Restarting loop in 5 seconds...\n", "blue")
    RSTD.Sleep(5000)
end
