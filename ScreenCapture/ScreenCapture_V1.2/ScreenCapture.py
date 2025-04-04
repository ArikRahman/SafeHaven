# Copy and paste these in the terminal to download packages
    # pip install numpy
    # pip install opencv-python
    # pip install pillow==9.5.0

# Required for ScreenCapture.py
    # pip install pygetwindow pywin32 pillow
    # pip install --upgrade Pillow

# Note: sure if needed anymore 
    # pip install pygetwindow pyautogui pyscreeze
    # pip install pyautogui --use-pep517    
    # pip install --upgrade pyautogui pyscreeze pillow
    # pip install pyautogui pygetwindow opencv-python

# V1.2 Change Log:
    # Changed from window screen capture to headless screen capture
    # Previous screen capture requires bringing camera feed to the front which is annoying
    # Headless screen capture allows screen shot on background windows

# How it works:
    # Find window by title
    # Use Window GDI to capture
    # Save as png

# Note:
    # IMPORTANT: DISABLE HARDWARE ACCELERATION ON CHROME
    # Background window capture is unsuccessful. The window is not fully captured and the bottom and right are partially clipped. Example is in "C:\GitHub\SafeHaven\Samples\SC_V1.2_Failed_Capture\Screenshot.png"

# Imports
import pygetwindow as gw
import win32gui
import win32ui
import win32con
import time
from PIL import Image

# Print all open window titles
for window in gw.getAllTitles():
    print(window)

# Window title to capture (modify accordingly)
window_title = "1.jpg (480×270) - Google Chrome"  # PUT WINDOW NAME INSIDE ""

# Get window handle
try:
    win = gw.getWindowsWithTitle(window_title)[0]
    hwnd = win._hWnd  # Get the window handle

    # Get exact window rectangle (including title bar)
    # Bring the window to the foreground
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # Restore if minimized
    win32gui.SetForegroundWindow(hwnd)  # Bring to front
    time.sleep(0.5)  # Small delay to let it render properly

    # Get full window rectangle (including title bar & borders)
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    # Capture the window
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(bitmap)

    # Copy full window pixels
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # Convert bitmap to image
    bitmap_info = bitmap.GetInfo()
    img = Image.frombuffer(
        'RGB',
        (bitmap_info['bmWidth'], bitmap_info['bmHeight']),
        bitmap.GetBitmapBits(True),
        'raw',
        'BGRX',
        0,
        1
    )

    # Save the screenshot
    img.save(r"C:\GitHub\SafeHaven\Samples\Screenshot.png")  # Modify path

    # Cleanup
    win32gui.DeleteObject(bitmap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    print("Screenshot saved successfully!")

except IndexError:
    print("Window not found! Check the title.")
except Exception as e:
    print(f"Error: {e}")
