from enum import Enum


class GlobalState(Enum):
    IDLE = 0
    FETCHING = 1
    FINISHED = 2

    def __and__(self, other):
        return self.value & other.value

    def __or__(self, other):
        return self.value | other.value

    def __xor__(self, other):
        return self.value ^ other.value

    def __invert__(self):
        return ~self.value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value
