import logging
from threading import Lock
from time import time


logging.basicConfig(format='%(message)s', filename="../result/GHS.log", level=logging.INFO, filemode='w')
lock = Lock()
def log(time, string):
    with lock:
        logging.info(f'{time:03.3f}) {string}')


class Channel:
    def __init__(self, node):
        self.node = node
        self.times = []
        self.messages = []
        self.mutex = Lock()

    def search(self, left, right, receiveTime):

        while right > left + 1:
            middle = (right + left) // 2

            if receiveTime >= self.times[middle - 1]:
                left = middle
            else:
                right = middle

        if right == left + 1 and receiveTime >= self.times[left]:
            return right

        return left

    def addToQueue(self, receiveTime, message, new=True):
        self.mutex.acquire()

        index = self.search(0, len(self.times), receiveTime)
        self.times.insert(index, receiveTime)
        self.messages.insert(index, message)

        self.mutex.release()

        if new:
            self.node.increaseMessage(message.getSize())
            log((time() - self.node.getTime()), f"node {self.node.getId()} {message}")

    def getMessage(self):

        if len(self.times) > 0 and self.times[0] <= time():
            self.mutex.acquire()
            message = self.messages.pop(0)
            self.times.pop(0)
            self.mutex.release()
            return message

        return None
