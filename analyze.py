from argparse import ArgumentParser

from utils.fea import ForceType, fea_opensees, fea_pynite, get_compression_tension_edges
from utils.parser import read_json
from utils.plot import visualize


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=str)
    parser.add_argument(
        "--fea", type=str, choices=["simple", "complex"], default="simple"
    )
    args = parser.parse_args()

    nodes, edges = read_json(args.input)
    if args.fea == "simple":
        max_forces = fea_pynite(nodes, edges)
    if args.fea == "complex":
        max_forces = fea_opensees(nodes, edges)
    print(max_forces)

    compression_tension_edges = get_compression_tension_edges(edges, max_forces)
    for entry in compression_tension_edges:
        print(
            f"Member {entry['id']}: Max force of {entry['max_force']}, {entry['force_type']} exceeds the euler load of {entry['euler_load']}"
        )

    print(
        f"The euler load is exceeded for {len(compression_tension_edges)} of {len(edges)} members"
    )

    compression_edges = [
        entry["id"]
        for entry in compression_tension_edges
        if entry["force_type"] == ForceType.COMPRESSION
    ]
    tension_edges = [
        entry["id"]
        for entry in compression_tension_edges
        if entry["force_type"] == ForceType.TENSION
    ]

    visualize(
        nodes=nodes,
        edges=edges,
        compression_edges=compression_edges,
        tension_edges=tension_edges,
    )


if __name__ == "__main__":
    main()
