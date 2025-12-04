#Requires AutoHotkey v2.0

; F1 starts the script
F1::
{
    ; WAIT 2 SECONDS before starting so you can get ready
    Sleep 200

    ; Loop from 1 to 100
    Loop 100
    {
        ; 1. Enter, Tab, Enter, Tab Tab Tab
        Send "{Enter}"
        Sleep 10
      
        Send "{Enter}"
        Sleep 1000
        Send "{Tab 2}"
        Sleep 1000

        ; 2. Navigate inside the filename
        ; Press END to jump to the very end of the line
        Send "{End}"
        Sleep 50
        ; Move back 4 spots (past ".bin")
        Send "{Left 4}"
        Sleep 50

        ; 3. Delete Previous Number Logic
        ; Loop 1-10: Deletes the previous single digit (0-9)
        ; Loop 11+: Deletes the previous double digit (10-99)
        if (A_Index <= 10)
        {
            Send "{Backspace}"
        }
        else
        {
            Send "{Backspace 2}"
        }
        Sleep 50

        ; 4. Type the current number
        Send A_Index
        Sleep 100

        ; 5. Shift+Tab 4 times to reset position
        Send "+{Tab 4}"
        Sleep 30
    }
}

; --- PANIC BUTTON ---
; Press Esc to stop the script immediately at any time
Esc::ExitApp