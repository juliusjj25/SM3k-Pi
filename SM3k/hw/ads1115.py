import time
from typing import Dict, List, Tuple

try:
    import board, busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
except Exception:
    board = busio = ADS = AnalogIn = None  # allows mock on dev PCs

class ADSReader:
    """Manages one or more ADS1115s; returns per-channel voltages."""
    def __init__(self, configs: List[Tuple[int, List[str]]], vref: float = 3.3):
        self.vref = vref
        self._maps: Dict[str, AnalogIn] = {}
        if board is None:
            self._mock = True
            self._t0 = time.monotonic()
            return
        self._mock = False
        i2c = busio.I2C(board.SCL, board.SDA)
        for cfg in configs:
            addr, names = cfg
            ads = ADS.ADS1115(i2c, address=addr)
            ads.gain = 1  # ±4.096 V full scale (safe for 0–3.3V nodes)
            chans = [ADS.P0, ADS.P1, ADS.P2, ADS.P3]
            for name, ch in zip(names, chans):
                self._maps[name] = AnalogIn(ads, ch)

    def read_volts(self) -> Dict[str, float]:
        if self._mock:
            # generate stable but changing values for dev
            t = time.monotonic() - self._t0
            return {"chamber": 1.65 + 0.1*__import__("math").sin(t/30.0)}
        return {name: ain.voltage for name, ain in self._maps.items()}
