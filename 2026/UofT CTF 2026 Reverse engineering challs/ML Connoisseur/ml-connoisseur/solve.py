import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from PIL import Image
import time
import model as model_obf

def solve_optimized_fixed():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"[{device}] Loading model...")

    model_class = None
    for item in model_obf.__dict__.values():
        if isinstance(item, type) and hasattr(item, '__entry__') and (getattr(item, '__entry__') is True):
            model_class = item
            break
    if model_class is None:
        print("Error: Model class not found.")
        return
    net = model_class()
    try:
        net.load_state_dict(torch.load('weights.pt', map_location=device))
    except:
        net.load_state_dict(torch.load('weights.pt', map_location='cpu'))
    
    net.to(device)
    net.eval()

    backbone = None
    reference = None
    
    for child in net.children():
        if any(isinstance(m, nn.ParameterList) for m in child.modules()):
            backbone = child
            break
            
    if backbone:
        for attr_name in dir(backbone):
            try:
                attr = getattr(backbone, attr_name)
                if callable(attr) and not attr_name.startswith('_'):
                    ret = attr()
                    if isinstance(ret, torch.Tensor) and list(ret.shape) == [1, 192, 32, 32]:
                        reference = ret.detach().to(device)
                        print(f"Reference tensor found via '{attr_name}'")
                        break
            except: pass
            
    if reference is None or backbone is None:
        print("Error: Could not setup model components.")
        return

    print("\n--- Starting Optimization ---")
    
    x = torch.rand(1, 3, 256, 256, device=device, requires_grad=True)
    
    optimizer = optim.Adam([x], lr=0.1)
    
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=50)

    start_time = time.time()
    
    print("Benchmarking 1 step...")
    optimizer.zero_grad()
    out = backbone(x)
    loss = nn.functional.mse_loss(out, reference)
    loss.backward()
    optimizer.step()
    print(f"1 Step took: {time.time() - start_time:.2f} seconds")
    
    print("Running full loop (Target Loss < 0.001)...")
    
    for i in range(1, 3001):
        loop_start = time.time()
        optimizer.zero_grad()
        
        output = backbone(x)
        loss = nn.functional.mse_loss(output, reference)
        
        loss.backward()
        optimizer.step()
        
        with torch.no_grad():
            x.data.clamp_(0, 1)
            
        scheduler.step(loss)
        
        if i % 10 == 0:
            current_loss = loss.item()
            elapsed = time.time() - start_time
            current_lr = optimizer.param_groups[0]['lr']
            print(f"Step {i}: Loss = {current_loss:.6f} | LR: {current_lr:.6f} (Time: {elapsed:.0f}s)")
            
            if i % 50 == 0:
                img_np = x.detach().cpu().squeeze(0).permute(1, 2, 0).numpy()
                img_save = Image.fromarray((img_np * 255).astype(np.uint8))
                img_save.save(f"progress.png")
            
            if current_loss < 0.001:
                print(f"\nSUCCESS! Converged at step {i}")
                break

    final_img = x.detach().cpu().squeeze(0).permute(1, 2, 0).numpy()
    final_save = Image.fromarray((final_img * 255).astype(np.uint8))
    final_save.save("flag_recovered.png")
    print("\nSaved 'flag_recovered.png'. Open it to see the flag!")

if __name__ == "__main__":
    solve_optimized_fixed()