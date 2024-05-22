from search.config import TrussEnvironmentConfig, UCTSConfig
from search.truss_environment import TrussEnvironment
from search.utils import load_config, read_json


def execute(run_id: str, config_file: str, input_file: str) -> None:
    config = load_config(config_file)
    ucts_config = UCTSConfig(run_id, config)
    truss_env_config = TrussEnvironmentConfig(config)
    print(ucts_config)
    print(truss_env_config)

    case = read_json(input_file)
    print(case)

    truss_env = TrussEnvironment(config=truss_env_config)
