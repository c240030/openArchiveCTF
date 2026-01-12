"""
Analysis script for the ML Connoisseur CTF challenge.

This script helps analyze the obfuscated model and understand
how to solve the challenge (make output > 9).
"""

import torch
import model
from pathlib import Path


def load_model():
    """Load the challenge model with weights."""
    for name, cls in model.__dict__.items():
        if hasattr(cls, '__entry__') and cls.__entry__:
            m = cls()
            weights = torch.load('weights.pt', map_location='cpu')
            m.load_state_dict(weights)
            m.eval()
            return m
    return None


def analyze_model():
    """Analyze the model structure and buffers."""
    m = load_model()
    if m is None:
        print("Failed to load model")
        return
    
    print("=" * 60)
    print("MODEL STRUCTURE ANALYSIS")
    print("=" * 60)
    
    print("\n[Full Model Architecture]")
    print(m)
    
    print("\n[Registered Buffers]")
    for name, buf in m.named_buffers():
        if buf is not None:
            print(f"  {name}:")
            print(f"    Shape: {buf.shape}")
            print(f"    Dtype: {buf.dtype}")
            if buf.numel() < 20:
                print(f"    Values: {buf}")
    
    print("\n[Parameters]")
    for name, param in m.named_parameters():
        print(f"  {name}: {param.shape}")
    
    print("\n" + "=" * 60)
    print("TESTING OUTPUTS")
    print("=" * 60)
    
    with torch.no_grad():
        print("\n[Random inputs]")
        for i in range(5):
            x = torch.randn(1, 3, 256, 256)
            output = m(x)
            print(f"  Random input {i+1}: output = {output.item()}")
        
        print("\n[Special inputs]")
        x = torch.zeros(1, 3, 256, 256)
        output = m(x)
        print(f"  All zeros: output = {output.item()}")
        
        x = torch.ones(1, 3, 256, 256)
        output = m(x)
        print(f"  All ones: output = {output.item()}")
        
        x = -torch.ones(1, 3, 256, 256)
        output = m(x)
        print(f"  All -1: output = {output.item()}")
        
        x = torch.ones(1, 3, 256, 256) * 1000
        output = m(x)
        print(f"  All 1000: output = {output.item()}")
    
    print("\n" + "=" * 60)
    print("REFERENCE ANALYSIS")
    print("=" * 60)
    
    g0gO = m.G0gosqu1d
    if hasattr(g0gO, 'get_ref'):
        ref = g0gO.get_ref()
        print(f"get_ref() output shape: {ref.shape}")
        print(f"get_ref() stats: min={ref.min():.4f}, max={ref.max():.4f}, mean={ref.mean():.4f}")


def gradient_attack():
    """Try gradient-based adversarial attack to get output > 9."""
    print("\n" + "=" * 60)
    print("GRADIENT-BASED ATTACK")
    print("=" * 60)
    
    m = load_model()
    if m is None:
        return
    
    m.eval()
    
    x = torch.randn(1, 3, 256, 256, requires_grad=True)
    optimizer = torch.optim.Adam([x], lr=0.1)
    
    print("\n[Gradient Ascent Attack]")
    for i in range(100):
        optimizer.zero_grad()
        output = m(x)
        
        loss = -output
        loss.backward()
        optimizer.step()
        
        if i % 10 == 0:
            print(f"  Step {i}: output = {output.item():.4f}")
        
        if output.item() > 9:
            print(f"\n  SUCCESS at step {i}! Output = {output.item()}")
            
            img = x.detach().squeeze().permute(1, 2, 0).numpy()
            img = (img * 255).clip(0, 255).astype('uint8')
            from PIL import Image
            Image.fromarray(img).save('adversarial_image.png')
            print("  Saved adversarial_image.png")
            return x.detach()
    
    print(f"\n  Final output: {m(x).item()}")
    return x.detach()


if __name__ == "__main__":
    analyze_model()
    gradient_attack()
