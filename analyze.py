from argparse import ArgumentParser

from utils.fea import generate_FEA_truss, get_euler_load
from utils.parser import read_json
from utils.plot import visualize


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default="dino.json")
    args = parser.parse_args()

    nodes, edges = read_json(args.input)
    truss = generate_FEA_truss(nodes, edges)
    truss.analyze(check_statics=True)
    max_forces = {member.name: member.max_axial() for member in truss.Members.values()}

    exceeded_edges = []
    for edge in edges:
        max_force = max_forces[edge.id]
        euler_load = get_euler_load(edge.length())
        if max_force > euler_load:
            exceeded_edges.append(edge.id)
            print(
                f"Member {edge.id}: Max force of {max_force} exceeds the euler load of {euler_load}"
            )

    print(
        f"The euler load is exceeded for {len(exceeded_edges)} of {len(edges)} members"
    )

    visualize(nodes, edges, exceeded_edges)


if __name__ == "__main__":
    main()
