from dataclasses import dataclass
import time

@dataclass
class PID:
    kp: float
    ki: float
    kd: float
    out_min: float = 0.0
    out_max: float = 1.0

    _i: float = 0.0
    _last_err: float = 0.0
    _last_t: float = time.monotonic()

    def step(self, sp: float, pv: float) -> float:
        now = time.monotonic()
        dt = max(1e-3, now - self._last_t)
        self._last_t = now
        err = sp - pv
        p = self.kp * err
        self._i += self.ki * err * dt
        self._i = max(self.out_min, min(self._i, self.out_max))  # anti-windup
        d = self.kd * (err - self._last_err) / dt
        self._last_err = err
        out = p + self._i + d
        return max(self.out_min, min(out, self.out_max))
