import os

from utils.config import load_config


class GeneralConfig:
    def __init__(self, config_file: str) -> None:
        config = load_config(config_file)
        args = config.get("general", {})
        self.input_file = args["input_file"]
        self.output_folder = args["output_folder"]
        self.k = args["k"]

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)


class UCTSConfig:
    def __init__(self, config_file: str) -> None:
        config = load_config(config_file)
        args = config.get("ucts", {})
        self.max_iter = args["max_iter"]
        self.max_iter_per_node = args["max_iter_per_node"]
        self.grid_density_unit = args["grid_density_unit"]
        self.num_neighbors = args["num_neighbors"]
        self.clamp_tolerance = args["clamp_tolerance"]
        self.max_edge_len = args["max_edge_len"]
