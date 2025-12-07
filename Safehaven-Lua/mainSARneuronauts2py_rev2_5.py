import os
import numpy as np
import matplotlib.pyplot as plt
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
    
    # Let's construct the channels first
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
    data_dir = 'dumps'
    X = 400
    Y = 100 # Updated to match new high-res scan
    samples = 512
    
    def filename_fn(y):
        return f"scan{y}_Raw_0.bin"
        
    print("Loading data...")
    raw_data = stack(samples, X, Y, 1, data_dir, filename_fn)
    
    # Parameters
    n_fft_time = 1024
    # z0 will be iterated
    dx = 290/400
    dy = 2 # Updated to 2mm to match physical step size
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
    z_start_mm = 200
    z_end_mm = 450
    z_step_mm = 5 # Finer step for better inspection around target
    z_values = np.arange(z_start_mm, z_end_mm + z_step_mm, z_step_mm)
    
    sar_stack = []
    
    print(f"Starting Z-sweep from {z_start_mm}mm to {z_end_mm}mm with {z_step_mm}mm step...")
    
    # Variables to hold axis info (assuming constant across Z)
    x_axis = None
    y_axis = None
    
    for z_mm in z_values:
        z0 = z_mm * 1e-3
        print(f"Processing Z = {z_mm} mm...")
        
        # Range focusing
        tI = 4.5225e-10
        k_idx = int(round(K * Ts * (2 * z0 / c + tI) * n_fft_time))
        
        # Extract slice
        # MATLAB: sarData = squeeze(rawDataFFT(k+1,:,:));
        # Python: k_idx is 0-based.
        sar_data = raw_data_fft[k_idx, :, :]
        
        # Create Matched Filter
        # print("Creating Matched Filter...")
        matched_filter = create_matched_filter(n_fft_space, dx, n_fft_space, dy, z0*1e3)
        
        # Create SAR Image
        # print("Reconstructing SAR Image...")
        im_size = 200
        sar_image, x_axis, y_axis = reconstruct_sar_image(sar_data, matched_filter, dx, dy, im_size)
        
        # Store magnitude
        # MATLAB: fliplr(sarImage)
        sar_stack.append(np.abs(np.fliplr(sar_image)))

    sar_stack = np.array(sar_stack) # Shape (N_z, Y, X)
    
    # Generate Heatmaps
    print("Generating Heatmaps...")
    
    # 1. Maximum Intensity Projection along Y axis (View X vs Z)
    # sar_stack is (Z, Y, X). Max over axis 1 (Y). Result (Z, X).
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
    
    # 4. Interactive Slider Plot
    print("Opening interactive inspector...")
    from matplotlib.widgets import Slider
    
    fig_int, ax_int = plt.subplots(figsize=(10, 8))
    plt.subplots_adjust(bottom=0.25)
    
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
        # Find nearest index
        z_selected = slider.val
        idx = int(round((z_selected - z_start_mm) / z_step_mm))
        idx = max(0, min(idx, len(z_values) - 1))
        
        # Update data
        mesh.set_array(sar_stack[idx].ravel())
        title_obj.set_text(f'SAR Image at Z = {z_values[idx]} mm')
        fig_int.canvas.draw_idle()
        
    slider.on_changed(update)
    
    plt.show()

if __name__ == "__main__":
    main()