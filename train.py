from generation.triangle_mesh_dataset import TriangleMeshDataset
import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from generation.model import TowerModel


def train():
    dataset = TriangleMeshDataset("data/", limit=1000)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=True)
    model = TowerModel()
    criterion = torch.nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    for epoch in range(10):
        running_loss = 0.0
        for i, data in enumerate(dataloader):
            # create torch tensor with size 20 and value 200
            meshes = data
            optimizer.zero_grad()
            outputs = model(torch.tensor([[200]], dtype=torch.float32))

            loss = criterion(outputs.flatten(), meshes.flatten())
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            if i % 10 == 9:
                print(f"[{epoch + 1}, {i + 1}] loss: {running_loss / 10}")
                running_loss = 0.0

    print("Finished Training")


if __name__ == "__main__":
    train()
