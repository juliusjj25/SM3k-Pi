from dataclasses import dataclass
from typing import List, Dict
import os, yaml

@dataclass
class ADSConfig:
    addr: int
    channels: List[str]  # names: ["chamber","meat1",...]

@dataclass
class ThermistorConfig:
    r_fixed_ohm: float = 100_000.0
    r25_ohm: float = 100_000.0
    beta_k: float = 3950.0

@dataclass
class GPIOConfig:
    ssr_pin: int = 17  # BCM

@dataclass
class Settings:
    sample_period_s: float = 1.0
    window_s: float = 8.0
    setpoint_f: float = 225.0
    max_safe_f: float = 325.0
    ads: List[ADSConfig] = None
    thermistor: ThermistorConfig = ThermistorConfig()
    gpio: GPIOConfig = GPIOConfig()

def load(path: str = "smoker.yaml") -> Settings:
    if not os.path.exists(path):
        # sensible defaults: 1 ADS at 0x48 with 4 channels
        return Settings(
            ads=[ADSConfig(addr=0x48, channels=["chamber","meat1","meat2","meat3"])]
        )
    with open(path, "r") as f:
        cfg = yaml.safe_load(f) or {}
    ads = [ADSConfig(addr=int(x["addr"],0) if isinstance(x["addr"],str) else x["addr"],
                     channels=x.get("channels",[]))
           for x in cfg.get("ads",[])]
    th = ThermistorConfig(**cfg.get("thermistor",{}))
    gp = GPIOConfig(**cfg.get("gpio",{}))
    return Settings(sample_period_s=cfg.get("sample_period_s",1.0),
                    window_s=cfg.get("window_s",8.0),
                    setpoint_f=cfg.get("setpoint_f",225.0),
                    max_safe_f=cfg.get("max_safe_f",325.0),
                    ads=ads or [ADSConfig(addr=0x48, channels=["chamber","meat1","meat2","meat3"])],
                    thermistor=th, gpio=gp)
