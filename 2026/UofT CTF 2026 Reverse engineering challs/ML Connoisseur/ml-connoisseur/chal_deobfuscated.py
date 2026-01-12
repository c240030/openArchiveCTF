"""
Deobfuscated version of chal.py
This script loads a PyTorch model and performs image classification.
"""
import sys
import importlib
from pathlib import Path
import numpy as np
import torch
from PIL import Image
import model as model_obf


def load_image(image_path):
    """Load and preprocess an image for the model."""
    img = Image.open(image_path).convert('RGB')
    img = img.resize((256, 256), Image.BILINEAR)
    img_array = np.array(img, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(img_array).permute(2, 0, 1).contiguous()
    return tensor.unsqueeze(0)


def main():
    """Main function to run the image classification."""
    if len(sys.argv) != 2:
        print('0')
        return
    
    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print('0')
        return
    
    model_class = None
    for item in model_obf.__dict__.values():
        if isinstance(item, type) and hasattr(item, '__entry__') and (getattr(item, '__entry__') is True):
            model_class = item
            break
    
    if model_class is None:
        print('0')
        return
    
    model = model_class()
    
    weights = torch.load(Path(__file__).parent / 'weights.pt', map_location='cpu')
    model.load_state_dict(weights)
    model.eval()
    
    input_tensor = load_image(image_path)
    
    with torch.no_grad():
        output = model(input_tensor)
    
    if int(output.item()) > 9:
        print('you got it!')
    else:
        print(int(output.item()))


if __name__ == '__main__':
    main()
