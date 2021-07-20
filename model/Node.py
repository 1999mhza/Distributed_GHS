import threading
from time import time

from model.Channel import Channel
from model.Enum import NodeState, EdgeState, Messagetype
from model.Message import Message


class Node(threading.Thread):
    def __init__(self, id, manager):
        threading.Thread.__init__(self)
        self.manager = manager
        self.channel = Channel(self)

        self.id = id
        self.edges = []

        self.done = False
        self.numberOfMessages = 0
        self.numberOfBits = 0
        self.time = None
        self.awake = False

        self.level = None
        self.fragment = None
        self.state = NodeState.Sleeping

        self.inBranch = None
        self.testEdge = None
        self.findCount = None
        self.bestEdge = None
        self.bestWeight = (float('inf'), float('inf'), float('inf'))

    def getChannel(self):
        return self.channel

    def getId(self):
        return self.id

    def getFragment(self):
        return self.fragment

    def getLevel(self):
        return self.level

    def getEdges(self):
        return self.edges

    def getTime(self):
        return self.time

    def setTime(self, time):
        self.time = time

    def isDone(self):
        return self.done

    def addEdge(self, edge):
        self.edges.append(edge)
        if not self.bestEdge or edge.getWeight() < self.bestWeight:
            self.bestEdge = edge
            self.bestWeight = edge.getWeight()

    def getEdge(self, id):
        for edge in self.edges:
            if edge.getNode().getId() == id:
                return edge
        return None

    def checkBasicEdges(self):
        for edge in self.edges:
            if edge.getState() == EdgeState.Basic:
                return True
        return False

    def getMinBasicEdges(self):
        min = None
        for edge in self.edges:
            if edge.getState() == EdgeState.Basic and (not min or edge < min):
                min = edge
        return min

    def increaseMessage(self, size):
        self.numberOfBits += size
        self.numberOfMessages += 1

    def getNumberOfMessagesAndBits(self):
        return self.numberOfMessages, self.numberOfBits

    def getBranches(self):
        branches = set()
        for edge in self.edges:
            if edge.getState() == EdgeState.Branch:
                weight = edge.getWeight()
                branches.add((weight[1], weight[2]))
        return branches

    def __lt__(self, other):
        return self.id < other.id

    def halting(self):
        self.done = True

    def awakening(self):
        self.awake = True

    def procedureWakeup(self):
        self.bestEdge.changeState(EdgeState.Branch)
        self.level = 0
        self.state = NodeState.Found
        self.findCount = 0
        self.send(self.bestEdge, Message(self.id, Messagetype.Connect, level=0))

    def responseConnect(self, edge, level):
        if self.state == NodeState.Sleeping:
            self.procedureWakeup()

        if level < self.level:
            edge.changeState(EdgeState.Branch)
            self.send(edge, Message(self.id, Messagetype.Initiate, level=self.level, fragment=self.fragment, state=self.state))
            if self.state == NodeState.Find:
                self.findCount += 1

        elif edge.getState() == EdgeState.Basic:
            self.channel.addToQueue(time(), Message(edge.getNode().getId(), Messagetype.Connect, level=level), False)

        else:
            self.send(edge, Message(self.id, Messagetype.Initiate, level=self.level + 1, fragment=edge.getWeight(), state=NodeState.Find))

    def responseInitiate(self, edge, level, fragment, state):
        self.level = level
        self.fragment = fragment
        self.state = state
        self.inBranch = edge
        self.bestEdge = None
        self.bestWeight = (float('inf'), float('inf'), float('inf'))

        for myEdge in self.edges:
            if not myEdge == edge and myEdge.getState() == EdgeState.Branch:
                self.send(myEdge, Message(self.id, Messagetype.Initiate, level=level, fragment=fragment, state=state))
                if state == NodeState.Find:
                    self.findCount += 1

        if state == NodeState.Find:
            self.procedureTest()

    def procedureTest(self):
        if self.checkBasicEdges():
            self.testEdge = self.getMinBasicEdges()
            self.send(self.testEdge, Message(self.id, Messagetype.Test, level=self.level, fragment=self.fragment))

        else:
            self.testEdge = None
            self.procedureReport()

    def responseTest(self, edge, level, fragment):
        if self.state == NodeState.Sleeping:
            self.procedureWakeup()

        if level > self.level:
            self.channel.addToQueue(time(), Message(edge.getNode().getId(), Messagetype.Test, level=level, fragment=fragment), False)

        elif fragment != self.fragment:
            self.send(edge, Message(self.id, Messagetype.Accept))

        else:
            if edge.getState() == EdgeState.Basic:
                edge.changeState(EdgeState.Rejected)

            if not self.testEdge == edge:
                self.send(edge, Message(self.id, Messagetype.Reject))
            else:
                self.procedureTest()

    def responseAccept(self, edge):
        self.testEdge = None

        if edge.getWeight() < self.bestWeight:
            self.bestEdge = edge
            self.bestWeight = edge.getWeight()

        self.procedureReport()

    def responseReject(self, edge):
        if edge.getState() == EdgeState.Basic:
            edge.changeState(EdgeState.Rejected)

        self.procedureTest()

    def procedureReport(self):
        if self.findCount == 0 and not self.testEdge:
            self.state = NodeState.Found
            self.send(self.inBranch, Message(self.id, Messagetype.Report, fragment=self.bestWeight))

    def responseReport(self, edge, weight):
        if not edge == self.inBranch:
            self.findCount -= 1

            if weight < self.bestWeight:
                self.bestWeight = weight
                self.bestEdge = edge

            self.procedureReport()

        elif self.state == NodeState.Find:
            self.channel.addToQueue(time(), Message(edge.getNode().getId(), Messagetype.Report, fragment=weight), False)

        elif weight > self.bestWeight:
            self.procedureChangeCore()

        elif weight == self.bestWeight == (float('inf'), float('inf'), float('inf')):
            self.manager.halting()

    def procedureChangeCore(self):
        if self.bestEdge.getState() == EdgeState.Branch:
            self.send(self.bestEdge, Message(self.id, Messagetype.ChangeCore))

        else:
            self.bestEdge.changeState(EdgeState.Branch)
            self.send(self.bestEdge, Message(self.id, Messagetype.Connect, level=self.level))

    def responseChangeCore(self):
        self.procedureChangeCore()

    def send(self, edge, message):
        if not edge.getNode().isDone():
            edge.getNode().getChannel().addToQueue(time() + edge.getDelay(), message)

    def parse(self, message):
        if not message:
            return

        id = message.getId()
        type = message.getType()
        level = message.getLevel()
        fragment = message.getFragment()
        state = message.getState()
        edge = self.getEdge(id)

        if type == Messagetype.Reject:
            self.responseReject(edge)

        elif type == Messagetype.Accept:
            self.responseAccept(edge)

        elif type == Messagetype.Test:
            self.responseTest(edge, level, fragment)

        elif type == Messagetype.Initiate:
            self.responseInitiate(edge, level, fragment, state)

        elif type == Messagetype.Connect:
            self.responseConnect(edge, level)

        elif type == Messagetype.Report:
            self.responseReport(edge, fragment)

        elif type == Messagetype.ChangeCore:
            self.responseChangeCore()

    def run(self):
        if self.awake and self.state == NodeState.Sleeping:
            self.procedureWakeup()

        while not self.done:
            self.parse(self.channel.getMessage())
