def load_from_file(filename):
    vertices = []
    edges = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    idx = 0
    n_verts = int(lines[idx].strip())
    idx += 1
    for i in range(n_verts):
        parts = lines[idx].strip().split()
        vertices.append([float(parts[0]), float(parts[1]), float(parts[2])])
        idx += 1
    n_edges = int(lines[idx].strip())
    idx += 1
    for i in range(n_edges):
        parts = lines[idx].strip().split()
        edges.append((int(parts[0]), int(parts[1])))
        idx += 1
    return vertices, edges

def save_to_file(filename, vertices, edges):

    with open(filename, 'w') as f:
        f.write(f"{len(vertices)}\n")
        for v in vertices:
            f.write(f"{v[0]} {v[1]} {v[2]}\n")
        f.write(f"{len(edges)}\n")
        for e in edges:
            f.write(f"{e[0]} {e[1]}\n")