from enum import Enum

from search.models import Node


class Opt(Enum):
    ADD_NODE = 0
    ADD_EDGE = 1


class Action:
    def __init__(
        self,
        opt,
        u: Node,
        v: Node,
        vec: Node | None = None,
        eid=0,
    ):
        self.opt = opt
        self.stateid = -1
        self.d = None
        self.t = None

        if opt == Opt.ADD_NODE.value:
            self.vec = vec  # add node

        if opt == Opt.ADD_EDGE.value:
            self.opt = opt
            self.u = u
            self.v = v

    def __str__(self):
        if self.opt == Opt.ADD_NODE.value:
            return "add node at" + self.vec.__str__()
        if self.opt == Opt.ADD_EDGE.value:
            return "add edge between" + str(self.u) + "and" + str(self.v)
