import time
from smoker.config import load
from smoker.hw.ads1115 import ADSReader
from smoker.hw.thermistor import NTC
from smoker.hw.ssr import SSR
from smoker.control.pid import PID
from smoker.control.windower import WindowPWM
from smoker.control.fsm import State, Context, next_state
from smoker.util.logging import get_logger
import argparse, os
from smoker.config import load as load_cfg

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="smoker.yaml")
    ap.add_argument("--data", default="/var/lib/SM3k")
    return ap.parse_args()

def fahrenheit(c): return c*9/5 + 32

def main():
    args = parse_args()
    cfg = load_cfg(args.config)
    os.makedirs(args.data, exist_ok=True)

    # Hardware
    ads_cfg = [(a.addr, a.channels) for a in cfg.ads]
    ads = ADSReader(ads_cfg, vref=3.3)
    ntc = NTC(cfg.thermistor.r_fixed_ohm, cfg.thermistor.r25_ohm, cfg.thermistor.beta_k)
    ssr = SSR(cfg.gpio.ssr_pin)

    # Control
    pid = PID(kp=0.08, ki=0.005, kd=0.3)  # gentle starters; tune later
    win = WindowPWM(cfg.window_s)
    ctx = Context(setpoint_f=cfg.setpoint_f, max_safe_f=cfg.max_safe_f, armed=True)
    state = State.LOCKOUT

    last_pid = 0.0
    v_supply = 3.3  # if you later read 3V3 on a spare channel, update this dynamically

    log.info("Smoker controller started")
    while True:
        now = time.monotonic()

        # 1) Read sensors
        volts = ads.read_volts()  # {'chamber': V, 'meat1': V, ...}
        chamber_v = volts.get("chamber", float("nan"))
        chamber_f = ntc.temp_f_from_v(chamber_v, v_supply)
        probe_ok = chamber_f == chamber_f and -40.0 < chamber_f < 600.0

        # 2) State + PID @ ~1 Hz
        if now - last_pid >= cfg.sample_period_s:
            state = next_state(state, ctx, chamber_f, probe_ok)
            if state in (State.LOCKOUT, State.ALARM) or not probe_ok:
                duty = 0.0
            else:
                duty = pid.step(ctx.setpoint_f, chamber_f)
            last_pid = now

            log.info(f"st={state.name} T={chamber_f:6.1f}F SP={ctx.setpoint_f:.1f} duty={duty*100:5.1f}%")

        # 3) Windowed SSR (non-blocking)
        on = win.update(duty if probe_ok and state==State.HEAT else 0.0)
        ssr.on() if on else ssr.off()

        # 4) Tiny nap
        time.sleep(0.01)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
