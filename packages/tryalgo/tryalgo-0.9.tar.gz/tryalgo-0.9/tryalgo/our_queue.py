#!/usr/bin/env python3
# A FIFO queue
# christoph dürr - jill-jênn vie - 2015

from random import randint
from collections import deque


# snip{ OurQueue
class OurQueue:
    """A FIFO queue

    Complexity:
        all operators in amortized constant time,
        except __str__ which is linear
    """
    def __init__(self):
        self.in_stack = []        # la queue
        self.out_stack = []       # la tête

    def __len__(self):
        return len(self.in_stack) + len(self.out_stack)

    def push(self, obj):
        self.in_stack.append(obj)


    def pop(self):
        if not self.out_stack:    # la tête est vide
            self.out_stack = self.in_stack[::-1]
            self.in_stack = []
        return self.out_stack.pop()
    # snip}

    def __str__(self):
        return str(self.out_stack[::-1] + self.in_stack)

if __name__ == "__main__":
    q1 = deque()
    q2 = OurQueue()
    for _ in range(10000):
        assert (q1 and not q2.is_empty()) or (not q1 and q2.is_empty())
        if randint(0, 2) == 0:
            x = randint(0, 100)
            q1.append(x)
            q2.push(x)
        else:
            if q1:
                assert q1.popleft() == q2.pop()
