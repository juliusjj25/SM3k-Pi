import time
from collections import deque, defaultdict

class Rollup:
    def __init__(self, period_s=60):
        self.period = period_s
        self.buf = defaultdict(lambda: deque())

    def add(self, readings: dict):
        now = time.time()
        for k,v in readings.items():
            self.buf[k].append((now,v))
        # prune
        for k,dq in self.buf.items():
            while dq and (now - dq[0][0]) > self.period:
                dq.popleft()

    def averages(self):
        out = {}
        for k,dq in self.buf.items():
            if dq:
                out[k] = sum(v for _,v in dq)/len(dq)
            else:
                out[k] = float("nan")
        return out
