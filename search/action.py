from abc import ABC, abstractmethod
import random
from search.models import Edge, Node
import uuid

class AbstractAction(ABC):
    @abstractmethod
    def execute(self, state):
        pass


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
        return new_state
