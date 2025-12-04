#Requires AutoHotkey v2.0

; F1 starts the script
F1::
{
    ; Wait a moment before starting
    Sleep 200

    ; Loop from 1 to 100
    Loop 100
    {
        ; --- YOUR WORKING LOGIC ---
        Send "{Enter}"
        Sleep 10
        
        Send "{Enter}"
        Sleep 1000
        
        Send "{Tab 2}"
        Sleep 1000

        ; Navigate inside filename
        Send "{End}"
        Sleep 50
        Send "{Left 4}"
        Sleep 50

        ; Delete Previous Number Logic
        if (A_Index <= 10)
        {
            Send "{Backspace}"
        }
        else
        {
            Send "{Backspace 2}"
        }
        Sleep 50

        ; Type the current number
        Send A_Index
        Sleep 100

        ; Reset position in mmWave Studio
        Send "+{Tab 4}"
        Sleep 30

        ; --- NEW STEP: SWITCH WINDOW, TYPE 'a', SWITCH BACK ---
        
        Sleep 500       ; Pause briefly before switching
        Send "!{Tab}"   ; Alt + Tab to the other window
        Sleep 500       ; Wait 0.5s for the window to actually open
        
        Send "a"        ; Type the letter 'a'
        Sleep 100
        
        Send "!{Tab}"   ; Alt + Tab back to mmWave Studio
        Sleep 1000      ; Wait 1s to ensure mmWave Studio is active before restarting loop
    }
}

; Press Esc to stop immediately
Esc::ExitApp