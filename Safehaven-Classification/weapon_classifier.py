import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import argparse
import glob

# ==========================================
# Phase 1: Reflectivity Added Image Generation
# ==========================================

def generate_reflectivity_image(input_path, output_path=None, target_size=(100, 100)):
    """
    Generates a 'reflectivity-added' image from a source image as described in the paper.
    
    Process:
    1. Load image and convert to grayscale.
    2. Normalize pixel intensity: rho = I(x,y) / I_max.
    3. Resize to target grid size (100x100).
    4. Map to reflectivity ranges (Background 0-0.3, Object 0.8-1.0).
       Note: The paper uses simple normalization (Eq 1). The ranges 0-0.3 and 0.8-1.0 
       are likely properties of the objects in the SAR simulation. 
       Here we perform a contrast stretch to approximate this separation 
       if the image has good contrast.
    """
    # 1. Load Image
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError(f"Could not load image: {input_path}")
        
    # Convert to grayscale
    # Handle various input channels (BGR, BGRA, or Grayscale)
    if len(img.shape) == 3:
        if img.shape[2] == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif img.shape[2] == 4:
            gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        else:
            gray = img[:,:,0] # Fallback
    else:
        gray = img
    
    # 2. Normalize (Eq 1: rho = I / I_max)
    # We use float32 for precision
    img_float = gray.astype(np.float32)
    i_max = np.max(img_float)
    if i_max == 0:
        i_max = 1 # Avoid divide by zero for black images
        
    rho = img_float / i_max
    
    # 3. Resize (Eq 2)
    # The paper mentions resizing to 100x100
    rho_resized = cv2.resize(rho, target_size, interpolation=cv2.INTER_LINEAR)
    
    # Optional: Enforce the reflectivity ranges mentioned (0-0.3 background, 0.8-1.0 object)
    # This is a heuristic step to match the paper's description of the data properties.
    # We assume the object is brighter than the background.
    # We can use a sigmoid-like or piecewise linear mapping.
    # Simple approach: Threshold and stretch.
    # However, strictly following Eq 1 and 2, we just return the normalized resized image.
    # We will stick to the normalized image but ensure it's saved as 0-255 for visualization.
    
    # To visualize/save as image, scale back to 0-255
    output_img = (rho_resized * 255).astype(np.uint8)
    
    if output_path:
        cv2.imwrite(output_path, output_img)
        print(f"Saved reflectivity added image to: {output_path}")
        
    return rho_resized

# ==========================================
# Phase 3: CNN Classifier Architecture
# ==========================================

class WeaponCNN(nn.Module):
    """
    CNN Architecture as described in the paper:
    - Input: 100x100 image
    - Conv Layer 1: 32 filters, 3x3, ReLU
    - Max Pooling
    - Conv Layer 2: 64 filters, 3x3, ReLU
    - Max Pooling
    - Conv Layer 3: 64 filters, 3x3, ReLU
    - Flatten
    - Dense Layer 1: 64 neurons, ReLU
    - Output Layer: 5 classes (Softmax implied by CrossEntropyLoss in training)
    """
    def __init__(self, num_classes=5):
        super(WeaponCNN, self).__init__()
        
        # Input shape: (Batch, 1, 100, 100) - Assuming grayscale input
        
        # Layer 1
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        
        # Layer 2
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        
        # Layer 3
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=64, kernel_size=3, padding=1)
        
        # Fully Connected Layers
        # Calculation for flattened size:
        # Input: 100x100
        # After Conv1 (padding=1): 100x100
        # After Pool1: 50x50
        # After Conv2 (padding=1): 50x50
        # After Pool2: 25x25
        # After Conv3 (padding=1): 25x25
        # Note: The paper mentions pooling after Conv1 and Conv2. 
        # It does NOT explicitly mention pooling after Conv3, but usually it's there or not.
        # "Another max pooling layer follows... The architecture also includes a third layer of convolution... The convolutional and pooling layers are followed by the flattening"
        # This implies: Conv1 -> Pool -> Conv2 -> Pool -> Conv3 -> Flatten
        
        self.flatten_size = 64 * 25 * 25
        
        self.fc1 = nn.Linear(self.flatten_size, 64)
        self.fc2 = nn.Linear(64, num_classes)
        
    def forward(self, x):
        # Layer 1
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        
        # Layer 2
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        
        # Layer 3
        x = F.relu(self.conv3(x))
        
        # Flatten
        x = x.view(-1, self.flatten_size)
        
        # Dense 1
        x = F.relu(self.fc1(x))
        
        # Output
        x = self.fc2(x)
        # Note: Softmax is usually applied in the Loss function (CrossEntropyLoss) in PyTorch
        return x

# ==========================================
# Helper for Inference
# ==========================================

def predict_weapon(model, image_path, classes=['Grenade', 'Knife', 'Gun', 'IronRod', 'Wrench']):
    """
    Predicts the class of a weapon from an image path using the trained model.
    """
    # Preprocess
    # 1. Generate reflectivity image (resize to 100x100, normalize)
    rho_img = generate_reflectivity_image(image_path, target_size=(100, 100))
    
    # 2. Convert to Tensor
    # Add channel dim (1) and batch dim (1) -> (1, 1, 100, 100)
    img_tensor = torch.from_numpy(rho_img).float().unsqueeze(0).unsqueeze(0)
    
    # 3. Predict
    model.eval()
    with torch.no_grad():
        outputs = model(img_tensor)
        probabilities = F.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
        
    class_idx = predicted.item()
    class_name = classes[class_idx]
    conf_score = confidence.item()
    
    return class_name, conf_score

# ==========================================
# Phase 4: Training Logic
# ==========================================

class SARDataset(Dataset):
    def __init__(self, root_dir):
        """
        Args:
            root_dir (string): Directory with all the images.
                               Structure: root_dir/class_name/image_files
        """
        self.root_dir = root_dir
        # Find classes based on subdirectories
        self.classes = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))])
        if not self.classes:
            raise ValueError(f"No class subdirectories found in {root_dir}")
            
        self.class_to_idx = {cls_name: i for i, cls_name in enumerate(self.classes)}
        self.images = []
        
        print(f"Found classes: {self.classes}")
        
        for cls_name in self.classes:
            cls_dir = os.path.join(root_dir, cls_name)
            count = 0
            # Use os.walk to recursively find images in subdirectories
            for root, dirs, files in os.walk(cls_dir):
                for img_name in files:
                    if img_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        self.images.append((os.path.join(root, img_name), self.class_to_idx[cls_name]))
                        count += 1
            print(f"  Class '{cls_name}': {count} images")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path, label = self.images[idx]
        
        # Use the preprocessing function
        # generate_reflectivity_image returns a numpy array (100, 100) float32 0-1
        try:
            processed_img = generate_reflectivity_image(img_path, target_size=(100, 100))
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            # Return a zero tensor in case of error to avoid crashing
            return torch.zeros(1, 100, 100), label
        
        # Convert to tensor
        # Add channel dim -> (1, 100, 100)
        img_tensor = torch.from_numpy(processed_img).float().unsqueeze(0)
        
        return img_tensor, label

def train_model(data_dir, num_epochs=20, batch_size=16, learning_rate=0.001, save_path='weapon_classifier.pth'):
    print(f"Starting training with data from {data_dir}")
    
    # 1. Setup Dataset and DataLoader
    dataset = SARDataset(data_dir)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    num_classes = len(dataset.classes)
    print(f"Training for {num_classes} classes...")
    
    # 2. Initialize Model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model = WeaponCNN(num_classes=num_classes).to(device)
    
    # 3. Loss and Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # 4. Training Loop
    for epoch in range(num_epochs):
        running_loss = 0.0
        correct = 0
        total = 0
        
        for i, (inputs, labels) in enumerate(dataloader):
            inputs, labels = inputs.to(device), labels.to(device)
            
            # Zero the parameter gradients
            optimizer.zero_grad()
            
            # Forward + Backward + Optimize
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
            
        epoch_loss = running_loss / len(dataloader)
        epoch_acc = 100 * correct / total
        print(f"Epoch [{epoch+1}/{num_epochs}] Loss: {epoch_loss:.4f} Accuracy: {epoch_acc:.2f}%")
        
    # 5. Save Model
    torch.save(model.state_dict(), save_path)
    print(f"Finished Training. Model saved to {save_path}")
    
    # Save class mapping
    with open(save_path + ".classes", "w") as f:
        f.write("\n".join(dataset.classes))
    print(f"Class mapping saved to {save_path}.classes")

# ==========================================
# Main Execution Block
# ==========================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Weapon Classifier for SAR Images')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Train Command
    train_parser = subparsers.add_parser('train', help='Train the model')
    train_parser.add_argument('--data_dir', type=str, required=True, help='Path to dataset directory (must contain class subfolders)')
    train_parser.add_argument('--epochs', type=int, default=20, help='Number of epochs')
    train_parser.add_argument('--batch_size', type=int, default=16, help='Batch size')
    train_parser.add_argument('--lr', type=float, default=0.001, help='Learning rate')
    train_parser.add_argument('--save_path', type=str, default='weapon_classifier.pth', help='Path to save trained model')
    
    # Predict Command
    predict_parser = subparsers.add_parser('predict', help='Predict class for an image')
    predict_parser.add_argument('--image', type=str, required=True, help='Path to image file')
    predict_parser.add_argument('--model_path', type=str, default='weapon_classifier.pth', help='Path to trained model')
    
    # Preprocess Command
    process_parser = subparsers.add_parser('preprocess', help='Generate reflectivity image only')
    process_parser.add_argument('--input', type=str, required=True, help='Input image')
    process_parser.add_argument('--output', type=str, required=True, help='Output image')

    args = parser.parse_args()
    
    if args.command == 'train':
        train_model(args.data_dir, num_epochs=args.epochs, batch_size=args.batch_size, learning_rate=args.lr, save_path=args.save_path)
        
    elif args.command == 'predict':
        if not os.path.exists(args.model_path):
            print(f"Error: Model file {args.model_path} not found. Train the model first.")
        else:
            # Load classes
            classes_file = args.model_path + ".classes"
            if os.path.exists(classes_file):
                with open(classes_file, 'r') as f:
                    classes = [line.strip() for line in f.readlines()]
            else:
                print("Warning: Class mapping file not found. Using default classes.")
                classes = ['Grenade', 'Knife', 'Gun', 'IronRod', 'Wrench']
                
            model = WeaponCNN(num_classes=len(classes))
            model.load_state_dict(torch.load(args.model_path))
            
            label, conf = predict_weapon(model, args.image, classes=classes)
            print(f"Prediction: {label} (Confidence: {conf:.2f})")
            
    elif args.command == 'preprocess':
        generate_reflectivity_image(args.input, args.output)
        
    else:
        parser.print_help()
