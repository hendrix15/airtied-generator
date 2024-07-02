from argparse import ArgumentParser

from utils.fea import ForceType, generate_FEA_truss, get_euler_load
from utils.parser import read_json
from utils.plot import visualize


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default="dino.json")
    args = parser.parse_args()

    nodes, edges = read_json(args.input)
    truss = generate_FEA_truss(nodes, edges)
    truss.analyze(check_statics=True, sparse=False)
    max_forces = {member.name: member.max_axial() for member in truss.Members.values()}
    print(max_forces)

    compression_edges = []
    tension_edges = []
    for edge in edges:
        max_force = max_forces[edge.id]
        force_type = ForceType.COMPRESSION if max_force > 0 else ForceType.TENSION
        euler_load = get_euler_load(l=edge.length(), force_type=force_type)
        if abs(max_force) > euler_load:
            if force_type == ForceType.COMPRESSION:
                compression_edges.append(edge.id)
            if force_type == ForceType.TENSION:
                tension_edges.append(edge.id)
            print(
                f"Member {edge.id}: Max force of {max_force}, {force_type} exceeds the euler load of {euler_load}"
            )

    print(
        f"The euler load is exceeded for {len(compression_edges) + len(tension_edges)} of {len(edges)} members"
    )

    visualize(
        nodes=nodes,
        edges=edges,
        compression_edges=compression_edges,
        tension_edges=tension_edges,
    )


if __name__ == "__main__":
    main()
