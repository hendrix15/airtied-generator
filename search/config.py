import os


class GeneralConfig:
    def __init__(self, config: dict) -> None:
        args = config.get("general", {})
        self.input_file = args["input_file"]
        self.output_folder = args["output_folder"]
        self.image_folder = args["image_folder"]
        self.k = args["k"]

        for folder in [self.output_folder, self.image_folder]:
            if not os.path.exists(folder):
                os.makedirs(folder)


class UCTSConfig:
    def __init__(self, config: dict) -> None:
        args = config.get("ucts", {})
        self.max_nodes = args["max_nodes"]
        self.max_iter = args["max_iter"]
        self.max_iter_per_node = args["max_iter_per_node"]
        self.min_x = args["coordinate_range"][0][0]
        self.max_x = args["coordinate_range"][0][1]
        self.min_y = args["coordinate_range"][1][0]
        self.max_y = args["coordinate_range"][1][1]
        self.min_z = args["coordinate_range"][2][0]
        self.max_z = args["coordinate_range"][2][1]
        self.grid_density_unit = args["grid_density_unit"]
        self.num_neighbors = args["num_neighbors"]
        self.clamp_tolerance = args["clamp_tolerance"]
        self.max_edge_len = args["max_edge_len"]
