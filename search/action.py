from abc import ABC, abstractmethod
from search.models import Node, Edge


class AbstractAction(ABC):
    @abstractmethod
    def execute(self, state):
        pass


class AddNodeAction(AbstractAction):
    def __init__(
        self,
        newNode: Node,
        e_id=0,
    ):
        self.node = newNode
        self.e_id = e_id

    def __str__(self):
        return "add node at" + self.node.__str__()

    def execute(self, state):
        state.addNode(self.node)
        return state


class AddEdgeAction(AbstractAction):
    def __init__(
        self,
        edge: Edge,
    ):
        self.edge = edge

    def execute(self, state):
        state.addEdge(self.edge)
        return state
