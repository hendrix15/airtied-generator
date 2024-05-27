from search.config import TrussEnvironmentConfig, UCTSConfig
from search.truss_search_tree import TrussEnvironment
from search.utils import load_config, read_json
from search.state import State
from search.truss_search_tree import TreeSearchNode, TrussSearchTree


def execute(run_id: str, config_file: str, input_file: str) -> None:
    config = load_config(config_file)
    ucts_config = UCTSConfig(run_id, config)
    truss_env_config = TrussEnvironmentConfig(config)
    print(ucts_config)
    print(truss_env_config)

    nodes = read_json(input_file)
    print(nodes)

    truss_env = TrussEnvironment(config=truss_env_config)

    state = State(config=ucts_config, nodes=nodes, edges=[])

    root = TreeSearchNode(state=state, config=truss_env_config)
    mcts = TrussSearchTree(root)
    best_node = mcts.best_action(ucts_config.max_iter)
