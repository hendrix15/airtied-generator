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
