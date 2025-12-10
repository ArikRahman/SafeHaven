import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.fft import fft, fft2, ifft2, fftshift


def load_data_cube(filename, samples, X, Y, option):
    """
    Load binary data and format into a 3D data cube.
    Replicates loadDataCube.m behavior.
    """
    try:
        with open(filename, 'rb') as f:
            data_int = np.fromfile(f, dtype=np.int16)
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        return np.zeros((samples, Y, X), dtype=np.complex128)

    chunk_size = samples * 4
    input_length = len(data_int)
    w = 1

    # Format data as I1+Q1, I2+Q2, etc.
    # MATLAB: 1:4:end corresponds to 0::4 in Python
    # MATLAB: 1:8:end corresponds to 0::8 in Python
    # MATLAB: 5:8:end corresponds to 4::8 in Python
    
    # bindata initialization
    # In MATLAB: bindata = zeros(inputlength / 2, 1);
    # We can just compute the complex values directly.
    
    # data_int is 1D array.
    # I1 = data_int[0::8], Q1 = data_int[4::8]
    # I2 = data_int[1::8], Q2 = data_int[5::8]
    # ...
    
    # We need to construct bindata which has length input_length / 2.
    # bindata has 4 interleaved channels.
    # Channel 1: indices 0, 4, 8... in bindata
    # Channel 2: indices 1, 5, 9... in bindata
    
    # Check for 2 RX vs 4 RX based on file size
    # Expected samples per channel = X * samples (assuming Y=1 per file)
    expected_samples_per_channel = X * samples
    
    # 4 RX: 4 * 2 (I+Q) * int16 = 8 int16s per sample.
    # 2 RX: 2 * 2 (I+Q) * int16 = 4 int16s per sample.
    
    if len(data_int) == expected_samples_per_channel * 4:
        # 2 RX Mode (I1 I2 Q1 Q2 format)
        # print(f"Detected 2 RX channels in {filename}")
        ch1 = data_int[0::4] + 1j * data_int[2::4]
        ch2 = data_int[1::4] + 1j * data_int[3::4]
        ch3 = np.zeros_like(ch1)
        ch4 = np.zeros_like(ch1)
    else:
        # Default to 4 RX Mode (I1 I2 I3 I4 Q1 Q2 Q3 Q4 format)
        ch1 = data_int[0::8] + 1j * data_int[4::8]
        ch2 = data_int[1::8] + 1j * data_int[5::8]
        ch3 = data_int[2::8] + 1j * data_int[6::8]
        ch4 = data_int[3::8] + 1j * data_int[7::8]
    
    # Now we need to select based on option.
    # The MATLAB code constructs 'bindata' interleaving these, then slices 'bindata'.
    # But we can just select the channel directly since we know the pattern.
    
    # MATLAB:
    # option 1: slice = bindata(start_idx:4:end_idx) -> This corresponds to Channel 1
    # option 2: slice = bindata(start_idx+1:4:end_idx) -> This corresponds to Channel 2
    # ...
    
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

    # Populate data_cube
    # Note: In mainSARORIGINAL, loadDataCube is called with Y=1.
    # So the loop over y is just y=0 (0-indexed).
    
    for y in range(Y):
        for x in range(X):
            # MATLAB: start_idx = ((x - 1) * chunk_size) + 1; (1-based)
            # Python: start_idx = x * samples (since chunk_size in MATLAB was samples*4, but that was for the raw int16 array? No.)
            # Let's trace carefully.
            # MATLAB: chunk_size = samples * 4; (This is in terms of int16 samples? No, bindata indices?)
            # data_int length is N. bindata length is N/2.
            # chunk_size in MATLAB seems to be number of elements in bindata per chirp?
            # bindata has 4 channels interleaved.
            # So for one chirp (one x, one y), we need 'samples' points per channel.
            # So total points in bindata for one chirp is samples * 4.
            # Correct.
            
            # So full_channel_data has length (N/2)/4 = N/8.
            # Each chirp has 'samples' data points.
            # So we just need to slice full_channel_data.
            
            start_idx = x * samples # For the current x
            # Wait, if Y > 1, we need to account for y.
            # In MATLAB: start_idx = ((x - 1) * chunk_size) + 1;
            # It resets for every y loop?
            # MATLAB:
            # for y = 1:Y
            #   for x = 1:X
            #     start_idx = ((x - 1) * chunk_size) + 1;
            #     slice = bindata(start_idx:4:end_idx);
            
            # This implies that for every y, it reads the SAME x chunks from the beginning of bindata?
            # That seems wrong if the file contains multiple y scans.
            # BUT, in mainSARORIGINAL, loadDataCube is called with Y=1.
            # And the filename changes for every y in stack().
            # So each file contains only 1 Y row (but X columns).
            # So the logic holds: for a single file, we iterate x.
            
            # So for a given x, the data is at x * samples in the specific channel array.
            
            slice_data = full_channel_data[x*samples : (x+1)*samples]
            
            # Handle truncated data (pad with zeros if file is shorter than expected)
            if len(slice_data) < samples:
                print(f"Warning: Truncated data in {filename} at x={x+1}, padding with zeros.")
                padded = np.zeros(samples, dtype=np.complex128)
                padded[:len(slice_data)] = slice_data
                slice_data = padded

            # Snake pattern logic
            # MATLAB: if rem(y, 2) == 1 (odd) -> data_cube(:, y, x)
            # else -> data_cube(:, y, X + 1 - x)
            # Python y is 0-indexed. y=0 corresponds to MATLAB y=1 (odd).
            # So if y % 2 == 0 (Python even, MATLAB odd) -> normal
            
            if (y + 1) % 2 == 1: # Odd in MATLAB terms
                data_cube[:, y, x] = slice_data * w
            else:
                data_cube[:, y, X - 1 - x] = slice_data * w

    return data_cube


def stack(samples, X, Y, option, data_dir, filename_fn):
    """
    Load data cubes and stack them along the Y dimension.
    """
    # Initialize 3D array
    # MATLAB: dataStack = zeros(samples, Y, X);
    data_stack = np.zeros((samples, Y, X), dtype=np.complex128)
    
    for y in range(Y): # 0 to Y-1
        # MATLAB y is 1-based. filename_fn expects 1-based index?
        # mainSARORIGINAL: filenameFn = @(y) "scan" + y + "_Raw_0.bin";
        # So we should pass y+1.
        
        filename = filename_fn(y + 1)
        filepath = os.path.join(data_dir, filename)
        
        # loadDataCube called with Y=1
        # MATLAB: loadDataCube(filepath, samples, X, 1, option)
        # Returns (samples, 1, X)
        cube = load_data_cube(filepath, samples, X, 1, option)
        
        # Assign to data_stack
        # MATLAB: dataStack(:, y, :) = ...
        data_stack[:, y, :] = cube[:, 0, :]
        
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
    # (-(xPointM-1)/2 : (x_point_m-1)/2) generates xPointM points centered at 0.
    
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


def reconstruct_sar_image(sar_data, matched_filter, x_step_m, y_step_m, x_size_t, y_size_t):
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
    ind_x = (x_range_t > -x_size_t/2) & (x_range_t < x_size_t/2)
    ind_y = (y_range_t > -y_size_t/2) & (y_range_t < y_size_t/2)
    
    # Apply crop
    # np.ix_ constructs open meshes from multiple sequences
    sar_image = sar_image[np.ix_(ind_y, ind_x)]
    x_range_t = x_range_t[ind_x]
    y_range_t = y_range_t[ind_y]
    
    return sar_image, x_range_t, y_range_t


def soft_threshold(x, thresh):
    """
    Soft thresholding operator for complex values.
    S_t(x) = x * max(|x| - t, 0) / |x|
    """
    abs_x = np.abs(x)
    # Avoid division by zero
    scale = np.maximum(abs_x - thresh, 0) / (abs_x + 1e-10)
    return x * scale


def reconstruct_sar_image_fista(sar_data, matched_filter, x_step_m, y_step_m, x_size_t, y_size_t, iterations=20, lambda_ratio=0.05):
    """
    Reconstruct SAR image using FISTA (Fast Iterative Shrinkage-Thresholding Algorithm).
    Solves: min_x || H*x - y ||^2 + lambda ||x||_1
    where y is raw data, H is forward operator (convolution with point response).
    """
    # Pad X
    y_point_m, x_point_m = sar_data.shape
    y_point_f, x_point_f = matched_filter.shape
    
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

    # Forward Operator Kernel (H)
    # matched_filter is the "Backward" kernel (conjugate of H).
    # So H = conj(matched_filter).
    H_spatial = np.conj(matched_filter)
    H_hat = fft2(H_spatial)
    
    # Data (Y)
    Y_hat = fft2(sar_data)
    
    # Lipschitz Constant
    # L = max eigenvalue of H^H H = max |H_hat|^2
    L = np.max(np.abs(H_hat)**2)
    step_size = 1.0 / L
    
    # Initial Guess (Matched Filter Solution)
    # X_hat = Y_hat * conj(H_hat)
    X_hat = Y_hat * np.conj(H_hat)
    x_k = ifft2(X_hat)
    
    # Determine Lambda
    lambda_val = lambda_ratio * np.max(np.abs(x_k))
    
    y_k = x_k.copy()
    t_k = 1.0
    
    for i in range(iterations):
        # Gradient: H^H * (H * y_k - Y)
        Y_k_hat = fft2(y_k)
        Diff_hat = (H_hat * Y_k_hat) - Y_hat
        Grad_hat = np.conj(H_hat) * Diff_hat
        grad = ifft2(Grad_hat)
        
        z_k = y_k - step_size * grad
        x_next = soft_threshold(z_k, lambda_val * step_size)
        
        t_next = (1 + np.sqrt(1 + 4 * t_k**2)) / 2
        y_next = x_next + ((t_k - 1) / t_next) * (x_next - x_k)
        
        x_k = x_next
        y_k = y_next
        t_k = t_next
        
    sar_image = fftshift(x_k)
    
    # Crop
    y_point_t, x_point_t = sar_image.shape
    x_range_t = x_step_m * np.arange(-(x_point_t-1)/2, (x_point_t-1)/2 + 1)
    y_range_t = y_step_m * np.arange(-(y_point_t-1)/2, (y_point_t-1)/2 + 1)
    
    ind_x = (x_range_t > -x_size_t/2) & (x_range_t < x_size_t/2)
    ind_y = (y_range_t > -y_size_t/2) & (y_range_t < y_size_t/2)
    
    sar_image = sar_image[np.ix_(ind_y, ind_x)]
    x_range_t = x_range_t[ind_x]
    y_range_t = y_range_t[ind_y]
    
    return sar_image, x_range_t, y_range_t


def reconstruct_sar_image_bpa(raw_data_fft, x_step_m, y_step_m, z_target_mm, 
                              scan_width_x, scan_height_y, 
                              display_width_x, display_height_y):
    """
    Reconstruct SAR image using Back Projection Algorithm (BPA).
    """
    c = 299792458.0
    f_start = 77e9
    slope = 63.343e12
    f_s = 9121e3
    n_fft = raw_data_fft.shape[0]
    
    # Aperture Grid
    n_y_ap, n_x_ap = raw_data_fft.shape[1], raw_data_fft.shape[2]
    
    # Aperture coordinates (centered at 0)
    # Note: x_step_m is usually dx (280/400)
    # y_step_m is usually dy (1.0)
    # We need to match the physical aperture dimensions
    
    # The aperture grid matches the scan dimensions
    # x_ap_vec = np.linspace(-scan_width_x/2, scan_width_x/2, n_x_ap) * 1e-3 # mm to m
    # y_ap_vec = np.linspace(-scan_height_y/2, scan_height_y/2, n_y_ap) * 1e-3
    
    # Using the step sizes provided (which are derived from scan_width / counts)
    x_ap_vec = x_step_m * np.arange(-(n_x_ap-1)/2, (n_x_ap-1)/2 + 1) * 1e-3
    y_ap_vec = y_step_m * np.arange(-(n_y_ap-1)/2, (n_y_ap-1)/2 + 1) * 1e-3
    
    # Flatten aperture for vectorization
    # Meshgrid: X varies along columns, Y along rows
    X_ap, Y_ap = np.meshgrid(x_ap_vec, y_ap_vec)
    X_ap_flat = X_ap.flatten()
    Y_ap_flat = Y_ap.flatten()
    
    # Flatten data to match aperture
    # raw_data_fft is (Bins, Y, X). Transpose to (Y, X, Bins) then flatten spatial
    # Actually, let's keep bins first: (Bins, N_ap)
    data_flat = raw_data_fft.reshape(n_fft, -1)
    
    # Image Grid
    # We want to reconstruct an image of size (display_height_y, display_width_x)
    # But what is the resolution?
    # Usually we want the same resolution as the aperture step or finer.
    # Let's use the same step size as the aperture for simplicity, but cover the display area.
    
    n_x_img = int(display_width_x) # Pixels
    n_y_img = int(display_height_y) # Pixels
    
    # Image coordinates
    x_img_vec = x_step_m * np.arange(-(n_x_img-1)/2, (n_x_img-1)/2 + 1) * 1e-3
    y_img_vec = y_step_m * np.arange(-(n_y_img-1)/2, (n_y_img-1)/2 + 1) * 1e-3
    
    sar_image = np.zeros((n_y_img, n_x_img), dtype=np.complex128)
    
    z0 = z_target_mm * 1e-3
    
    # Pre-calculate constants
    # k_idx = R * (2 * slope / c) * (n_fft / f_s)
    range_to_idx_scale = (2 * slope / c) * (n_fft / f_s)
    
    # Phase correction factor: exp(j * 4 * pi * f_start * R / c)
    phase_scale = 4 * np.pi * f_start / c
    
    print(f"  BPA: Reconstructing {n_x_img}x{n_y_img} pixels from {n_x_ap*n_y_ap} aperture points...")
    
    # Iterate over Image Rows to save memory
    for i, y_val in enumerate(y_img_vec):
        # Coordinates for this row of pixels: (N_x_img, )
        # We broadcast against aperture: (N_ap, )
        
        # Distances: R[pixel_x, aperture_idx]
        # R = sqrt( (x_img - x_ap)^2 + (y_img - y_ap)^2 + z0^2 )
        
        # Expand dims for broadcasting
        # x_img_vec: (N_x_img, 1)
        # X_ap_flat: (1, N_ap)
        dx = x_img_vec[:, np.newaxis] - X_ap_flat[np.newaxis, :]
        dy = y_val - Y_ap_flat[np.newaxis, :] # y_val is scalar, Y_ap_flat is vector
        
        R = np.sqrt(dx**2 + dy**2 + z0**2)
        
        # Calculate Bin Indices
        bin_indices = R * range_to_idx_scale
        bin_indices_int = np.round(bin_indices).astype(int)
        
        # Clip indices
        np.clip(bin_indices_int, 0, n_fft - 1, out=bin_indices_int)
        
        # Gather Data
        # data_flat is (Bins, N_ap)
        # We need data at [bin_indices[pix, ap], ap]
        # Advanced indexing:
        # We want result of shape (N_x_img, N_ap)
        
        # Create aperture indices array
        ap_indices = np.arange(n_x_ap * n_y_ap)
        # Broadcast ap_indices to match bin_indices shape
        ap_indices_grid = np.broadcast_to(ap_indices, bin_indices_int.shape)
        
        # Fetch values
        values = data_flat[bin_indices_int, ap_indices_grid]
        
        # Phase Correction
        # We want to compensate for the phase rotation due to range
        # The received signal has phase ~ -4*pi*f*R/c
        # So we multiply by +4*pi*f*R/c
        phases = np.exp(1j * phase_scale * R)
        
        # Sum over aperture (axis 1)
        row_sum = np.sum(values * phases, axis=1)
        
        sar_image[i, :] = row_sum
        
    return sar_image, x_img_vec * 1e3, y_img_vec * 1e3 # Return mm axes


def parse_z_value(z_str):
    """
    Parse a Z index string and return value in millimeters as a float.
    Accepts formats like '300', '300mm', '0.3m'.
    """
    if z_str is None:
        return None
    s = str(z_str).strip().lower()
    try:
        if s.endswith('mm'):
            return float(s[:-2])
        elif s.endswith('m'):
            # meters to mm
            return float(s[:-1]) * 1000.0
        else:
            return float(s)
    except Exception:
        raise argparse.ArgumentTypeError(f"Invalid zindex value: {z_str}")


def get_unique_filename(base_name):
    """
    Returns a unique filename by appending a counter if the file already exists.
    E.g., 'output.html' -> 'output_1.html', 'output_2.html', etc.
    """
    if not os.path.exists(base_name):
        return base_name
    
    name, ext = os.path.splitext(base_name)
    counter = 1
    while True:
        new_name = f"{name}_{counter}{ext}"
        if not os.path.exists(new_name):
            return new_name
        counter += 1


def main():
    parser = argparse.ArgumentParser(description='SAR Reconstruction (rev3)')
    parser.add_argument('--folder', type=str, default='dumps', help='Folder containing scan data')
    parser.add_argument('--zindex', type=str, default=None, help="Single Z slice to process (e.g., '300', '300mm', '0.3m')")
    parser.add_argument('--zstep', type=str, default=None, help="Step size for Z sweep (e.g., '3', '3mm', '0.003m')")
    parser.add_argument('--zstart', '--z_start', dest='zstart', type=str, default=None, help="Start Z value for sweep (e.g., '300', '300mm', '0.3m')")
    parser.add_argument('--zend', '--z_end', dest='zend', type=str, default=None, help="End Z value for sweep (e.g., '800', '800mm', '0.8m')")
    parser.add_argument('--xyonly', action='store_true', help='Only generate the X-Y image; skip X-Z and Y-Z heatmaps')
    parser.add_argument('--3d_scatter', dest='scatter3d', action='store_true', help='Generate interactive 3D scatter plot')
    parser.add_argument('--3d_scatter_intensity', dest='scatter3d_intensity', type=float, default=95.0, help='Initial percentile threshold for 3D scatter plot (0-100)')
    parser.add_argument('--plotly', action='store_true', help='Generate interactive Plotly HTML with Z-slider instead of Matplotlib window')
    parser.add_argument('--mat_plot_lib', action='store_true', help='Force use of Matplotlib for visualization, overriding --plotly')
    parser.add_argument('--sar_dump', type=str, default=None, help='Directory to dump processed SAR images (Z-slices)')
    parser.add_argument('--silent', action='store_true', help='Suppress all graphical output and heatmap generation')
    parser.add_argument('--algo', type=str, default='mf', choices=['mf', 'fista', 'bpa'], help="Reconstruction algorithm: 'mf' (Matched Filter), 'fista' (Fast Iterative Shrinkage-Thresholding), or 'bpa' (Back Projection)")
    parser.add_argument('--fista_iters', type=int, default=20, help="Number of FISTA iterations")
    parser.add_argument('--fista_lambda', type=float, default=0.05, help="FISTA regularization ratio (0.0 to 1.0)")
    parser.add_argument('--frames_in_x', type=int, default=800, help='Number of frames in X dimension (default: 800)')
    parser.add_argument('--frames_in_y', type=int, default=40, help='Number of frames in Y dimension (default: 40)')
    args = parser.parse_args()

    # Configuration
    data_dir = args.folder
    X = args.frames_in_x
    Y = args.frames_in_y
    samples = 512

    def filename_fn(y):
        return f"scan{y}_Raw_0.bin"
        
    print("Loading data...")
    raw_data = stack(samples, X, Y, 1, data_dir, filename_fn)

    # Parameters
    n_fft_time = 1024
    # z0 will be iterated
    # dx = 290/400
    # dy = 205/100 # Note: As per original MATLAB code
    

    #This is our config 12-07
    dx = 18 * 0.018  # = 0.324 mm (Speed * Periodicity)
    dy = 1.0
    n_fft_space = 1024


    c = 299792458.0
    fS = 9121e3
    Ts = 1/fS
    K = 63.343e12

    # Range FFT
    print("Processing Range FFT...")
    # MATLAB: fft(rawData, nFFTtime) -> operates on first dimension (samples)
    raw_data_fft = fft(raw_data, n=n_fft_time, axis=0)

    # Z-axis iteration parameters
    # Original code used z0 = 323mm. We sweep around this value.
    z_start_mm = 300
    z_end_mm = 800
    z_step_mm = 3 # Default step (mm)

    # If the user passed a single zindex, override the sweep
    z_index_val = parse_z_value(args.zindex) if args.zindex is not None else None
    # zstart/zend overrides, parse and validate if present
    if args.zstart is not None:
        z_start_parsed = parse_z_value(args.zstart)
        if z_start_parsed is None:
            raise ValueError(f"Invalid zstart value: {args.zstart}")
        z_start_mm = z_start_parsed
    if args.zend is not None:
        z_end_parsed = parse_z_value(args.zend)
        if z_end_parsed is None:
            raise ValueError(f"Invalid zend value: {args.zend}")
        z_end_mm = z_end_parsed
    if z_start_mm >= z_end_mm:
        raise ValueError(f"zstart ({z_start_mm}mm) must be less than zend ({z_end_mm}mm)")
    # If the user passed a zstep value, override default z_step_mm
    if args.zstep is not None:
        z_step_val = parse_z_value(args.zstep)
        if z_step_val <= 0:
            raise ValueError(f"Invalid zstep: {z_step_val}. Must be > 0.")
        z_step_mm = z_step_val
    if z_index_val is not None:
        z_values = np.array([z_index_val])
        print(f"Processing single Z = {z_index_val} mm specified via --zindex")
    else:
        z_values = np.arange(z_start_mm, z_end_mm + z_step_mm, z_step_mm)
        print(f"Starting Z-sweep from {z_start_mm}mm to {z_end_mm}mm with {z_step_mm}mm step...")
    if args.xyonly:
        print("XY-only flag set; skipping X-Z and Y-Z heatmap generation.")

    sar_stack = []

    # Variables to hold axis info (assuming constant across Z)
    x_axis = None
    y_axis = None

    for z_mm in z_values:
        z0 = z_mm * 1e-3
        print(f"Processing Z = {z_mm} mm...")
        
        # Range focusing
        tI = 4.5225e-10
        k_idx = int(round(K * Ts * (2 * z0 / c + tI) * n_fft_time))
        # Safety check: ensure we are in the valid FFT index range
        if k_idx < 0 or k_idx >= raw_data_fft.shape[0]:
            print(f"Computed range-FFT index {k_idx} out of bounds (0, {raw_data_fft.shape[0]-1}); skipping this Z value")
            continue
        
        # Extract slice
        # MATLAB: sarData = squeeze(rawDataFFT(k+1,:,:));
        # Python: k_idx is 0-based.
        sar_data = raw_data_fft[k_idx, :, :]
        
        # Create Matched Filter
        # print("Creating Matched Filter...")
        matched_filter = create_matched_filter(n_fft_space, dx, n_fft_space, dy, z0*1e3)
        
        # Create SAR Image
        # print("Reconstructing SAR Image...")
        
        # Use scan dimensions for axis alignment
        scan_width_x = 280
        scan_height_y = 40
        
        # Use a larger display size to see the full reconstruction (beyond the scan area)
        display_width_x = 400
        display_height_y = 300
        
        if args.algo == 'fista':
             sar_image, x_axis, y_axis = reconstruct_sar_image_fista(sar_data, matched_filter, dx, dy, display_width_x, display_height_y, args.fista_iters, args.fista_lambda)
        elif args.algo == 'bpa':
             sar_image, x_axis, y_axis = reconstruct_sar_image_bpa(raw_data_fft, dx, dy, z_mm, scan_width_x, scan_height_y, display_width_x, display_height_y)
        else:
             sar_image, x_axis, y_axis = reconstruct_sar_image(sar_data, matched_filter, dx, dy, display_width_x, display_height_y)
        
        # Shift axes so that (0,0) corresponds to the bottom-left of the physical scan area
        if args.algo != 'bpa': # BPA already returns centered axes
            x_axis += scan_width_x / 2
            y_axis += scan_height_y / 2
        
        # Store magnitude
        # MATLAB: fliplr(sarImage)
        sar_stack.append(np.abs(np.fliplr(sar_image)))

    sar_stack = np.array(sar_stack) # Shape (N_z, Y, X)

    # Dump images if requested
    if args.sar_dump:
        print(f"Dumping SAR images to {args.sar_dump}...")
        os.makedirs(args.sar_dump, exist_ok=True)
        
        # Normalize for image saving (0-255)
        # Using global max to preserve relative intensity across Z-slices
        stack_max = np.max(sar_stack)
        if stack_max > 0:
            norm_stack = (sar_stack / stack_max * 255).astype(np.uint8)
        else:
            norm_stack = sar_stack.astype(np.uint8)

        for i, z_val in enumerate(z_values):
            out_path = os.path.join(args.sar_dump, f"sar_z{z_val}.png")
            # Save as grayscale
            plt.imsave(out_path, norm_stack[i], cmap='gray')
        
        print(f"Saved {len(z_values)} slices to {args.sar_dump}")

    if args.silent:
        return

    # Generate Heatmaps
    print("Generating Heatmaps...")

    # 1. Maximum Intensity Projection along Y axis (View X vs Z)
    # sar_stack is (Z, Y, X). Max over axis 1 (Y). Result (Z, X).
    if not args.xyonly:
        mip_xz = np.max(sar_stack, axis=1)

        plt.figure(figsize=(10, 6))
        # pcolormesh expects X, Y. Here X is x_axis, Y is z_values.
        # mip_xz shape is (Z, X).
        plt.pcolormesh(x_axis, z_values, mip_xz, cmap='jet', shading='gouraud')
        plt.xlabel('Horizontal (mm)')
        plt.ylabel('Depth Z (mm)')
        plt.title('SAR X-Z Maximum Intensity Projection')
        plt.colorbar(label='Intensity')
        plt.savefig('sar_heatmap_xz.png')
        print("Saved X-Z heatmap to sar_heatmap_xz.png")

    # 2. Maximum Intensity Projection along X axis (View Y vs Z)
    # sar_stack is (Z, Y, X). Max over axis 2 (X). Result (Z, Y).
    if not args.xyonly:
        mip_yz = np.max(sar_stack, axis=2)

        plt.figure(figsize=(10, 6))
        # pcolormesh expects X, Y. Here X is y_axis, Y is z_values.
        plt.pcolormesh(y_axis, z_values, mip_yz, cmap='jet', shading='gouraud')
        plt.xlabel('Vertical (mm)')
        plt.ylabel('Depth Z (mm)')
        plt.title('SAR Y-Z Maximum Intensity Projection')
        plt.colorbar(label='Intensity')
        plt.savefig('sar_heatmap_yz.png')
        print("Saved Y-Z heatmap to sar_heatmap_yz.png")

    # 3. Best Focus Image (Max over Z)
    # Max over axis 0 (Z). Result (Y, X).
    mip_xy = np.max(sar_stack, axis=0)

    plt.figure(figsize=(10, 6))
    plt.pcolormesh(x_axis, y_axis, mip_xy, cmap='jet', shading='gouraud')
    plt.xlabel('Horizontal (mm)')
    plt.ylabel('Vertical (mm)')
    plt.title('SAR X-Y Maximum Intensity Projection (All Z)')
    plt.axis('equal')
    plt.colorbar(label='Intensity')
    plt.savefig('sar_heatmap_xy_max.png')
    print("Saved X-Y max projection to sar_heatmap_xy_max.png")

    # 3.5 3D Scatter Plot (Volumetric Proxy)
    if args.scatter3d:
        print("Generating 3D Scatter Plot with Plotly...")
        try:
            import plotly.graph_objects as go
        except ImportError:
            print("Error: plotly not found. Please install it with 'pip install plotly' or 'uv pip install plotly'")
        else:
            # Create meshgrid for 3D plotting
            # sar_stack is (Z, Y, X)
            # We need coordinates corresponding to indices
            # Z: z_values
            # Y: y_axis
            # X: x_axis
            
            # meshgrid indexing='ij' produces grids matching the array indexing (Z, Y, X)
            Z_grid, Y_grid, X_grid = np.meshgrid(z_values, y_axis, x_axis, indexing='ij')
            
            # Flatten arrays for scatter plot
            xs = X_grid.flatten()
            ys = Y_grid.flatten()
            zs = Z_grid.flatten()
            vals = sar_stack.flatten()
            
            # Initial Thresholding
            initial_percentile = args.scatter3d_intensity
            
            # Base data (using the lowest threshold to ensure all points are available if we were using transforms, 
            # but here we are using restyle with explicit arrays, so we just need the source data)
            # Actually, for the initial plot, we use the first percentile.
            
            # We will create a slider that goes from initial_percentile up to 99.9%
            # To do this efficiently in a standalone HTML, we can pre-generate the subsets for each slider step.
            # However, storing many copies of the data can be heavy.
            
            # Dynamic step count based on data size to prevent browser crashes
            threshold_0_val = np.percentile(vals, initial_percentile)
            mask_0 = vals > threshold_0_val
            num_points = np.sum(mask_0)
            
            print(f"Filtering data: keeping points > {initial_percentile} percentile ({num_points} points)")
            
            if num_points > 200000:
                print("WARNING: High point count (>200k). Reducing slider steps to 5 to prevent browser crash.")
                num_steps = 5
            elif num_points > 50000:
                print("Notice: Moderate point count (>50k). Reducing slider steps to 10.")
                num_steps = 10
            else:
                num_steps = 20
            
            percentiles = np.linspace(initial_percentile, 99.9, num_steps)
            
            # Recalculate threshold_0 based on the first step of the linspace (which is initial_percentile)
            threshold_0 = np.percentile(vals, percentiles[0])
            mask_0 = vals > threshold_0

            # Create Plotly Figure
            fig = go.Figure()

            # Add the initial trace
            fig.add_trace(go.Scatter3d(
                x=xs[mask_0],
                y=ys[mask_0],
                z=zs[mask_0],
                mode='markers',
                marker=dict(
                    size=3,
                    color=vals[mask_0],
                    colorscale='Jet',
                    opacity=0.3,
                    colorbar=dict(title='Intensity')
                ),
                name='SAR Data'
            ))

            # Create Slider Steps
            steps = []
            print("Generating slider steps...")
            for p in percentiles:
                thresh = np.percentile(vals, p)
                mask = vals > thresh
                
                # We update x, y, z, and marker.color
                step = dict(
                    method="restyle",
                    args=[{
                        "x": [xs[mask]],
                        "y": [ys[mask]],
                        "z": [zs[mask]],
                        "marker.color": [vals[mask]]
                    }],
                    label=f"{p:.1f}%"
                )
                steps.append(step)

            sliders = [dict(
                active=0,
                currentvalue={"prefix": "Intensity Threshold: "},
                pad={"t": 50},
                steps=steps
            )]

            fig.update_layout(
                title='3D SAR Reconstruction',
                scene=dict(
                    xaxis_title='Horizontal (mm)',
                    yaxis_title='Vertical (mm)',
                    zaxis_title='Depth Z (mm)',
                    aspectmode='data' # Preserve aspect ratio
                ),
                margin=dict(l=0, r=0, b=0, t=40),
                sliders=sliders
            )

            output_file = get_unique_filename('sar_3d_scatter.html')
            fig.write_html(output_file)
            print(f"Saved interactive 3D plot to {output_file}")
            
            # Attempt to open in browser
            try:
                import webbrowser
                webbrowser.open(output_file)
            except Exception:
                pass

    # 4. Interactive Slider Plot (or single Z display)
    if args.plotly and not args.mat_plot_lib:
        print("Generating Interactive Plotly Slice Viewer...")
        try:
            import plotly.graph_objects as go
        except ImportError:
            print("Error: plotly not found. Please install it with 'pip install plotly' or 'uv pip install plotly'")
            return

        # Create frames for each Z slice
        frames = []
        steps = []
        
        # Determine global min/max for consistent color scaling
        cmin = np.min(sar_stack)
        cmax = np.max(sar_stack)

        # Initial data (middle slice)
        initial_idx = len(z_values) // 2
        
        # Create the base figure with the initial slice
        fig = go.Figure(
            data=[go.Heatmap(
                z=sar_stack[initial_idx],
                x=x_axis,
                y=y_axis,
                colorscale='Jet',
                zmin=cmin,
                zmax=cmax,
                colorbar=dict(title='Intensity')
            )],
            layout=go.Layout(
                title=f"SAR Reconstruction (Z={z_values[initial_idx]}mm)",
                xaxis=dict(title="Horizontal (mm)", scaleanchor="y", scaleratio=1),
                yaxis=dict(title="Vertical (mm)"),
                updatemenus=[dict(
                    type="buttons",
                    buttons=[dict(label="Play",
                                  method="animate",
                                  args=[None, dict(frame=dict(duration=100, redraw=True), fromcurrent=True)])]
                )]
            )
        )

        # Create frames
        print("Building frames for HTML animation...")
        for i, z_val in enumerate(z_values):
            frame = go.Frame(
                data=[go.Heatmap(z=sar_stack[i])],
                name=str(z_val),
                layout=go.Layout(title=f"SAR Reconstruction (Z={z_val}mm)")
            )
            frames.append(frame)
            
            # Create slider step
            step = dict(
                method="animate",
                args=[[str(z_val)],
                      dict(mode="immediate",
                           frame=dict(duration=0, redraw=True),
                           transition=dict(duration=0))],
                label=f"{z_val}"
            )
            steps.append(step)

        fig.frames = frames
        
        fig.update_layout(
            sliders=[dict(
                active=initial_idx,
                currentvalue={"prefix": "Depth Z: ", "suffix": " mm"},
                pad={"t": 50},
                steps=steps
            )]
        )

        output_file = get_unique_filename('sar_interactive_slices.html')
        fig.write_html(output_file)
        print(f"Saved interactive slice viewer to {output_file}")
        
        try:
            import webbrowser
            webbrowser.open(output_file)
        except Exception:
            pass

    else:
        print("Opening interactive inspector (Matplotlib)...")

        single_z_mode = (len(z_values) == 1)

        fig_int, ax_int = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(bottom=0.25)

        # If a single Z was selected, just display that single image without a slider
        if single_z_mode:
            idx = 0
            mesh = ax_int.pcolormesh(x_axis, y_axis, sar_stack[idx], cmap='jet', shading='gouraud')
            ax_int.set_xlabel('Horizontal (mm)')
            ax_int.set_ylabel('Vertical (mm)')
            title_obj = ax_int.set_title(f'SAR Image at Z = {z_values[idx]} mm')
            ax_int.axis('equal')
            fig_int.colorbar(mesh, ax=ax_int, label='Intensity')
            plt.show()
        else:
            initial_idx = len(z_values) // 2
            # Note: pcolormesh with gouraud shading
            mesh = ax_int.pcolormesh(x_axis, y_axis, sar_stack[initial_idx], cmap='jet', shading='gouraud')
            ax_int.set_xlabel('Horizontal (mm)')
            ax_int.set_ylabel('Vertical (mm)')
            title_obj = ax_int.set_title(f'SAR Image at Z = {z_values[initial_idx]} mm')
            ax_int.axis('equal')
            fig_int.colorbar(mesh, ax=ax_int, label='Intensity')

            ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
            slider = Slider(
                ax=ax_slider,
                label='Depth Z (mm)',
                valmin=z_values[0],
                valmax=z_values[-1],
                valinit=z_values[initial_idx],
                valstep=z_step_mm
            )

            def update(val):
                # Find nearest index in z_values to the slider's current value
                z_selected = slider.val
                idx = int(np.argmin(np.abs(z_values - z_selected)))
                # Update data
                mesh.set_array(sar_stack[idx].ravel())
                title_obj.set_text(f'SAR Image at Z = {z_values[idx]} mm')
                fig_int.canvas.draw_idle()

            slider.on_changed(update)
            plt.show()

if __name__ == "__main__":
    main()
