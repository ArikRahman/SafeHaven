#Requires AutoHotkey v2.0

; --- CONFIGURATION ---
; VERIFY THIS PATH IS CORRECT FOR YOUR CURRENT PROJECT
global DataFolder := "C:\ti\mmwave_studio_02_01_01_00\mmWaveStudio\PostProc\cranidetect"
global FileExtension := "*.txt"  ; You mentioned waiting for a new TXT file

; Press 'F1' to start the sequence
F1::
{
    global DataFolder, FileExtension
    
    MsgBox("Starting Loop. Make sure mmWave Studio is focused.", "Rev 6 Started", "T1")
    Sleep 500

    ; Get the baseline count of files before we do anything
    currentFileCount := CountFiles(DataFolder, FileExtension)

    Loop 100
    {
        ; --- 1. START CAPTURE ---
        ; Sequence requested: Enter, Tab, Enter
        Send "{Enter}"
        Sleep 200
        Send "{Tab}"
	Sleep 200

	Send "{Enter}"
	
        Sleep 200
        Send "{Enter}"

        ; --- 2. ABSOLUTE WAIT ---
        ; The script pauses here completely until a NEW file appears.
        ; It passes the 'currentFileCount' we just took to compare against.
        if !WaitForNewFile(DataFolder, FileExtension, currentFileCount, 20000)
        {
            MsgBox "Error: Timed out waiting for new " FileExtension " file. Sequence stopped."
            Return ; Exits the thread, stops the loop
        }
        
        ; Update our count because we just confirmed a new file exists
        currentFileCount := currentFileCount + 1

        ; --- 3. RENAMING & TABBING ---
        ; Only runs after the check above passes
        
        ; Wait a tiny bit for UI to settle after file generation
        Sleep 500 

        Send "{Tab 2}"
        Sleep 500

        Send "{End}"
        Sleep 50
        Send "{Left 4}"
        Sleep 50

        ; Delete Previous Number logic
        if (A_Index <= 10)
            Send "{Backspace}"
        else
            Send "{Backspace 2}"
        Sleep 50

        ; Type Current Loop Number
        Send A_Index
        Sleep 100

        ; Reset Position for next run
        Send "+{Tab 4}"
        Sleep 500
    }
    MsgBox "Sequence Complete!"
}

; --- HELPER FUNCTIONS ---

CountFiles(dirPath, ext) {
    count := 0
    try {
        Loop Files, dirPath "\" ext
            count++
    }
    return count
}

WaitForNewFile(dirPath, ext, baselineCount, timeoutMS) {
    startTime := A_TickCount
    
    Loop {
        currentCount := CountFiles(dirPath, ext)

        ; SUCCESS: We found more files than we started with
        if (currentCount > baselineCount) {
            return true
        }

        ; TIMEOUT: Took too long
        if (A_TickCount - startTime > timeoutMS) {
            return false
        }

        ; Wait 100ms before checking again (prevents CPU spamming)
        Sleep 100
    }
}

Esc::ExitApp
