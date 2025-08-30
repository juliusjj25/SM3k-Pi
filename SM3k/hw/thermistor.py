import math

class NTC:
    """Simple Beta model (good for 100k/3950 BBQ probes)."""
    def __init__(self, r_fixed_ohm: float, r25_ohm: float = 100_000.0, beta_k: float = 3950.0):
        self.Rf = float(r_fixed_ohm)
        self.R0 = float(r25_ohm)
        self.B  = float(beta_k)
        self.T0 = 25.0 + 273.15

    def r_from_divider(self, v_node: float, v_supply: float) -> float:
        if v_node <= 0.0 or v_node >= v_supply:  # open/short sanity
            return float("inf") if v_node>=v_supply else 0.0
        # divider: V = Vs * Rt/(Rf+Rt)  -> Rt = Rf * V/(Vs - V)
        return self.Rf * (v_node / (v_supply - v_node))

    def temp_c_from_r(self, R: float) -> float:
        if R <= 0.0 or not math.isfinite(R): return float("nan")
        invT = 1.0/self.T0 + (1.0/self.B)*math.log(R/self.R0)
        return (1.0/invT) - 273.15

    def temp_f_from_v(self, v_node: float, v_supply: float) -> float:
        R = self.r_from_divider(v_node, v_supply)
        c = self.temp_c_from_r(R)
        return c*9/5 + 32 if math.isfinite(c) else float("nan")
