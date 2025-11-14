import cmath

import numpy as np

# print("Loading DCA1000 reader...")


def readDCA1000(
    filename: str = "first.bin",
    numberOfWindows: int = 4,
    numADCBits: int = 16,
    isReal: bool = True,
    trim_to_windows: bool = False,
) -> np.ndarray:
    """
    Extract ADC data from a DCA1000 binary file

    Args:
        filename (str):        Path to .bin file
        numberOfWindows (int): Number of windows to make from the data
        numADCBits (int):      ADC bit resolution (default 16)
        isReal (bool):         True for real-only data, False for complex data
        trim_to_windows (bool):  True to trim data length to be divisible by numberOfWindows

    Returns:
        adcData (np.ndarray): Numpy array of converted ADC data
    """
    # Read binary file
    adcData = np.fromfile(filename, dtype="int16")

    # If not a 16 bit ADC, then the data is unsigned: need to convert to signed to correct the data
    if numADCBits != 16:
        l_max = 2 ** (numADCBits - 1) - 1
        adcData[adcData > l_max] = adcData[adcData > l_max] - 2**numADCBits

    # Trim data to be evenly divisible into the specified number of windows
    if trim_to_windows:
        new_len = len(adcData) - len(adcData) % numberOfWindows
        adcData = adcData[:new_len]

    # Only real data in the file
    if isReal:
        adcData = adcData.reshape(numberOfWindows, -1)
    # Combine the real and imaginary parts of the complex data (first four lanes are real, last four are imaginary) using I + jQ
    else:
        adcData = adcData.reshape(numberOfWindows * 2, -1)
        adcData = adcData[[0, 1, 2, 3], :] + cmath.sqrt(-1) * adcData[[4, 5, 6, 7], :]
    return adcData


print(readDCA1000())
