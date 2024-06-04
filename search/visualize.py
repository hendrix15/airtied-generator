import networkx as nx

import matplotlib.pyplot as plt


def visualize_tree(root):
    # Create an empty graph
    graph = nx.DiGraph()

    # Add the root node to the graph
    graph.add_node(root)

    # Add the children nodes recursively
    add_children_to_graph(graph, root)

    # Draw the graph
    pos = nx.nx_agraph.graphviz_layout(graph, prog="dot")
    nx.draw(graph, pos, with_labels=False, arrows=True)

    # export the graph
    plt.savefig("tree.png")
    # Display the graph
    plt.show()


def add_children_to_graph(graph, node):
    # Base case: if the node has no children, return
    if not node.children:
        return

    # Add the children nodes to the graph
    for child in node.children:
        graph.add_node(child)
        graph.add_edge(node, child)

        # Recursively add the children of the current child
        add_children_to_graph(graph, child)
