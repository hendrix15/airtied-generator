from search.utils import read_json


def execute(input_file: str) -> None:
    test = read_json(input_file)
    print(test)
