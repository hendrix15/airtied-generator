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


class TrussEnvironmentConfig:
    def __init__(self, config: dict) -> None:
        args = config.get("truss_env", {})
        self.E = args["E"]
        self.pho = args["pho"]
        self.sigma_T = args["sigma_T"]
        self.sigma_C = args["sigma_C"]
        self.slenderness_ratio_T = args["slenderness_ratio_c"]
        self.slenderness_ratio_C = args["slenderness_ratio_t"]
        self.dislimit = args["dislimit"]
        self.max_len = 5.0
        self.min_len = 0.03
        self.use_self_weight = True
        self.use_dis_constraint = True
        self.use_stress_constraint = True
        self.use_buckle_constraint = True
        self.use_slenderness_constraint = True
        self.use_longer_constraint = True
        self.use_shorter_constraint = True
        self.use_cross_constraint = True
