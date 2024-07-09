from pathlib import Path

from search.config import GeneralConfig, UCTSConfig
from search.state import State
from search.truss_search_tree import TreeSearchNode, TrussSearchTree
from utils.parser import read_json, write_json
from utils.plot import visualize


def execute(config_file: str) -> None:
    general_config = GeneralConfig(config_file)
    ucts_config = UCTSConfig(config_file)

    nodes, edges = read_json(general_config.input_file)

    state = State(config=ucts_config, nodes=nodes, edges=edges)
    state.init_fully_connected()

    visualize(
        nodes=state.nodes,
        edges=state.edges,
    )


    root = TreeSearchNode(state=state, parent=None)
    mcts = TrussSearchTree(root=root)
    mcts.simulate(ucts_config.max_iter)

    folder_name = Path(general_config.input_file).stem
    output_path = f"{general_config.output_folder}{folder_name}/"
    # shutil.rmtree(output_path)
    # shutil.rmtree(image_path)

    # visualize_tree(root)
    # return
    # Store and print best k children
    best_children = mcts.get_k_best_children(general_config.k)
    for i, child in enumerate(best_children):
        nodes = [node for node in child.state.nodes]
        edges = [edge for edge in child.state.edges]
        print(
            "visualizing child",
            i,
            "with score",
            child.score,
            " and ",
            len(edges),
            "edges",
        )
        write_json(
            nodes=child.state.nodes,
            edges=child.state.edges,
            dirname=output_path,
            filename=f"{i}.json",
        )
        visualize(
            nodes=child.state.nodes,
            edges=child.state.edges,
            dirname=output_path,
            filename=f"{i}.png",
        )

    # leafs = mcts.get_leafs()
    # print('leafs', leafs)
    # for j, leaf in enumerate(leafs):
    #     print("visualizing leaf", j, 'with score', leaf.score, " and ", len(leaf.state.edges), "edges")
    #     write_json(nodes=leaf.state.nodes, edges=leaf.state.edges, dirname=output_path, filename=f"leaf_{j}.json")
    #     visualize(nodes=leaf.state.nodes, edges=leaf.state.edges, dirname=output_path, filename=f"leaf_{j}.png")
