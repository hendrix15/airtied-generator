from argparse import ArgumentParser

from search.utils import generate_FEA_truss, read_json


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default="dino.json")
    args = parser.parse_args()

    nodes, edges = read_json(args.input)

    truss = generate_FEA_truss(nodes, edges)
    truss.analyze(check_statics=True)
    for members in truss.Members.values():
        print(f"Member {members.name} calculated axial force: {members.max_axial()}")


if __name__ == "__main__":
    main()
