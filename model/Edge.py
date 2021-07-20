from model.Enum import EdgeState


class Edge:
    def __init__(self, node, weight, delay):
        self.node = node
        self.weight = weight
        self.delay = delay
        self.state = EdgeState.Basic

    def __str__(self):
        return f'{self.weight} {self.state}'

    def changeState(self, state):
        self.state = state

    def __lt__(self, other):
        if self.weight[0] < other.weight[0]:
            return True
        if self.weight[0] == other.weight[0] and self.weight[1] < other.weight[1]:
            return True
        if self.weight[0] == other.weight[0] and self.weight[1] == other.weight[1] and self.weight[2] < other.weight[2]:
            return True
        return False

    def getNode(self):
        return self.node

    def getWeight(self):
        return self.weight

    def getDelay(self):
        return self.delay

    def getState(self):
        return self.state
