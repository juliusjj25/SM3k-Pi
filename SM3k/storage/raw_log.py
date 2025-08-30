import csv, time, os

class RawLogger:
    def __init__(self, path="smoker_raw.csv"):
        self.path = path
        self._fh = None
        self._writer = None

    def _ensure(self, fieldnames):
        if self._fh: return
        new = not os.path.exists(self.path)
        self._fh = open(self.path,"a",newline="")
        self._writer = csv.DictWriter(self._fh, fieldnames=["ts"]+fieldnames)
        if new:
            self._writer.writeheader()

    def write(self, data: dict):
        """data: {'chamber':225.3,'meat1':148.7,...}"""
        self._ensure(list(data.keys()))
        row = {"ts": time.time(), **data}
        self._writer.writerow(row)
        self._fh.flush()
