import uuid
from argparse import ArgumentParser

import numpy as np
from scipy.spatial import ConvexHull, distance_matrix

from fea.openseespy import fea_opensees
from fea.utils import get_all_compression_tension_edges
from search.config import GeneralConfig, UCTSConfig
from search.models import Edge, Node, Vector3
from search.utils import load_config
from utils.parser import read_json
from utils.plot import visualize


class State:
    def __init__(self, config: UCTSConfig, nodes, edges, iteration=0):
        self.nodes: list[Node] = nodes
        self.edges = edges
        self.iteration = iteration
        self.config = config
        self.grid_nodes = []

        # we have to keep the max total edge length to normalize the edge length of a node in the scoring funcction
        self.max_total_edge_length = 0

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        if not self._edge_exists(edge.u, edge.v):
            self.edges.append(edge)

    def _edge_exists(self, u, v):
        for edge in self.edges:
            if (edge.u.id == u.id and edge.v.id == v.id) or (
                edge.u.id == v.id and edge.v.id == u.id
            ):
                return True
        return False

    def init_fully_connected(self):
        """init the state with free joint nodes that are within in the config constraints"""
        free_joints_points = self.get_nodes_in_convex_hull(
            grid_spacing=self.config.grid_density_unit,
            clamp_tolerance=self.config.clamp_tolerance,
        )
        for point in free_joints_points:
            self.nodes.append(
                Node(str(uuid.uuid4()), Vector3(point[0], point[1], point[2]))
            )

        self.connect_nodes_nearest_neighbors(num_neighbors=self.config.num_neighbors)
        edges_to_remove = []
        edges_to_add = []
        for edge in self.edges:
            self.divide_too_long_edge(edge, edges_to_remove, edges_to_add)
        for edge in edges_to_remove:
            self.edges.remove(edge)
        for edge in edges_to_add:
            self.add_edge(edge)
        self.connect_nodes_nearest_neighbors(num_neighbors=self.config.num_neighbors)

        self.max_total_edge_length = self.total_length()

    def total_length(self):
        return sum(edge.length() for edge in self.edges)

    def is_point_in_hull(self, point, hull):
        new_hull = ConvexHull(np.vstack((hull.points, point)))
        return np.array_equal(new_hull.vertices, hull.vertices)

    def distance_to_edge(self, point, edge_start, edge_end):
        edge = edge_end - edge_start
        point_vector = point - edge_start
        edge_length = np.linalg.norm(edge)

        if edge_length == 0:
            return np.linalg.norm(point_vector)

        projection_length = np.dot(point_vector, edge) / edge_length
        projection_length_clamped = np.clip(projection_length, 0, edge_length)

        closest_point_on_edge = edge_start + (
            edge * (projection_length_clamped / edge_length)
        )
        return np.linalg.norm(point - closest_point_on_edge)

    def distance_to_vertex(self, point, vertex):
        return np.linalg.norm(point - vertex)

    def get_nodes_in_convex_hull(
        self, grid_spacing=0.5, clamp_tolerance=0.1, vertex_tolerance=0.1
    ):
        points = [np.array([node.vec.x, node.vec.y, node.vec.z]) for node in self.nodes]

        hull = ConvexHull(points)
        nodes_within_hull = []
        nodes_on_edges = set()
        grid_range_x = [
            min([point[0] for point in points]),
            max([point[0] for point in points]),
        ]
        grid_range_y = [
            min([point[1] for point in points]),
            max([point[1] for point in points]),
        ]
        grid_range_z = [
            min([point[2] for point in points]),
            max([point[2] for point in points]),
        ]

        x_range = np.arange(
            grid_range_x[0], grid_range_x[1] + grid_spacing, grid_spacing
        )
        y_range = np.arange(
            grid_range_y[0], grid_range_y[1] + grid_spacing, grid_spacing
        )
        z_range = np.arange(
            grid_range_z[0], grid_range_z[1] + grid_spacing, grid_spacing
        )

        # Define edges from hull simplices
        edges = set()
        for simplex in hull.simplices:
            for i in range(len(simplex)):
                edge = tuple(sorted([simplex[i], simplex[(i + 1) % len(simplex)]]))
                edges.add(edge)
        edges = list(edges)

        for x in x_range:
            for y in y_range:
                for z in z_range:
                    point = np.array([x, y, z])
                    if self.is_point_in_hull(point, hull):
                        # Check if the point is near any edge
                        for edge_indices in edges:
                            edge_start, edge_end = (
                                points[edge_indices[0]],
                                points[edge_indices[1]],
                            )
                            if (
                                self.distance_to_edge(point, edge_start, edge_end)
                                <= clamp_tolerance
                            ):
                                if all(
                                    self.distance_to_vertex(point, vertex)
                                    > vertex_tolerance
                                    for vertex in points
                                ):
                                    nodes_on_edges.add(tuple(point))
                                break
                        else:
                            nodes_within_hull.append(point)

        return nodes_within_hull + list(nodes_on_edges)

    def connect_nodes_nearest_neighbors(self, num_neighbors=1):
        # Compute distance matrix
        nodes = np.array([[node.vec.x, node.vec.y, node.vec.z] for node in self.nodes])
        dist_matrix = distance_matrix(nodes, nodes)
        np.fill_diagonal(dist_matrix, np.inf)  # Avoid zero distance to self

        for i in range(len(nodes)):
            # Find the indices of the nearest neighbors
            nearest_neighbors = np.argsort(dist_matrix[i])[:num_neighbors]
            for neighbor in nearest_neighbors:
                if (
                    not self._edge_exists(self.nodes[i], self.nodes[neighbor])
                    and i != neighbor
                ):
                    self.add_edge(
                        Edge(str(uuid.uuid4()), self.nodes[i], self.nodes[neighbor])
                    )

    def _get_free_edges(self):
        free_edges = []
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                if not self._edge_exists(self.nodes[i], self.nodes[j]):
                    edge = Edge(str(uuid.uuid4()), self.nodes[i], self.nodes[j])
                    free_edges.append(edge)
        return free_edges

    def divide_too_long_edge(
        self, edge: Edge, edges_to_remove: list, edges_to_add: list
    ):
        if edge.length() > self.config.max_edge_len:
            # visualize(nodes =self.nodes, edges= self.edges, compression_edges=[edge.id])

            if self._edge_exists(edge.u, edge.v):
                edges_to_remove.append(edge)
            middle = Vector3(
                (edge.u.vec.x + edge.v.vec.x) / 2,
                (edge.u.vec.y + edge.v.vec.y) / 2,
                (edge.u.vec.z + edge.v.vec.z) / 2,
            )
            new_node = Node(str(uuid.uuid4()), middle)
            self.add_node(new_node)
            self.divide_too_long_edge(
                Edge(str(uuid.uuid4()), edge.u, new_node), edges_to_remove, edges_to_add
            )
            self.divide_too_long_edge(
                Edge(str(uuid.uuid4()), new_node, edge.v), edges_to_remove, edges_to_add
            )

        else:
            edges_to_add.append(edge)

    def remove_edge_least_impact(self) -> bool:
        if len(self.edges) == 0:
            return False

        results = {}
        tmp_edges = {}
        tmp_nodes = {}
        for current_edge in self.edges:
            new_nodes = self.nodes.copy()
            new_edges = [
                edge for edge in self.edges.copy() if edge.id != current_edge.id
            ]
            nodes = [current_edge.u, current_edge.v]
            for edge_node in nodes:
                if not any(
                    [
                        edge
                        for edge in new_edges
                        if edge.u.id == edge_node.id or edge.v.id == edge_node.id
                    ]
                ):
                    if edge_node.fixed or edge_node.load:
                        continue
                    new_nodes = [
                        node for node in self.nodes.copy() if node.id != edge_node.id
                    ]

            force_ratios = []

            try:
                max_forces = fea_opensees(self.nodes, self.edges)
                compression_tension_edges = get_all_compression_tension_edges(
                    self.edges, max_forces
                )
                for entry in compression_tension_edges:
                    force_ratios.append(
                        abs(entry["max_force"]) / abs(entry["euler_load"])
                    )

                    if abs(entry["max_force"]) > entry["euler_load"]:
                        results[current_edge.id] = -1

                results[current_edge.id] = max(force_ratios)
                tmp_edges[current_edge.id] = new_edges
                tmp_nodes[current_edge.id] = new_nodes

            except Exception:
                results[current_edge.id] = -1

        if all(value == -1 for value in results.values()):
            return False
        else:
            min_val = min(value for value in results.values() if value != -1)
            edge_id = [k for k, v in results.items() if v == min_val][0]
            self.nodes = tmp_nodes[edge_id]
            self.edges = tmp_edges[edge_id]
            return True


def execute(config_file: str) -> None:
    config = load_config(config_file)
    general_config = GeneralConfig(config)
    ucts_config = UCTSConfig(config)

    nodes, edges = read_json(general_config.input_file)

    state = State(config=ucts_config, nodes=nodes, edges=edges)
    state.init_fully_connected()

    iteration = 1
    while state.remove_edge_least_impact():
        print(f"Interation: {iteration}")
        iteration += 1
        print(f"Nodes: {len(state.nodes)}")
        print(f"Edges: {len(state.edges)}")

    print("/n")

    visualize(nodes=state.nodes, edges=state.edges)


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--config_file", type=str)
    args = parser.parse_args()

    execute(config_file=args.config_file)


if __name__ == "__main__":
    main()
