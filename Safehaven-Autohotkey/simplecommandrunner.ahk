#Requires AutoHotkey v2.0

global running := false

z::
{
    if (running)
    {
        running := false
        MsgBox "Loop stopped!"
        return
    }

    running := true

    ; Infinite loop - press 'z' again to stop
    while (running)
    {
        ; --- SWITCH WINDOW & TRIGGER RP5 ---
        Sleep 200
        Send "!{Tab}"
        Sleep 500
        Send "clear" ; Ctrl+L usually clears screen
        A_Clipboard := ""
        Send "{Enter}"
        Sleep 100
        ; 1. Send the Python command
        Send "python3 motorTest_rev10.py right=2000 --force"
        sleep 100
        Send "{Enter}"
        sleep 100
        ; 2. Wait for "done" to appear
        Loop
        {
            ; Exit if user stopped the loop
            if (!running)
                break

            ; Clear clipboard so we don't read old data
            A_Clipboard := ""

            ; Select all text in terminal (Ctrl+A) then Copy (Ctrl+C)
            ; NOTE: In some terminals (like Unix shells), Ctrl+A goes to start of line.
            ; If so, we use Shift+Up or similar.
            ; A reliable "grab last line" method for most terminals:
            Send "^+a"  ; Select All (often Ctrl+Shift+A in terminals to avoid SIGINT conflict)
            ; If your terminal uses standard Ctrl+A, change above to: Send "^a"

            Sleep 50
            Send "^c"   ; Copy

            ; Wait up to 0.2s for clip to contain text
            ClipWait(0.2)

            ; Check if the LAST few characters contain "done"
            ; We look at the last 50 chars to be safe
            if (InStr(SubStr(A_Clipboard, -100), "done"))
            {
                ; Found it! Clean up selection (press End to deselect)
                ; Send "{End}"
                break
            }

            ; Wait before checking again to save CPU
            Sleep 500
        }

        Send "!{Tab}"
        Sleep 1000

        ; Loop will automatically continue unless stopped
    }
}
