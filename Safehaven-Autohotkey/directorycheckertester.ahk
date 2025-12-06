#Requires AutoHotkey v2.0

; folderPath := "C:\Users\arikrahman\Documents\AutoHotkey\test"
folderPath := "C:\ti\mmwave_studio_02_01_01_00\mmWaveStudio\PostProc"
lastCount := CountBinFiles(folderPath) ; Get initial count

; Check every 500ms
SetTimer CheckForNewBin, 500

CheckForNewBin() {
    global lastCount
    currentCount := CountBinFiles(folderPath)

    if (currentCount > lastCount) {
        Send "!{Tab}"      ; Alt+Tab if new .bin file found
        lastCount := currentCount ; Update count to prevent loop
    }
}

CountBinFiles(dir) {
    count := 0
    Loop Files, dir "\*.bin" ; Only counts .bin files
        count++
    return count
}
