from argparse import ArgumentParser

from utils.parser import convert_obj_to_json, read_json
from utils.plot import visualize


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default="dino.obj")
    parser.add_argument("--output", type=str, default="dino.json")
    args = parser.parse_args()

    convert_obj_to_json(args.input, args.output)

    nodes, edges = read_json(args.output)
    visualize(nodes, edges)

    # Convert back to obj for verification
    # nodes_and_edges_to_obj("dino_test.obj", nodes, edges)


if __name__ == "__main__":
    main()
