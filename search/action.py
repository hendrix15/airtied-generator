from abc import ABC, abstractmethod
import random
from search.models import Edge, Node
import uuid

class AbstractAction(ABC):
    @abstractmethod
    def execute(self, state):
        pass


class AddNodeAction(AbstractAction):
    def __init__(
        self,
        newNode: Node,
    ):
        self.node = newNode

    def execute(self, state):
        new_state = state.deep_copy()
        new_state.add_node(self.node)
        new_state.grid_nodes = [
            node for node in new_state.grid_nodes if node.id != self.node.id
        ]
        new_state.iteration += 1
        return new_state


class AddNodeWithEdgeAction(AbstractAction):
    def __init__(
        self,
        newNode: Node,
    ):
        self.node = newNode

    def execute(self, state):
        new_state = state.deep_copy()
        new_state.add_node(self.node)
        self._add_random_edge(new_state)
        new_state.iteration += 1
        return new_state

    def _add_random_edge(self, state):
        existing_node = random.choice(state.nodes)
        edge = Edge(str(uuid.uuid4()), self.node, existing_node)
        state.add_edge(edge)


class AddEdgeAction(AbstractAction):
    def __init__(
        self,
        edge: Edge,
    ):
        self.edge = edge

    def execute(self, state):
        new_state = state.deep_copy()
        new_state.add_edge(self.edge)
        new_state.iteration += 1
        return new_state


class RemoveEdgeAction(AbstractAction):
    def __init__(
        self,
        edge: Edge,
    ):
        self.edge = edge

    def execute(self, state):
        new_state = state.deep_copy()
        new_state.edges = [edge for edge in new_state.edges if edge.id != self.edge.id]
        # # remove node if it is not connected to any edge
        nodes = [self.edge.u, self.edge.v]
        if not any(
            [edge for edge in new_state.edges if edge.u.id == nodes[0].id or edge.v.id == nodes[0].id]
        ):
            new_state.nodes = [
                node for node in new_state.nodes if node.id != nodes[0].id
            ]

        if not any(
            [edge for edge in new_state.edges if edge.v.id == nodes[1].id or edge.u.id == nodes[1].id]
        ):
            new_state.nodes = [
                node for node in new_state.nodes if node.id != nodes[1].id
            ]

        new_state.iteration += 1
        return new_state


class AddEdgeWithNewNodeAction(AbstractAction):
    def __init__(
        self,
        edge: Edge,
        newNode: Node,
    ):
        self.edge = edge
        self.node = newNode

    def execute(self, state):
        new_state = state.deep_copy()
        new_state.add_node(self.node)
        new_state.add_edge(self.edge)
        new_state.iteration += 1
        return new_state


class TestAction(AbstractAction):
    def __init__(
        self,
        score: int,
    ):
        self.score = score

    def execute(self, state):
        new_state = state.deep_copy()
        new_state.score += self.score
        new_state.iteration += 1
        return new_state
