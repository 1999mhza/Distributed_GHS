import math


class Message:
    def __init__(self, id, type, level=None, fragment=None, state=None):
        self.id = id
        self.type = type
        self.level = level
        self.fragment = fragment
        self.state = state

    def __str__(self):
        return f'received from node {self.id}: type={self.type}'\
               + (f' level={self.level}' if self.level else '')\
               + (f' fragment={self.fragment}' if self.fragment else '')\
               + (f' state={self.state}' if self.state else '')

    def getId(self):
        return self.id

    def getType(self):
        return self.type

    def getLevel(self):
        return self.level

    def getFragment(self):
        return self.fragment

    def getState(self):
        return self.state

    def getSize(self):
        id = 16
        type = 3
        level = int(math.log2(id))
        fragment = 32 + 2 * id
        state = 2
        return id + type + (level if self.level else 0) + (fragment if self.fragment else 0) + (state if self.state else 0)

