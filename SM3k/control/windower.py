import time

class WindowPWM:
    """Time-proportioning window for SSRs (e.g., 8 s window)."""
    def __init__(self, window_s: float):
        self.window = float(window_s)
        self._t0 = time.monotonic()

    def update(self, duty_0_1: float) -> bool:
        """Return True => SSR ON, False => OFF."""
        duty = max(0.0, min(1.0, float(duty_0_1)))
        now = time.monotonic()
        if (now - self._t0) >= self.window:
            # slide window forward (avoid drift by +window, not =now)
            self._t0 += self.window
        on_time = duty * self.window
        return (now - self._t0) < on_time
