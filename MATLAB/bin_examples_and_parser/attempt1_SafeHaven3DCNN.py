import cmath

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

# ======================== DATA LOADING ========================


def readDCA1000(
    filename: str = "first.bin",
    numberOfWindows: int = 4,
    numADCBits: int = 16,
    isReal: bool = True,
    trim_to_windows: bool = False,
) -> np.ndarray:
    """Extract ADC data from DCA1000 binary file"""
    adcData = np.fromfile(filename, dtype="int16")

    if numADCBits != 16:
        l_max = 2 ** (numADCBits - 1) - 1
        adcData[adcData > l_max] = adcData[adcData > l_max] - 2**numADCBits

    if trim_to_windows:
        new_len = len(adcData) - len(adcData) % numberOfWindows
        adcData = adcData[:new_len]

    if isReal:
        adcData = adcData.reshape(numberOfWindows, -1)
    else:
        adcData = adcData.reshape(numberOfWindows * 2, -1)
        adcData = adcData[[0, 1, 2, 3], :] + 1j * adcData[[4, 5, 6, 7], :]

    return adcData


def process_radar_cube(
    adc_data, num_range_bins=256, num_doppler_bins=256, num_angle_bins=64
):
    """
    Convert raw ADC to Range-Doppler-Angle cube via FFT processing

    Args:
        adc_data: Complex ADC samples [num_rx, num_samples]
        num_range_bins: Range FFT size
        num_doppler_bins: Doppler FFT size
        num_angle_bins: Angle FFT size

    Returns:
        radar_cube: 3D numpy array [Range, Doppler, Angle]
    """
    num_rx = adc_data.shape[0]

    # 1. Range FFT (across fast-time samples)
    range_fft = np.fft.fft(adc_data, n=num_range_bins, axis=1)

    # 2. Doppler FFT (across chirps - reshape if needed based on your config)
    # Assuming adc_data columns can be reshaped to [num_chirps, samples_per_chirp]
    # Adjust this based on your actual chirp configuration
    doppler_fft = np.fft.fft(range_fft, n=num_doppler_bins, axis=1)
    doppler_fft = np.fft.fftshift(doppler_fft, axes=1)

    # 3. Angle FFT (across RX antennas for AoA estimation)
    angle_fft = np.fft.fft(doppler_fft, n=num_angle_bins, axis=0)
    angle_fft = np.fft.fftshift(angle_fft, axes=0)

    # Take magnitude (power spectrum)
    radar_cube = np.abs(angle_fft) ** 2

    # Reshape to [Range, Doppler, Angle] if needed
    # This depends on your exact FFT output shape
    radar_cube = (
        np.transpose(radar_cube, (1, 0, 2)) if radar_cube.ndim == 3 else radar_cube
    )

    return radar_cube


# ======================== DATASET ========================


class WeaponRadarDataset(Dataset):
    """Dataset for weapon detection from radar cubes [web:24][web:28]"""

    def __init__(
        self,
        bin_files,
        labels,
        cube_size=(64, 64, 32),
        num_range_bins=256,
        num_doppler_bins=256,
        num_angle_bins=64,
    ):
        """
        Args:
            bin_files: List of paths to .bin files
            labels: List of labels (0=no weapon, 1=weapon)
            cube_size: Target size for radar cube (R, D, A)
        """
        self.bin_files = bin_files
        self.labels = labels
        self.cube_size = cube_size
        self.num_range_bins = num_range_bins
        self.num_doppler_bins = num_doppler_bins
        self.num_angle_bins = num_angle_bins

    def __len__(self):
        return len(self.bin_files)

    def __getitem__(self, idx):
        # Load and process radar data
        adc_data = readDCA1000(self.bin_files[idx], isReal=False)
        radar_cube = process_radar_cube(
            adc_data, self.num_range_bins, self.num_doppler_bins, self.num_angle_bins
        )

        # Normalize
        radar_cube = (radar_cube - np.mean(radar_cube)) / (np.std(radar_cube) + 1e-8)

        # Resize to target cube size via interpolation
        radar_cube = self._resize_cube(radar_cube, self.cube_size)

        # Convert to tensor [C, D, H, W] format where C=1 (single channel)
        radar_cube = torch.from_numpy(radar_cube).float().unsqueeze(0)
        label = torch.tensor(self.labels[idx], dtype=torch.long)

        return radar_cube, label

    def _resize_cube(self, cube, target_size):
        """Resize 3D cube using scipy interpolation"""
        from scipy.ndimage import zoom

        zoom_factors = [t / s for t, s in zip(target_size, cube.shape)]
        return zoom(cube, zoom_factors, order=1)


# ======================== 3D CNN ARCHITECTURE ========================


class Weapon3DCNN(nn.Module):
    """
    3D CNN for weapon detection from radar cubes [web:18][web:28]
    Processes full Range-Doppler-Angle cube for orientation-invariant detection
    """

    def __init__(self, num_classes=2, input_channels=1):
        super(Weapon3DCNN, self).__init__()

        # 3D Convolutional blocks with batch norm [web:18]
        self.conv1 = nn.Sequential(
            nn.Conv3d(input_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm3d(32),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2, stride=2),
        )

        self.conv2 = nn.Sequential(
            nn.Conv3d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm3d(64),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2, stride=2),
        )

        self.conv3 = nn.Sequential(
            nn.Conv3d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm3d(128),
            nn.ReLU(),
            nn.MaxPool3d(kernel_size=2, stride=2),
        )

        self.conv4 = nn.Sequential(
            nn.Conv3d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm3d(256),
            nn.ReLU(),
            nn.AdaptiveAvgPool3d(
                (2, 2, 2)
            ),  # Adaptive pooling for flexible input sizes
        )

        # Fully connected layers
        self.fc1 = nn.Linear(256 * 2 * 2 * 2, 512)
        self.dropout = nn.Dropout(0.5)
        self.fc2 = nn.Linear(512, 128)
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x):
        # 3D convolutions preserve spatial relationships [web:18]
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.conv3(x)
        x = self.conv4(x)

        # Flatten for FC layers
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.fc3(x)

        return x


# ======================== TRAINING FUNCTION ========================


def train_weapon_detector(
    model, train_loader, val_loader, num_epochs=50, lr=2e-4, device="cuda"
):
    """
    Train 3D CNN weapon classifier [web:30]

    Args:
        model: Weapon3DCNN model
        train_loader: DataLoader for training
        val_loader: DataLoader for validation
        num_epochs: Number of training epochs
        lr: Learning rate
        device: 'cuda' or 'cpu'
    """
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=5
    )

    best_val_acc = 0.0

    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)

            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = torch.max(output.data, 1)
            train_total += target.size(0)
            train_correct += (predicted == target).sum().item()

        train_acc = 100 * train_correct / train_total
        avg_train_loss = train_loss / len(train_loader)

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                loss = criterion(output, target)

                val_loss += loss.item()
                _, predicted = torch.max(output.data, 1)
                val_total += target.size(0)
                val_correct += (predicted == target).sum().item()

        val_acc = 100 * val_correct / val_total
        avg_val_loss = val_loss / len(val_loader)

        # Learning rate scheduling
        scheduler.step(avg_val_loss)

        print(
            f"Epoch [{epoch + 1}/{num_epochs}] "
            f"Train Loss: {avg_train_loss:.4f} | Train Acc: {train_acc:.2f}% | "
            f"Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc:.2f}%"
        )

        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "best_weapon_detector.pth")
            print(f"✓ Saved best model (Val Acc: {val_acc:.2f}%)")

    print(f"\nTraining complete! Best validation accuracy: {best_val_acc:.2f}%")
    return model


# ======================== INFERENCE ========================


def predict_weapon(model, bin_file, device="cuda", threshold=0.5):
    """
    Predict whether weapon is present in radar scan

    Returns:
        prediction: 0 (no weapon) or 1 (weapon)
        confidence: Probability score for weapon class
    """
    model.eval()

    # Load and process single file
    adc_data = readDCA1000(bin_file, isReal=False)
    radar_cube = process_radar_cube(adc_data)
    radar_cube = (radar_cube - np.mean(radar_cube)) / (np.std(radar_cube) + 1e-8)

    # Convert to tensor
    radar_tensor = torch.from_numpy(radar_cube).float().unsqueeze(0).unsqueeze(0)
    radar_tensor = radar_tensor.to(device)

    with torch.no_grad():
        output = model(radar_tensor)
        probs = F.softmax(output, dim=1)
        confidence = probs[0, 1].item()  # Probability of weapon class
        prediction = 1 if confidence >= threshold else 0

    return prediction, confidence


# ======================== USAGE EXAMPLE ========================

if __name__ == "__main__":
    # Example: Prepare your dataset
    train_files = ["weapon_scan1.bin", "no_weapon1.bin", "weapon_scan2.bin", ...]
    train_labels = [1, 0, 1, ...]  # 1=weapon, 0=no weapon

    val_files = ["weapon_val1.bin", "no_weapon_val1.bin", ...]
    val_labels = [1, 0, ...]

    # Create datasets and loaders [web:30]
    train_dataset = WeaponRadarDataset(
        train_files, train_labels, cube_size=(64, 64, 32)
    )
    val_dataset = WeaponRadarDataset(val_files, val_labels, cube_size=(64, 64, 32))

    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False, num_workers=4)

    # Initialize model [web:18]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = Weapon3DCNN(num_classes=2, input_channels=1)

    # Train the model
    trained_model = train_weapon_detector(
        model, train_loader, val_loader, num_epochs=50, lr=2e-4, device=device
    )

    # Inference on new scan
    prediction, confidence = predict_weapon(
        trained_model, "test_scan.bin", device=device
    )
    print(f"Prediction: {'WEAPON DETECTED' if prediction == 1 else 'NO WEAPON'}")
    print(f"Confidence: {confidence:.2%}")
