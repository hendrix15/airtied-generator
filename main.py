from argparse import ArgumentParser

from search import ucts


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--config_file", type=str)
    args = parser.parse_args()

    ucts.execute(config_file=args.config_file)


if __name__ == "__main__":
    main()
