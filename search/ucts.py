from search.config import TrussEnvironmentConfig, UCTSConfig
from search.state import State
from search.truss_search_tree import TreeSearchNode, TrussSearchTree
from search.utils import generate_FEA_truss, load_config, read_json, visualize


def execute(run_id: str, config_file: str, input_file: str) -> None:
    config = load_config(config_file)
    ucts_config = UCTSConfig(run_id, config)
    truss_env_config = TrussEnvironmentConfig(config)

    nodes = read_json(input_file)

    state = State(config=ucts_config, nodes=nodes, edges=[])

    root = TreeSearchNode(state=state, config=truss_env_config, parent=None)
    mcts = TrussSearchTree(root=root, config=truss_env_config)
    best_node = mcts.best_action(ucts_config.max_iter)

    result = {}
    result["nodes"] = [node for node in best_node.state.nodes]
    result["edges"] = [edge for edge in best_node.state.edges]
    print(result)

    truss = generate_FEA_truss(nodes=result["nodes"], edges=result["edges"])
    try:
        truss.analyze(check_statics=True)
        for members in truss.Members.values():
            print(
                f"Member {members.name} calculated axial force: {members.max_axial()}"
            )
        visualize(nodes=result["nodes"], edges=result["edges"])
    except Exception:
        raise Exception("Truss is not stable")
