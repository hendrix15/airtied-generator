from search.action import AbstractAction
import uuid
from search.models import Node, Vector3, Edge
from search.config import TrussEnvironmentConfig, UCTSConfig
import numpy as np
import random
from math import ceil, floor
from search.action import AddNodeAction, AddEdgeAction


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

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def get_legal_actions(self, config: TrussEnvironmentConfig):
        new_node = self._create_random_node(config)
        new_edge = self._create_new_edge()
        return [AddNodeAction(new_node, id), AddEdgeAction(new_edge)]

    def move(self, action: AbstractAction):
        self.iteration += 1
        return action.execute(self)

    def truss_holds(self):
        # TODO: Check FEA if the truss holds
        pass

    @property
    def should_stop_search(self):
        return self.iteration > self.config.max_iter or self.truss_holds()

    def _create_random_node(self, config: TrussEnvironmentConfig):
        min_x, max_x = config.min_x, config.max_x
        min_y, max_y = config.min_y, config.max_y
        min_z, max_z = config.min_z, config.max_z
        id = str(uuid.uuid4())

        x = random.randint(floor(min_x / 0.25), ceil(max_x / 0.25)) * 0.25
        y = random.randint(floor(min_y / 0.25), ceil(max_y / 0.25)) * 0.25
        z = random.randint(floor(min_z / 0.25), ceil(max_z / 0.25)) * 0.25

        return Node(id, Vector3(x, y, z), support=False, load=None)

    def _create_new_edge(self):
        # TODO: improve this
        u, v = random.sample(self.nodes, 2)
        existing_edges = [
            edge
            for edge in self.edges
            if edge.u.id == u.id
            and edge.v.id == v.id
            or edge.u.id == v.id
            and edge.v.id == u.id
        ]

        return Edge(str(uuid.uuid4()), u, v)
