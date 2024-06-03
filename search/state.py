import random
import uuid
from math import ceil, floor

from search.action import AbstractAction, AddEdgeAction, AddNodeWithEdgeAction
from search.config import UCTSConfig
from search.models import Edge, Node, Vector3
from search.utils import generate_FEA_truss


class State:
    def __init__(self, config: UCTSConfig, nodes, edges, iteration=0):
        self.nodes = nodes
        self.edges = edges
        self.iteration = iteration
        self.config = config

    def __str__(self):
        return (
            "nodes: "
            + str(self.nodes)
            + " edges: "
            + str(self.edges)
            + " eid: "
            + str(self.eid)
        )

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_legal_actions(self):
        new_node = self._create_random_node()
        new_edge = self._create_new_edge()
        if new_edge is None:
            return [AddNodeWithEdgeAction(new_node)]
        return [AddNodeWithEdgeAction(new_node), AddEdgeAction(new_edge)]

    def move(self, action: AbstractAction):
        self.iteration += 1
        return action.execute(self)

    def truss_holds(self):
        truss = generate_FEA_truss(self.nodes, self.edges)
        try:
            truss.analyze(check_statics=True)
            return True
        except Exception:
            return False

    def should_stop_search(self):
        return self.iteration > self.config.max_iter or self.truss_holds()

    def _create_random_node(self):
        min_x, max_x = self.config.min_x, self.config.max_x
        min_y, max_y = self.config.min_y, self.config.max_y
        min_z, max_z = self.config.min_z, self.config.max_z
        id = str(uuid.uuid4())

        x = random.randint(floor(min_x / 0.25), ceil(max_x / 0.25)) * 0.25
        y = random.randint(floor(min_y / 0.25), ceil(max_y / 0.25)) * 0.25
        z = random.randint(floor(min_z / 0.25), ceil(max_z / 0.25)) * 0.25

        return Node(id, Vector3(x, y, z), support=False, load=None)

    def _create_new_edge(self):
        if len(self.edges) == len(self.nodes) * (len(self.nodes) - 1) / 2:
            return None

        while True:
            u, v = random.sample(self.nodes, 2)
            if not self._edge_exists(u, v):
                return Edge(str(uuid.uuid4()), u, v)

    def _edge_exists(self, u, v):
        for edge in self.edges:
            if (edge.u == u and edge.v == v) or (edge.u == v and edge.v == u):
                return True
        return False

    def total_length(self):
        return sum(edge.length() for edge in self.edges)
