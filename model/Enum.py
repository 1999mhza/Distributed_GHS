from enum import Enum


class EdgeState(str, Enum):
    Rejected = 'Rejected'
    Branch = 'Branch'
    Basic = 'Basic'


class NodeState(str, Enum):
    Sleeping = 'Sleeping'
    Find = 'Find'
    Found = 'Found'


class Messagetype(str, Enum):
    Reject = 'Reject'
    Accept = 'Accept'
    Test = 'Test'
    Initiate = 'Initiate'
    Connect = 'Connect'
    Report = 'Report'
    ChangeCore = 'ChangeCore'
