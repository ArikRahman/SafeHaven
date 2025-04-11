What this program does:
    # Capture and save a screenshot of an active Chrome window
    # Initialization of window capture is manual and not automatic

Installation:
# Copy and paste these in the terminal to download packages
    Note: Use this installation method. The requirements.txt is giving problems with pygetwindow module
    pip install numpy
    pip install opencv-python
    pip install pillow==9.5.0
    pip install pygetwindow pywin32 pillow
    pip install --upgrade Pillow
    pip install pygetwindow pyautogui pyscreeze
    pip install pyautogui --use-pep517    
    pip install --upgrade pyautogui pyscreeze pillow
    pip install pyautogui pygetwindow opencv-python

OR

    Note: replace /full/path/to/ with your path
    Note: Ran into issues with this method of installation and points to an issue with pillow==9.5.0 and pygetwindow 
    pip install -r /full/path/to/requirements.txt

    SafeHaven example: pip install -r C:\GitHub\SafeHaven\ScreenCapture\ScreenCapture_V1.3\requirements.txt
    
# V1.4 Change Log:
    # Uses primary approach of window capture from V1.1 by bringing window over the IDE and screenshot
    # Supporting readme.md file is created
    # Capture window with keyword. Keyword is the camera IP address
    # After window is brought to the front and the screenshot is taken, VSC/cmd is restored and brought to the front

# Notes:
    # V1.2 attempted headless window capture to capture windows in the background
    # This approach was partially unsuccessful because V1.2 program does not fully capture screen
    # Part of the bottom and right are cropped in the picture. Example can be seen in "C:\GitHub\SafeHaven\Samples\SC_V1.2_Failed_Capture\Screenshot.png" 
    # Speculated reasons as to why this didn't work is rendering issues with background windows or incorrect window size

# How it works:
    # Find window by keyword in the title
    # Use pyautogui to capture window
    # Save as png
    # Repeated captures overwrite previous saved screenshot

# How to use it:
    # Complete the installation and install modules
    # Execute the program and see available windows in the terminal
    # Replace keyword with Camera IP address
    # Replace PATH with your desired destination in screenshot.save(r"C:\PATH\Screenshot.png")
