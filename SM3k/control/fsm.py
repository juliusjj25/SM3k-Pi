from enum import Enum, auto
from dataclasses import dataclass

class State(Enum):
    LOCKOUT = auto()
    IDLE    = auto()
    HEAT    = auto()
    ALARM   = auto()

@dataclass
class Context:
    setpoint_f: float
    max_safe_f: float
    armed: bool = False

def next_state(st: State, ctx: Context, chamber_f: float, probe_ok: bool) -> State:
    if not probe_ok or (chamber_f != chamber_f): # NaN check
        return State.LOCKOUT
    if chamber_f > ctx.max_safe_f:
        return State.ALARM
    if st in (State.LOCKOUT, State.ALARM):
        return State.IDLE if ctx.armed else State.LOCKOUT
    if st == State.IDLE:
        return State.HEAT if chamber_f < (ctx.setpoint_f - 2.0) else State.IDLE
    if st == State.HEAT:
        return State.IDLE if chamber_f >= ctx.setpoint_f else State.HEAT
    return State.IDLE
