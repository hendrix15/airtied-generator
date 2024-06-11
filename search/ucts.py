import shutil
from pathlib import Path

from search.config import GeneralConfig, TrussEnvironmentConfig, UCTSConfig
from search.state import State
from search.truss_search_tree import TreeSearchNode, TrussSearchTree
from search.utils import load_config, read_json, visualize, write_json


def execute(config_file: str) -> None:
    config = load_config(config_file)
    general_config = GeneralConfig(config)
    ucts_config = UCTSConfig(config)
    truss_env_config = TrussEnvironmentConfig(config)

    nodes, edges = read_json(general_config.input_file)

    state = State(config=ucts_config, nodes=nodes, edges=edges)

    root = TreeSearchNode(state=state, config=truss_env_config, parent=None)
    mcts = TrussSearchTree(root=root, config=truss_env_config)
    mcts.best_action(ucts_config.max_iter)
    best_children = root.best_children(general_config.k)

    folder_name = Path(general_config.input_file).stem
    output_path = f"{general_config.output_folder}{folder_name}/"
    image_path = f"{general_config.image_folder}{folder_name}/"
    shutil.rmtree(output_path)
    shutil.rmtree(image_path)

    for i, child in enumerate(best_children):
        nodes = [node for node in child.state.nodes]
        edges = [edge for edge in child.state.edges]
        write_json(dirname=output_path, filename=f"{i}.json", nodes=nodes, edges=edges)
        visualize(dirname=image_path, filename=f"{i}.png", nodes=nodes, edges=edges)

    # truss = generate_FEA_truss(nodes=result["nodes"], edges=result["edges"])
    # try:
    #     truss.analyze(check_statics=True)
    #     for members in truss.Members.values():
    #         print(
    #             f"Member {members.name} calculated axial force: {members.max_axial()}"
    #         )
    #     write_json(output_file, nodes=result["nodes"], edges=result["edges"])
    # except Exception:
    #     raise Exception("Truss is not stable")
