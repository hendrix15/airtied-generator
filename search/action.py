from abc import ABC, abstractmethod

from search.models import Edge, Node


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

    def execute(self, state):
        state.add_node(self.node)
        return state


class AddEdgeAction(AbstractAction):
    def __init__(
        self,
        edge: Edge,
    ):
        self.edge = edge

    def execute(self, state):
        state.add_edge(self.edge)
        return state
