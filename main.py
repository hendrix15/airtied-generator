from search import ucts


def main() -> None:
    ucts.execute(
        run_id="test", config_file="config/search.yaml", input_file="input/example.json"
    )


if __name__ == "__main__":
    main()
