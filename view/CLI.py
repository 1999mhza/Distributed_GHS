import logging
import sys
from datetime import datetime
from threading import Thread
from time import sleep

from matplotlib import pyplot as plt
from tqdm import tqdm

from controller.Manager import MainManager


class CLI:
    def __init__(self):
        self.manager = MainManager()

    def getDesiredInput(self):

        print("\nTo finish edges, enter \"finish\". To back home, enter \"back\". To exit, enter \"exit\".\n")
        line = input("Enter the edges: (node1 node2 weight delay)\n")
        if line.lower().startswith("ex"):
            sys.exit(1)

        if line.lower().startswith("ba"):
            return 1

        while not line.lower().startswith("fi"):
            try:
                edge = line.split(" ")

                if edge[0].isalpha() and len(edge[0]) == 1:
                    id1 = edge[0].upper()
                elif edge[0].isalpha() and len(edge[0]) != 1:
                    raise Exception
                elif edge[0].isdigit():
                    id1 = int(edge[0])
                else:
                    raise Exception

                if edge[1].isalpha() and len(edge[1]) == 1:
                    id2 = edge[1].upper()
                elif edge[1].isalpha() and len(edge[1]) != 1:
                    raise Exception
                elif edge[1].isdigit():
                    id2 = int(edge[1])
                else:
                    raise Exception

                weight = float(edge[2])

                if len(edge) < 4:
                    delay = self.manager.getDefaultDelay()
                else:
                    delay = float(edge[3])

                if id1 == id2:
                    print("Unsuccessful! Loop is not allowed!")
                    line = input()

                    if line.lower().startswith("ex"):
                        sys.exit(1)

                    if line.lower().startswith("ba"):
                        return 1
                    continue

                if delay <= 0:
                    print("Unsuccessful! Weight is invalid!")
                    line = input()

                    if line.lower().startswith("ex"):
                        sys.exit(1)

                    if line.lower().startswith("ba"):
                        return 1
                    continue

                if weight < 0:
                    print("Unsuccessful! Delay is invalid!")
                    line = input()

                    if line.lower().startswith("ex"):
                        sys.exit(1)

                    if line.lower().startswith("ba"):
                        return 1
                    continue

                if not self.manager.addEdge(id1, id2, weight, delay):
                    print("Unsuccessful! Edge exits!")
                    line = input()

                    if line.lower().startswith("ex"):
                        sys.exit(1)

                    if line.lower().startswith("ba"):
                        return 1
                    continue

            except Exception as e:
                print(e)

                print("Unsuccessful! Invalid edge!")
                line = input()

                if line.lower().startswith("ex"):
                    sys.exit(1)

                if line.lower().startswith("ba"):
                    return 1
                continue

            line = input()

            if line.lower().startswith("ex"):
                sys.exit(1)

            if line.lower().startswith("ba"):
                return 1
            continue

        return 2

    def run(self):

        index = input("Enter the type of graph:\n1: Desired\n2: Ring\n3: Complete\n4: Random\n5: Exit\n")
        while True:
            self.manager.clear()
            try:
                index = int(index)
                if not 0 < index <= 5:
                    index = input("Illegal input!\n")
                    continue
            except Exception:
                index = input("Illegal input!\n")
                continue

            if index == 1:

                index2 = self.getDesiredInput()
                while index2 != 1 and not self.manager.checkConnectedGraph():
                    index2 = input("The graph is not connected!\n1: New graph\n2: Add edge\n")
                    while True:
                        index2 = int(index2)
                        if not 0 < index2 <= 2:
                            index2 = input("Illegal input!\n")
                            continue

                    if index2 == 1:
                        break
                    else:
                        index2 = self.getDesiredInput()

                if index2 == 1:
                    self.manager.clear()
                    index = input("\nEnter the type of graph:\n1: Desired\n2: Ring\n3: Complete\n4: Random\n5: Exit\n")
                    continue

            else:
                print("\nTo back home, enter \"back\". To exit, enter \"exit\".\n")
                line = input("Enter the number of nodes:\n")

                if line.lower().startswith("ex"):
                    sys.exit(1)

                if line.lower().startswith("ba"):
                    index = input("\nEnter the type of graph:\n1: Desired\n2: Ring\n3: Complete\n4: Random\n5: Exit\n")
                    continue

                while True:
                    try:
                        numberOfNodes = int(line)
                        self.manager.addNode(numberOfNodes)
                        break

                    except Exception:
                        line = input("Illegal input!\n")

                        if line.lower().startswith("ex"):
                            sys.exit(1)

                        if line.lower().startswith("ba"):
                            index = input("\nEnter the type of graph:\n1: Desired\n2: Ring\n3: Complete\n4: Random\n5: Exit\n")
                            break

                if line.lower().startswith("ba"):
                    continue

                if index == 2:
                    self.manager.addRingEdges()

                elif index == 3:
                    self.manager.addCompleteEdges()

                elif index == 4:

                    line = input("\nEnter the number of edges:\n")

                    if line.lower().startswith("ex"):
                        sys.exit(1)

                    if line.lower().startswith("ba"):
                        index = input("\nEnter the type of graph:\n1: Desired\n2: Ring\n3: Complete\n4: Random\n5: Exit\n")
                        continue

                    while True:
                        try:
                            numberOfEdges = int(line)
                            numberOfNodes = self.manager.getNumberOfNodes()

                            if not numberOfNodes - 1 <= numberOfEdges <= (numberOfNodes - 1) * numberOfNodes / 2:
                                line = input("Invalid number!\n")

                                if line.lower().startswith("ex"):
                                    sys.exit(1)

                                if line.lower().startswith("ba"):
                                    index = input("\nEnter the type of graph:\n1: Desired\n2: Ring\n3: Complete\n4: Random\n5: Exit\n")
                                    break

                            self.manager.addRandomEdges(numberOfEdges)
                            break

                        except Exception:
                            line = input("Illegal input!\n")

                            if line.lower().startswith("ex"):
                                sys.exit(1)

                            if line.lower().startswith("ba"):
                                index = input("\nEnter the type of graph:\n1: Desired\n2: Ring\n3: Complete\n4: Random\n5: Exit\n")
                                break

                    if line.lower().startswith("ba"):
                        continue

                else:
                    sys.exit(1)

            awakeId = input("\nEnter the id of awake node: (To awaken all nodes, enter \"all\")\n")
            if awakeId.lower().startswith("ex"):
                sys.exit(1)

            if awakeId.lower().startswith("ba"):
                index = input("\nEnter the type of graph:\n1: Desired\n2: Ring\n3: Complete\n4: Random\n5: Exit\n")
                continue

            check = False
            while True:
                if not awakeId.lower().startswith("al"):
                    if awakeId.isdigit():
                        node = self.manager.getNode(int(awakeId))
                        if node:
                            self.manager.setAwakeNode(node)
                            check = True
                            break
                    elif awakeId.isalpha() and len(awakeId) == 1:
                        node = self.manager.getNode(awakeId.upper())
                        if node:
                            self.manager.setAwakeNode(node)
                            check = True
                            break

                    awakeId = input("Invalid id! Enter the id of awake node: (To awaken all nodes, enter \"all\")\n")
                    if awakeId.lower().startswith("ex"):
                        sys.exit(1)

                    if awakeId.lower().startswith("ba"):
                        index = input("\nEnter the type of graph:\n1: Desired\n2: Ring\n3: Complete\n4: Random\n5: Exit\n")
                        break

                else:
                    check = True
                    break

            if check:
                break

        self.manager.setPositions()
        self.manager.updateGraph()
        plt.legend(scatterpoints=1)
        plt.show()

        print("\nGHS Algorithm Started!\n")

        logging.basicConfig(format='%(message)s', filename="../result/GHS.log", level=logging.INFO, filemode='w')
        logging.info(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ") GHS was run!\n")

        wait = Progress(self.manager)
        wait.start()

        self.manager.run()

        wait.stop()

        self.manager.updateGraph()
        plt.legend(scatterpoints=1)
        plt.show()

        logging.info(self.manager)


class Progress(Thread):
    def __init__(self, manager):
        Thread.__init__(self)
        self.done = False
        self.progress = 0
        self.n = 0
        self.bar = tqdm(total=100, file=sys.stdout, bar_format='{l_bar}{bar}| {postfix}', postfix=f'{manager.getNumberOfFragments()} Fragments , In Process ')
        self.manager = manager
        self.numberOfFragments = manager.getNumberOfFragments()
        self.numberOfNodes = manager.getNumberOfNodes()

    def stop(self):
        self.done = True

    def map(self):
        self.numberOfFragments = self.manager.getNumberOfFragments()
        return int(100 * (self.numberOfNodes - self.numberOfFragments) / self.numberOfNodes)

    def update(self):
        self.n = (self.n + 1) % 5
        newProgress = self.map()
        self.bar.set_postfix_str(f'{self.numberOfFragments} Fragments , In Process ' + self.n * '.', True)

        if newProgress != self.progress:
            self.bar.update(newProgress - self.progress)
            self.progress = newProgress

    def run(self):
        while not self.done:
            sleep(0.1)
            self.update()

        self.bar.postfix = 'MST Created!'
        self.bar.update(100 - self.progress)
