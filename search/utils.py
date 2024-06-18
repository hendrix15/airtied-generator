import yaml


def load_config(filename: str) -> dict:
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config
