import os
try:
    from gpiozero import OutputDevice
except Exception:
    OutputDevice = None

class SSR:
    def __init__(self, pin_bcm: int):
        if OutputDevice is None:
            self._mock = True
            self.state = False
        else:
            self._mock = False
            self._dev = OutputDevice(pin_bcm, active_high=True, initial_value=False)

    def on(self):
        self.state = True
        if not self._mock: self._dev.on()

    def off(self):
        self.state = False
        if not self._mock: self._dev.off()
