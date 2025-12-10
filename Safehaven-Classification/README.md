# Weapon Classifier for SAR Images

This tool implements a CNN-based classifier for mmWave SAR images, designed to detect weapons like knives and guns. It includes functionality for training, prediction, and image preprocessing.

## Prerequisites

This project uses `uv` for dependency management and execution. Ensure you have `uv` installed.

## Usage

All commands are executed using `uv run weapon_classifier.py`.

### 1. Training

Train the model on a labeled dataset.

```bash
uv run weapon_classifier.py train --data_dir <path_to_dataset> [options]
```

**Arguments:**
- `--data_dir` (Required): Path to the dataset directory. Must contain subfolders for each class (e.g., `knife/`, `gun/`).
- `--epochs`: Number of training epochs (default: 20).
- `--batch_size`: Batch size (default: 16).
- `--lr`: Learning rate (default: 0.001).
- `--save_path`: Path to save the trained model (default: `weapon_classifier.pth`).

**Example:**
```bash
uv run weapon_classifier.py train --data_dir ./dataset --epochs 50 --save_path my_model.pth
```

### 2. Prediction

Classify a single SAR image using a trained model.

```bash
uv run weapon_classifier.py predict --image <path_to_image> [options]
```

**Arguments:**
- `--image` (Required): Path to the input image file.
- `--model_path`: Path to the trained model file (default: `weapon_classifier.pth`).

**Example:**
```bash
uv run weapon_classifier.py predict --image ./output_images/images68/sar_z350.png --model_path my_model.pth
```

### 3. Preprocessing

Generate the "reflectivity-added" version of an image (resize to 100x100, normalize) without running inference. Useful for debugging or dataset preparation.

```bash
uv run weapon_classifier.py preprocess --input <input_image> --output <output_image>
```

**Arguments:**
- `--input` (Required): Path to source image.
- `--output` (Required): Path to save processed image.

**Example:**
```bash
uv run weapon_classifier.py preprocess --input raw_scan.png --output processed_scan.png
```

## Dataset Structure

For training, organize your images into subdirectories named after their class labels:

```
dataset/
├── knife/
│   ├── scan1.png
│   ├── scan2.png
│   └── ...
├── gun/
│   ├── scan1.png
│   └── ...
└── background/
    ├── scan1.png
    └── ...
```

The script automatically detects class names from the folder names.
