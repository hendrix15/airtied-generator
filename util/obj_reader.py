import torch

def vertices_and_edges_from_obj(filename):
    vertices = []
    edges = []
    with open(filename) as f:
        for line in f:
            if line.startswith("v "):
                vertices.append(list(map(float, line.strip().split()[1:])))
            if line.startswith("l "):
                edges.append(list(map(int, line.strip().split()[1:])))
    return vertices, edges

def write_result_to_file(result, filename):
    reshaped = torch.reshape(result, (128, 2, 3))

    vertices = []
    edges = set()
    for tensor in reshaped:
        v1 = tensor[0].tolist()
        v2 = tensor[1].tolist()
        try:
            v1_index = vertices.index(v1)
        except ValueError:
            vertices.append(v1)
            v1_index = len(vertices) - 1
        try:
            v2_index = vertices.index(v2)
        except ValueError:
            vertices.append(v2)
            v2_index = len(vertices) - 1
        edges.add((v1_index, v2_index))
    
    with open(filename, "w") as obj_file:
        vertices_output = [f"v {x} {y} {z}\n" for (x, y, z) in vertices]
        edges_output = [f"l {t+1} {u+1}\n" for (t, u) in edges]
        print(f"Writing {len(vertices_output)} vertices and {len(edges_output)} edges to file")
        obj_file.writelines(vertices_output)
        obj_file.write("\n")
        obj_file.writelines(edges_output)
        obj_file.write("\n")
        
