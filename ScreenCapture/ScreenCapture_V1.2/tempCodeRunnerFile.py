# Get window handle
# try:
#     win = gw.getWindowsWithTitle(window_title)[0]
#     hwnd = win._hWnd  # Get the window handle

#     # Get exact window rectangle (including title bar)
#     left, top, right, bottom = win32gui.GetWindowRect(hwnd)
#     width = right - left
#     height = bottom - top

#     # Capture the window
#     hwndDC = win32gui.GetWindowDC(hwnd)
#     mfcDC = win32ui.CreateDCFromHandle(hwndDC)
#     saveDC = mfcDC.CreateCompatibleDC()
#     bitmap = win32ui.CreateBitmap()
#     bitmap.CreateCompatibleBitmap(mfcDC, width, height)
#     saveDC.SelectObject(bitmap)
#     saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

#     # Convert bitmap to an image
#     bitmap_info = bitmap.GetInfo()
#     img = Image.frombuffer(
#         'RGB',
#         (bitmap_info['bmWidth'], bitmap_info['bmHeight']),
#         bitmap.GetBitmapBits(True),
#         'raw',
#         'BGRX',
#         0,
#         1
#     )

#     # Save the screenshot
#     img.save(r"C:\Users\USER\Desktop\Screenshot.png")  # Modify path

#     # Cleanup
#     win32gui.DeleteObject(bitmap.GetHandle())
#     saveDC.DeleteDC()
#     mfcDC.DeleteDC()
#     win32gui.ReleaseDC(hwnd, hwndDC)

#     print("Screenshot saved successfully!")

# except IndexError:
#     print("Window not found! Check the title.")