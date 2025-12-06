#Requires AutoHotkey v2.0

; --- CONFIGURATION ---
global DataFolder := "C:\ti\mmwave_studio_02_01_01_00\mmWaveStudio\PostProc\cranidetect"
global lastBinCount := 0

; Press 'f1' to start the sequence
F1::
{
    Sleep 200

    ; Initialize count before starting the loop so we have a baseline
    global lastBinCount := CountBinFiles(DataFolder)

    Loop 100
    {
        ; --- 1. START CAPTURE (mmWave Studio) ---
        Send "{Enter}"
        Sleep 10
        Send "{Enter}"

        ; --- 2. INTELLIGENT WAIT (Wait for .bin file) ---
        ; This ensures we don't move the motor until capture is actually saved
        if !WaitForNewBin(DataFolder, 17000)
        {
            MsgBox "Error: Timeout waiting for .bin file. Script stopped."
            ExitApp
        }

        ; --- 3. POST-CAPTURE LOGIC (Rename/Log in Studio) ---
        Send "{Tab 2}"
        Sleep 500

        Send "{End}"
        Sleep 50
        Send "{Left 4}"
        Sleep 50

        ; Delete Previous Number
        if (A_Index <= 10)
            Send "{Backspace}"
        else
            Send "{Backspace 2}"
        Sleep 50

        ; Type Current Number
        Send A_Index
        Sleep 100

        ; Reset Position
        Send "+{Tab 4}"
        Sleep 30
    }
}

; --- HELPER FUNCTIONS ---

CountBinFiles(dir) {
    count := 0
    try {
        Loop Files, dir "\*.txt"
            count++
    }
    return count
}

WaitForNewBin(dir, timeoutMS) {
    ; Sleep 2000
    ; return true
    ; comment out when real ^
    global lastBinCount


    startTime := A_TickCount
    Loop {
        currentCount := CountBinFiles(dir)

        ; If we have more files than before, success!
        if (currentCount > lastBinCount) {
            lastBinCount := currentCount ; Update global count
            return true
        }

        if (A_TickCount - startTime > timeoutMS)
            return false

        Sleep 100
    }
}

Esc::ExitApp
