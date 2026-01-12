import torch
import torch.nn as nn
import torch.nn.functional as F


def space_to_depth(x, block_size=8):
    """
    Rearrange spatial blocks into depth (channels).
    [B, C, H, W] -> [B, C * block_size^2, H/block_size, W/block_size]
    
    Example: [1, 3, 256, 256] with block_size=8 -> [1, 192, 32, 32]
    """
    B, C, H, W = x.shape
    x = x.reshape(B, C, H // block_size, block_size, W // block_size, block_size)
    x = x.permute(0, 1, 3, 5, 2, 4)  # [B, C, bs, bs, H/bs, W/bs]
    x = x.reshape(B, C * block_size * block_size, H // block_size, W // block_size)
    return x


def depth_to_space(x, block_size=8):
    """
    Rearrange depth (channels) into spatial blocks.
    [B, C * block_size^2, H, W] -> [B, C, H * block_size, W * block_size]
    
    Uses F.pixel_shuffle internally.
    """
    return F.pixel_shuffle(x, block_size)


class MainModel(nn.Module):
    """
    Complex image processing model (originally: g0gO / G0gosqu1d)
    
    Processes input image through series of operations to produce
    a feature tensor that should match a reference tensor.
    """
    
    def __init__(self):
        super().__init__()
        
        self.conv_weights = nn.ParameterList([
            nn.Parameter(torch.randn(192, 192, 1, 1)) 
            for _ in range(32)
        ])
        
        self.register_buffer('mean', torch.zeros(3))
        self.register_buffer('std', torch.ones(3))
        
        self.register_buffer('sort_indices_x', torch.zeros(3, 65536, dtype=torch.long))
        self.register_buffer('sort_indices_y', torch.zeros(3, 65536, dtype=torch.long))
        self.register_buffer('channel_order', torch.arange(192, dtype=torch.long))
        
        self.register_buffer('flat_weights', torch.zeros(23592960))
        self.register_buffer('bias_data', torch.zeros(22528))
        
        self.register_buffer('op_sequence', torch.zeros(4, 5, dtype=torch.long))
        self.register_buffer('op_config', torch.zeros(4, 5, dtype=torch.long))
        self.register_buffer('num_steps', torch.tensor(0, dtype=torch.long))
        self.register_buffer('block_ops', torch.zeros(5000, 4, dtype=torch.long))
        self.register_buffer('layer_config', torch.zeros(32, 6, dtype=torch.long))
        self.register_buffer('layer_indices', torch.zeros(32, dtype=torch.long))
        
        self.register_buffer('lookup_table_1', torch.zeros(65536))
        self.register_buffer('lookup_table_2', torch.zeros(65536))
        self.register_buffer('lookup_table_3', torch.zeros(65536))
    
    def forward(self, x):
        """
        Process image through the network.
        
        Operations (based on op codes):
        - 163: Normalize input
        - 230: Space to depth transformation
        - 917: Apply 1x1 convolutions
        - 273: ReLU activation
        - 403: Add tensors
        - 117: Concatenate
        - 956: Reorder channels
        - 905: Chunk/split tensor
        - 859: Swap channels
        """
        pass
    
    def get_ref(self):
        """
        Get the reference tensor that the processed image should match.
        Returns: tensor of shape [1, 192, 32, 32]
        """
        pass


class ImageClassifier(nn.Module):
    """
    CNN classifier for 10-class classification (originally: g0goSqU1D / G0Gosquid)
    
    Simple CNN that classifies the input image into 10 classes.
    Used as a decoy - the real challenge is in MainModel.
    """
    
    def __init__(self):
        super().__init__()
        
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(128, 128, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        
        self.fc = nn.Linear(128, 10)
    
    def forward(self, x):
        """Classify input image into 10 classes."""
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)
        return x


class EntryModel(nn.Module):
    """
    Main entry point model (originally: G0G0sQuid)
    
    This is the model that chal.py loads and runs.
    It combines MainModel and ImageClassifier to produce the final output.
    
    The challenge is to make output > 9, which requires:
    - MSE(main_model(image), reference) < threshold (0.001)
    """
    
    __entry__ = True
    
    def __init__(self):
        super().__init__()
        
        self.main_model = MainModel()
        self.classifier = ImageClassifier()
        
        self.register_buffer('threshold', torch.tensor(0.001))
    
    def forward(self, x):
        """
        Forward pass with conditional output.
        
        Args:
            x: Input image tensor [B, 3, 256, 256]
        
        Returns:
            - 10 if MSE(main_model(x), reference) < threshold
            - argmax(classifier(x)) otherwise (0-9)
        """
        main_output = self.main_model(x)
        
        reference = self.main_model.get_ref()
        
        classifier_output = self.classifier(x)
        
        argmax_result = torch.argmax(classifier_output, dim=-1)
        
        mse = (main_output - reference).pow(2).mean(dim=(1, 2, 3))
        
        fill_10 = torch.full_like(argmax_result, 10)
        
        is_match = mse < self.threshold
        
        return torch.where(is_match, fill_10, argmax_result)
