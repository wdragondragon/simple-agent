from enum import Enum


class State(Enum):
    INIT = 0
    THINK = 1
    ACT = 2
    OBSERVE = 3
    FINISH = 4
