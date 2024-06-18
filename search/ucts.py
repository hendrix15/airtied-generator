import shutil
from pathlib import Path

from search.config import GeneralConfig, TrussEnvironmentConfig, UCTSConfig
from search.state import State
from search.truss_search_tree import TreeSearchNode, TrussSearchTree
from search.utils import load_config
from utils.parser import read_json, write_json
from utils.plot import visualize


def execute(config_file: str) -> None:
    config = load_config(config_file)
    general_config = GeneralConfig(config)
    ucts_config = UCTSConfig(config)
    truss_env_config = TrussEnvironmentConfig(config)

    nodes, edges = read_json(general_config.input_file)

    state = State(config=ucts_config, nodes=nodes, edges=edges)
    state.init_fully_connected()

    visualize(
        dirname="bro.png",
        filename=f"1.png",
        nodes=state.nodes,
        edges=state.edges,
        save=False,
    )
    root = TreeSearchNode(state=state, config=truss_env_config, parent=None)
    mcts = TrussSearchTree(root=root, config=truss_env_config)
    best_child = mcts.best_action(ucts_config.max_iter)
    leafs = mcts.get_leafs()
    leafs.sort(key=lambda x: x.state.total_length())
    best_children = leafs[: general_config.k]

    folder_name = Path(general_config.input_file).stem
    output_path = f"{general_config.output_folder}{folder_name}/"
    image_path = f"{general_config.image_folder}{folder_name}/"
    # shutil.rmtree(output_path)
    # shutil.rmtree(image_path)

    # Store and print only best child
    write_json(nodes=nodes, edges=edges, dirname=output_path, filename="0.json")
    visualize(nodes=nodes, edges=edges)

    # Store and print best k children
    # for i, child in enumerate(best_children):
    #     nodes = [node for node in child.state.nodes]
    #     edges = [edge for edge in child.state.edges]
    #     write_json(nodes=nodes, edges=edges, dirname=output_path, filename=f"{i}.json")
    #     visualize(nodes=nodes, edges=edges, dirname=image_path, filename=f"{i}.png")
