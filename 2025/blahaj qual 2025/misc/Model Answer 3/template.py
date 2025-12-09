from torch import nn
from torchvision.utils import save_image
import torch
class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(32, 256),
            nn.ReLU(),
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, 8192),
            nn.LeakyReLU(0.2)
        )
        self.deconv = nn.Sequential(
            nn.Upsample(scale_factor=2, mode='nearest'),
            nn.Conv2d(in_channels=2, out_channels=3, kernel_size=3, stride=1, padding=1),
            nn.Tanh()
        )

    def forward(self, x):
        x = self.fc(x)
        x = x.view(-1, 2, 64, 64)
        x = self.deconv(x)
        return x
model2 = MyModel()
model2.load_state_dict(torch.load("model.pt", weights_only=True, map_location=torch.device('cpu')))
model2.eval()

key = torch.round(torch.rand(1, 32)) # TODO: find the real key!

tensor = model2(key)
save_image(tensor, "out.png", normalize=True)