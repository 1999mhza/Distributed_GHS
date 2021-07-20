from time import time

import networkx as nx
from numpy import random

from model.Edge import Edge
from model.Enum import EdgeState
from model.Node import Node


class MainManager:
    def __init__(self):
        self.nodes = []
        self.numberOfNodes = 0
        self.numberOfEdges = 0
        self.awakeNode = None
        self.timeOfExecution = 0
        self.numberOfMessages = 0
        self.numberOfBits = 0
        self.maxLevel = 0
        self.defaultDelay = 0.2
        self.graph = nx.Graph()
        self.positions = None

    def clear(self):
        self.nodes = []
        self.numberOfNodes = 0
        self.graph.clear()

    def getGraph(self):
        return self.graph

    def setPositions(self):
        self.positions = nx.spring_layout(self.graph)

    def updateGraph(self):
        G = self.graph
        pos = self.positions

        nx.draw(G, pos)
        nx.draw_networkx_labels(G, pos, font_size=15)
        nx.draw_networkx_nodes(G, pos, node_color='yellow', linewidths=1, node_size=500)

        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        nx.draw_networkx_edges(G, pos, edgelist=self.getEdges(EdgeState.Basic), edge_color="green", width=3, label="Basic")
        nx.draw_networkx_edges(G, pos, edgelist=self.getEdges(EdgeState.Branch), edge_color="blue", width=3, label="Branch")
        nx.draw_networkx_edges(G, pos, edgelist=self.getEdges(EdgeState.Rejected), edge_color="red", width=3, label="Rejected")

    def getDefaultDelay(self):
        return self.defaultDelay

    def getNumberOfNodes(self):
        return self.numberOfNodes

    def getEdges(self, type):
        edges = []
        for edge in self.graph.edges:
            state1 = self.getNode(edge[0]).getEdge(edge[1]).getState()
            state2 = self.getNode(edge[1]).getEdge(edge[0]).getState()

            if state1 == state2 == type:
                edges.append(edge)

        return edges

    def getEdgeLegends(self):
        legends = []
        for edge in self.graph.edges:
            state1 = self.getNode(edge[0]).getEdge(edge[1]).getState()
            state2 = self.getNode(edge[1]).getEdge(edge[0]).getState()

            if state1 == EdgeState.Branch or state2 == EdgeState.Branch:
                legends.append('branch')

            elif state1 == EdgeState.Rejected or state2 == EdgeState.Rejected:
                legends.append('rejected')

            else:
                legends.append('basic')

        return legends

    def getNumberOfFragments(self):
        fragments = set()
        numberOfNones = 0

        for node in self.nodes:
            fragment = node.getFragment()
            if fragment:
                fragments.add(fragment)
            else:
                numberOfNones += 1

        return len(fragments) + numberOfNones

    def getNode(self, id):
        for node in self.nodes:
            if node.getId() == id:
                return node
        return None

    def halting(self):
        for node in self.nodes:
            node.halting()

    def addNode(self, numberOfNodes):
        for i in range(numberOfNodes):
            self.nodes.append(Node(i, self))
            self.graph.add_node(i)
        self.numberOfNodes = numberOfNodes

    def addRingEdges(self):
        self.numberOfEdges = self.numberOfNodes
        for i in range(self.numberOfNodes):
            j = (i + 1) % self.numberOfNodes
            weight = random.randint(100) / 100
            self.nodes[i].addEdge(Edge(self.nodes[j], (weight, min(i, j), max(i, j)), self.defaultDelay))
            self.nodes[j].addEdge(Edge(self.nodes[i], (weight, min(i, j), max(i, j)), self.defaultDelay))
            self.graph.add_edge(i, j, weight=weight)

    def addCompleteEdges(self):
        self.numberOfEdges = self.numberOfNodes * (self.numberOfNodes - 1) / 2
        for i in range(self.numberOfNodes):
            for j in range(i + 1, self.numberOfNodes):
                weight = random.randint(100) / 100
                self.nodes[i].addEdge(Edge(self.nodes[j], (weight, min(i, j), max(i, j)), self.defaultDelay))
                self.nodes[j].addEdge(Edge(self.nodes[i], (weight, min(i, j), max(i, j)), self.defaultDelay))
                self.graph.add_edge(i, j, weight=weight)

    def addRandomEdges(self, numberOfEdges):
        i = 0
        self.numberOfEdges = numberOfEdges
        while i < self.numberOfEdges:
            index1 = random.randint(self.numberOfNodes)
            index2 = random.randint(self.numberOfNodes)

            if self.nodes[index1].getEdge(index2) or self.nodes[index2].getEdge(index1) or index1 == index2:
                continue

            weight = random.randint(100) / 100
            self.nodes[index1].addEdge(Edge(self.nodes[index2], (weight, min(index1, index2), max(index1, index2)), self.defaultDelay))
            self.nodes[index2].addEdge(Edge(self.nodes[index1], (weight, min(index1, index2), max(index1, index2)), self.defaultDelay))
            self.graph.add_edge(index1, index2, weight=weight)
            i += 1

        while True:
            labels = {}

            for node in self.nodes:
                labels[node] = False

            self.DFS(self.nodes[0], labels)

            check = True
            for node1, value1 in labels.items():
                if not value1:
                    for node2, value2 in labels.items():
                        if value2:
                            weight = random.randint(100) / 100
                            index1 = node1.getId()
                            index2 = node2.getId()

                            node1.addEdge(Edge(node2, (weight, min(index1, index2), max(index1, index2)), self.defaultDelay))
                            node2.addEdge(Edge(node1, (weight, min(index1, index2), max(index1, index2)), self.defaultDelay))
                            self.numberOfEdges += 1
                            self.graph.add_edge(index1, index2, weight=weight)
                            break
                    check = False
                    break

            if check:
                break

    def setAwakeNode(self, node):
        if id:
            self.awakeNode = node

    def addEdge(self, id1, id2, weight, delay):

        node1 = self.getNode(id1)
        if not node1:
            node1 = Node(id1, self)
            self.nodes.append(node1)
            self.graph.add_node(id1)
            self.numberOfNodes += 1

        node2 = self.getNode(id2)
        if not node2:
            node2 = Node(id2, self)
            self.nodes.append(node2)
            self.graph.add_node(id2)
            self.numberOfNodes += 1

        if node1.getEdge(id2) or node2.getEdge(id1):
            return False

        node1.addEdge(Edge(node2, (weight, min(id1, id2), max(id1, id2)), delay))
        node2.addEdge(Edge(node1, (weight, min(id1, id2), max(id1, id2)), delay))
        self.numberOfEdges += 1
        self.graph.add_edge(id1, id2, weight=weight)
        return True

    def DFS(self, node, labels):
        labels[node] = True

        for edge in node.getEdges():
            adjacent = edge.getNode()
            if not labels[adjacent]:
                self.DFS(adjacent, labels)

    def checkConnectedGraph(self):
        labels = {}

        for node in self.nodes:
            labels[node] = False

        self.DFS(self.nodes[0], labels)

        for _, value in labels.items():
            if not value:
                return False

        return True

    def run(self):

        if self.awakeNode:
            self.awakeNode.awakening()
        else:
            for node in self.nodes:
                node.awakening()

        startTime = time()

        for node in self.nodes:
            node.setTime(startTime)

        for node in self.nodes:
            node.start()

        for node in self.nodes:
            node.join()

        self.timeOfExecution = time() - startTime

        for node in self.nodes:
            info = node.getNumberOfMessagesAndBits()
            self.numberOfMessages += info[0]
            self.numberOfBits += info[1]
            self.maxLevel = max(self.maxLevel, node.getLevel())

    def __str__(self):
        string = '\n'
        string += f'number of nodes = {self.numberOfNodes}\n'
        string += f'number of edges = {self.numberOfEdges}\n'
        string += f'number of levels = {self.maxLevel}\n'
        string += f'total time of execution = {self.timeOfExecution:.2f}\n'
        string += f'average time of execution per level = {self.timeOfExecution / self.maxLevel:.2f}\n'
        string += f'total number of messages = {self.numberOfMessages}\n'
        string += f'average number of messages per node = {self.numberOfMessages / self.numberOfNodes:.2f}\n'
        string += f'average number of messages per level = {self.numberOfMessages / self.maxLevel:.2f}\n'
        string += f'total number of bits = {self.numberOfBits}\n'
        string += f'average number of bits per node = {self.numberOfBits / self.numberOfNodes:.2f}\n'
        string += f'average number of bits per message = {self.numberOfBits / self.numberOfMessages:.2f}\n'

        branches = set()
        for node in self.nodes:
            branches = branches.union(node.getBranches())

        branches = list(branches)
        branches.sort()

        string += f'\nbranches:'
        for branch in branches:
            string += f'\n\t({branch[0]},{branch[1]})'

        return string

