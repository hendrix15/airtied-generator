import torch
from torch import nn


class CustomLoss(nn.Module):
    def __init__(self):
        super(CustomLoss, self).__init__()

    def forward(self, pred, target):
        # Calculate mean squared error
        loss = torch.mean((pred - target) ** 2)

        return loss

    def check_physics():
        # Check if the model is physically accurate with FEA simulation and if there are triangles
        pass
