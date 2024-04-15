import torch
from util.obj_reader import vertices_and_edges_from_obj


vertices, edges = vertices_and_edges_from_obj("data/2.obj")

edge_tensor = torch.zeros([2, 3])
final_tensor = torch.zeros([len(edges), 2, 3])
for i, edge in enumerate(edges):
    v1_idx, v2_idx = edge
    v1_idx -= 1
    v2_idx -= 1
    v1_tensor = torch.Tensor(vertices[v1_idx])
    v2_tensor = torch.Tensor(vertices[v2_idx])
    edge_tensor[0] = v1_tensor
    edge_tensor[1] = v2_tensor
    final_tensor[i] = edge_tensor


print(final_tensor.shape)
print(final_tensor)
