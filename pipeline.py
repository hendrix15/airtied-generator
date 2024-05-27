from argparse import ArgumentParser

from pipeline_draft import generate_truss


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("input_file", type=str)
    # parser.add_argument('-output-file', type=str, default='generated_truss.json')

    args = parser.parse_args()
    # output_file = args.output_file
    generate_truss.run(input_file=args.input_file)


if __name__ == "__main__":
    main()
