from __future__ import annotations

import numpy as np
from tqdm import tqdm

from search.state import State


class TreeSearchNode:
    def __init__(
        self,
        state: State,
        parent: TreeSearchNode | None = None,
    ):
        self.state = state
        self.parent = parent
        self._number_of_visits = 0.0
        self._result = 0.0
        self._untried_actions = None
        self.children = []
        self.score = -100

    @property
    def untried_actions(self):
        if self._untried_actions is None:
            self._untried_actions = self.state.get_legal_actions()
        return self._untried_actions

    @property
    def q(self):
        return self._result

    @property
    def n(self):
        return self._number_of_visits

    def expand(self):
        action = self.untried_actions.pop()
        next_state = self.state.move(action)
        child_node = TreeSearchNode(state=next_state, config=self.config, parent=self)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        return self.state.calculate_fea_score() < 0

    def rollout(self):
        current_rollout_state = self.state
        while not current_rollout_state.should_stop_search():
            possible_moves = current_rollout_state.get_legal_actions()
            action = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.move(action)
        fea_score = current_rollout_state.calculate_fea_score()
        self.score = (
            -1
            if fea_score < 0
            else (1 - (self.state.total_length() / self.state.max_total_edge_length))
        )
        return self.score

    def backpropagate(self, result):
        self._number_of_visits += 1.0
        self._result += result
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self):
        return len(self.untried_actions) == 0

    def best_child(self, c_param=0):
        choices_weights = [
            (c.q / c.n) + c_param * np.sqrt((2 * np.log(self.n) / c.n))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def best_children(self, n):
        choices_weights = [
            (c.q / c.n) + np.sqrt((2 * np.log(self.n) / c.n)) for c in self.children
        ]
        return [self.children[i] for i in np.argsort(choices_weights)[-n:]]

    def rollout_policy(self, possible_moves):
        return possible_moves[np.random.randint(len(possible_moves))]


class TrussSearchTree:
    def __init__(self, root: TreeSearchNode) -> None:
        self.root = root

    def simulate(self, simulations_number):
        """

        Parameters
        ----------
        simulations_number : int
            number of simulations performed to get the best action

        Returns
        -------

        """

        for simulation in tqdm(range(0, simulations_number)):
            # selection
            v = self._tree_policy()
            # rollout
            reward = v.rollout()
            # backpropagation
            v.backpropagate(reward)
            # if simulation % 100 == 0:
            #     visualize(
            #         nodes=v.state.nodes,
            #         edges=v.state.edges,
            #         dirname="output/run/",
            #         filename=f"{simulation}.png",
            #     )

    def _tree_policy(self):
        """
        selects node to run rollout/playout for

        Returns
        -------

        """
        current_node = self.root
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

    def get_leafs(self):
        leafs = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            if node.is_terminal_node():
                leafs.append(node)
            else:
                stack.extend(node.children)
        return leafs

    def get_k_best_children(self, k: int):
        children = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            children.append(node)
            stack.extend(node.children)
        children.sort(key=lambda x: x.score)
        print("Scores")
        print([child.score for child in children])
        # print("Best Scores")
        # print([child.score for child in children[-k:]])
        # print("FEA Scores")
        # print([child.state.calculate_fea_score() for child in children])
        return children[-k:]
