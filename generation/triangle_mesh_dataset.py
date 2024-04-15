from torch.utils.data import Dataset
from torch.nn import functional as F
import torch
import os
from util.obj_reader import vertices_and_edges_from_obj


class TriangleMeshDataset(Dataset):
    def __init__(
        self,
        dataset_filepath: str,
        limit: int = 100000,
    ) -> None:
        super().__init__()
        if not os.path.exists(dataset_filepath):
            raise Exception(f"{dataset_filepath} does not exist.")

        self.limit = limit
        self.dataset_filepath = dataset_filepath
        self.samples = []

        for root, dirs, files in os.walk(dataset_filepath):
            for file in files:
                if file.endswith(".obj"):
                    vertices, edges = vertices_and_edges_from_obj(
                        os.path.join(root, file)
                    )

                    edge_tensor = torch.zeros([2, 3])
                    mesh_tensor = torch.zeros([len(edges), 2, 3])
                    for i, edge in enumerate(edges):
                        v1_idx, v2_idx = edge
                        v1_idx -= 1
                        v2_idx -= 1
                        v1_tensor = torch.Tensor(vertices[v1_idx])
                        v2_tensor = torch.Tensor(vertices[v2_idx])
                        edge_tensor[0] = v1_tensor
                        edge_tensor[1] = v2_tensor
                        mesh_tensor[i] = edge_tensor
                    self.samples.append(mesh_tensor)

    def __len__(self):
        return min(len(self.samples), self.limit)

    def __getitem__(self, index):
        return self.pad(self.samples[index])

    def pad(self, vector: torch.Tensor) -> torch.Tensor:
        # pad the vector with zero padding to vector size 64
        VECTOR_SIZE = 128
        n_edges = vector.size(0)
        padded = F.pad(
            vector,
            (
                0,
                0,
                0,
                0,
                0,
                VECTOR_SIZE - n_edges,
            ),
        )
        return padded
