import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fft2, ifft2, fftshift

def load_data_cube(filename, samples, X, Y, option):
    """
    Load binary data and format into a 3D data cube.
    Adapted for vertical snake scan: each file contains data for one X position, multiple Y positions.
    """
    try:
        with open(filename, 'rb') as f:
            data_int = np.fromfile(f, dtype=np.int16)
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        return np.zeros((samples, Y, X), dtype=np.complex128)

    # For vertical snake: each file has Y positions for 1 X
    # So, similar logic, but now loop over y, fixed x=0

    # Construct channels
    ch1 = data_int[0::8] + 1j * data_int[4::8]
    ch2 = data_int[1::8] + 1j * data_int[5::8]
    ch3 = data_int[2::8] + 1j * data_int[6::8]
    ch4 = data_int[3::8] + 1j * data_int[7::8]
    
    if option == 1:
        full_channel_data = ch1
    elif option == 2:
        full_channel_data = ch2
    elif option == 3:
        full_channel_data = ch3
    elif option == 4:
        full_channel_data = ch4
    elif option == 5:
        full_channel_data = (ch1 + ch2 + ch3 + ch4) / 4
    else:
        raise ValueError(f"Invalid option: {option}")

    data_cube = np.zeros((samples, Y, X), dtype=np.complex128)

    for y in range(Y):
        for x in range(X):  # X=1
            start_idx = y * samples
            slice_data = full_channel_data[start_idx : start_idx + samples]
            
            # Vertical snake: reverse y direction for even x
            if (x + 1) % 2 == 1:  # Odd x (1-based)
                data_cube[:, y, x] = slice_data
            else:
                data_cube[:, Y - 1 - y, x] = slice_data

    return data_cube

def stack(samples, X, Y, option, data_dir, filename_fn):
    """
    Load data cubes and stack them along the X dimension.
    For vertical snake scan: each file is for one X position, containing Y positions.
    """
    # Initialize 3D array
    data_stack = np.zeros((samples, Y, X), dtype=np.complex128)
    
    for x in range(X): # 0 to X-1
        filename = filename_fn(x + 1)
        filepath = os.path.join(data_dir, filename)
        
        # loadDataCube called with X=1
        cube = load_data_cube(filepath, samples, 1, Y, option)
        
        # Assign to data_stack
        data_stack[:, :, x] = cube[:, :, 0]
        
    return data_stack

def create_matched_filter(x_point_m, x_step_m, y_point_m, y_step_m, z_target):
    """
    Creates Matched Filter.
    """
    f0 = 77e9
    c = 299792458.0 # physconst('lightspeed')
    
    # Coordinates
    # MATLAB: x = xStepM * (-(xPointM-1)/2 : (xPointM-1)/2) * 1e-3;
    # Python: np.arange(-(x_point_m-1)/2, (x_point_m-1)/2 + 0.1) ?
    # Let's use linspace or arange carefully.
    # (-(xPointM-1)/2 : (xPointM-1)/2) generates xPointM points centered at 0.
    
    x_vec = x_step_m * np.arange(-(x_point_m-1)/2, (x_point_m-1)/2 + 1) * 1e-3
    y_vec = y_step_m * np.arange(-(y_point_m-1)/2, (y_point_m-1)/2 + 1) * 1e-3
    
    # Create meshgrid
    # MATLAB: x and y are vectors, then used in sqrt(x.^2 + y.^2 ...)
    # MATLAB implicit expansion or meshgrid.
    # We need 2D arrays.
    # Note: MATLAB 'y' vector is transposed: y = (...).' 
    # So y is column vector, x is row vector.
    # x.^2 + y.^2 creates a grid.
    
    X_grid, Y_grid = np.meshgrid(x_vec, y_vec) 
    # meshgrid(x, y) returns X with rows=y, cols=x. 
    # So X_grid varies along columns, Y_grid varies along rows.
    # This matches MATLAB's implicit expansion of row-vec + col-vec.
    
    z0 = z_target * 1e-3
    
    k = 2 * np.pi * f0 / c
    matched_filter = np.exp(-1j * 2 * k * np.sqrt(X_grid**2 + Y_grid**2 + z0**2))
    
    return matched_filter

def reconstruct_sar_image(sar_data, matched_filter, x_step_m, y_step_m, xy_size_t):
    """
    Reconstruct SAR image.
    """
    # sarData: yPointM x xPointM
    y_point_m, x_point_m = sar_data.shape
    y_point_f, x_point_f = matched_filter.shape
    
    # Zero Padding
    # We need to pad sar_data to match matched_filter (or vice versa, usually filter is larger or same)
    # The MATLAB code handles both cases.
    
    # Pad X
    if x_point_f > x_point_m:
        pad_pre = int(np.floor((x_point_f - x_point_m) / 2))
        pad_post = int(np.ceil((x_point_f - x_point_m) / 2))
        sar_data = np.pad(sar_data, ((0, 0), (pad_pre, pad_post)), 'constant')
    else:
        pad_pre = int(np.floor((x_point_m - x_point_f) / 2))
        pad_post = int(np.ceil((x_point_m - x_point_f) / 2))
        matched_filter = np.pad(matched_filter, ((0, 0), (pad_pre, pad_post)), 'constant')
        
    # Pad Y
    if y_point_f > y_point_m:
        pad_pre = int(np.floor((y_point_f - y_point_m) / 2))
        pad_post = int(np.ceil((y_point_f - y_point_m) / 2))
        sar_data = np.pad(sar_data, ((pad_pre, pad_post), (0, 0)), 'constant')
    else:
        pad_pre = int(np.floor((y_point_m - y_point_f) / 2))
        pad_post = int(np.ceil((y_point_m - y_point_f) / 2))
        matched_filter = np.pad(matched_filter, ((pad_pre, pad_post), (0, 0)), 'constant')
        
    # FFT
    sar_data_fft = fft2(sar_data)
    matched_filter_fft = fft2(matched_filter)
    
    # Multiply and IFFT
    sar_image = fftshift(ifft2(sar_data_fft * matched_filter_fft))
    
    # Crop
    y_point_t, x_point_t = sar_image.shape
    
    x_range_t = x_step_m * np.arange(-(x_point_t-1)/2, (x_point_t-1)/2 + 1)
    y_range_t = y_step_m * np.arange(-(y_point_t-1)/2, (y_point_t-1)/2 + 1)
    
    # Indices
    ind_x = (x_range_t > -xy_size_t/2) & (x_range_t < xy_size_t/2)
    ind_y = (y_range_t > -xy_size_t/2) & (y_range_t < xy_size_t/2)
    
    # Apply crop
    # np.ix_ constructs open meshes from multiple sequences
    sar_image = sar_image[np.ix_(ind_y, ind_x)]
    x_range_t = x_range_t[ind_x]
    y_range_t = y_range_t[ind_y]
    
    return sar_image, x_range_t, y_range_t

def main():
    # Configuration
    data_dir = 'testdummydata3'  # Update to your new data directory
    X = 24  # Now X is the number of files (one per x position)
    Y = 400  # Y is the number of y positions per file
    samples = 512
    
    def filename_fn(x):
        return f"adc_data{x}_Raw_0.bin"  # Assuming files are named by x
        
    print("Loading data...")
    raw_data = stack(samples, X, Y, 1, data_dir, filename_fn)
    
    # Parameters
    n_fft_time = 1024
    z0 = 323e-3
    dx = 290/400
    dy = 205/100 # Note: As per original MATLAB code
    n_fft_space = 1024
    
    c = 299792458.0
    fS = 9121e3
    Ts = 1/fS
    K = 63.343e12
    
    # Range FFT
    print("Processing Range FFT...")
    # MATLAB: fft(rawData, nFFTtime) -> operates on first dimension (samples)
    raw_data_fft = fft(raw_data, n=n_fft_time, axis=0)
    
    # Range focusing
    tI = 4.5225e-10
    k_idx = int(round(K * Ts * (2 * z0 / c + tI) * n_fft_time))
    
    # Extract slice
    # MATLAB: sarData = squeeze(rawDataFFT(k+1,:,:));
    # Python: k_idx is 0-based.
    sar_data = raw_data_fft[k_idx, :, :]
    
    # Create Matched Filter
    print("Creating Matched Filter...")
    matched_filter = create_matched_filter(n_fft_space, dx, n_fft_space, dy, z0*1e3)
    
    # Create SAR Image
    print("Reconstructing SAR Image...")
    im_size = 200
    sar_image, x_axis, y_axis = reconstruct_sar_image(sar_data, matched_filter, dx, dy, im_size)
    
    # Plot
    print("Plotting...")
    plt.figure()
    # MATLAB: mesh(xRangeT,yRangeT,abs(fliplr(sarImage))...)
    # fliplr flips left/right (columns).
    # We can use pcolormesh or imshow.
    
    # Note on orientation:
    # MATLAB mesh(x, y, Z) plots Z against x and y.
    # fliplr(sarImage) reverses the x-axis direction of the image content?
    # Let's just plot abs(sar_image) and see.
    # Usually we want to align with how MATLAB displays it.
    
    # MATLAB: fliplr(sarImage)
    to_plot = np.abs(np.fliplr(sar_image))
    
    plt.pcolormesh(x_axis, y_axis, to_plot, cmap='jet', shading='gouraud')
    plt.xlabel('Horizontal (mm)')
    plt.ylabel('Vertical (mm)')
    plt.title('SAR Image - Matched Filter Response')
    plt.axis('equal')
    plt.colorbar()
    
    # Save output
    output_file = 'sar_image_python.png'
    plt.savefig(output_file)
    print(f"Saved image to {output_file}")
    plt.show()

if __name__ == "__main__":
    main()
