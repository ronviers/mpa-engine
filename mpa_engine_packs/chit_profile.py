"""cdv1 chit reading on engine substrate data.

chit = ln(G_0 / L), where for an engine on a brake dynamometer:
    G_0 = fuel_rate(rpm, brake_torque) * LHV       [combustion energy rate, W]
    W   = brake_torque * omega                     [brake power, W]
    L   = G_0 - W                                  [losses, W]

At idle, brake_torque = 0 by definition, so W = 0 and L = G_0 → chit = 0 exactly.
This is the cdv1 §Pattern formation SOC-attractor prediction's instance on
feedback-controlled NESS substrates.

cdv1 regimes apply to the *driving* register (brake_torque ≥ 0). The motoring
region (brake_torque < 0) is the engine being driven by the dyno, distinct
from cdv1's c/s/r regime structure; chit on the motoring side is not the
same quantity.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np

from .engine_data import EngineData


@dataclass(frozen=True)
class ChitReading:
    """A cdv1 chit reading at one (rpm, brake_torque) operating point."""

    rpm: float
    brake_torque_nm: float
    brake_power_w: float
    g0_w: float
    l_w: float
    chit: float
    regime: str   # "c" | "s" | "r" | "out_of_gamut_motoring" | "out_of_gamut_high" | "out_of_gamut_low_rpm"
    notes: Optional[str] = None


def _omega_radps(rpm: float) -> float:
    return rpm * 2.0 * math.pi / 60.0


def chit_at(
    engine: EngineData,
    rpm: float,
    brake_torque_nm: float,
    *,
    s_band: float = 0.05,
) -> ChitReading:
    """Compute the cdv1 chit reading at (rpm, brake_torque) for an engine.

    s_band: regime classification width. |chit| < s_band → s-regime;
    chit > s_band → c-regime; chit < -s_band → r-regime.

    Out-of-gamut returns (NaN, NaN, NaN, NaN) with a regime tag explaining why.
    """
    # Gamut checks first.
    rpm_min, rpm_max = engine.rpm_range
    if rpm < rpm_min or rpm > rpm_max:
        return ChitReading(
            rpm=rpm, brake_torque_nm=brake_torque_nm,
            brake_power_w=float("nan"), g0_w=float("nan"),
            l_w=float("nan"), chit=float("nan"),
            regime="out_of_gamut_rpm",
            notes=f"RPM {rpm} outside grid [{rpm_min}, {rpm_max}]",
        )
    if brake_torque_nm < 0:
        # Motoring region: outside cdv1's driving register.
        # We still compute G_0 and a "chit-like" number but tag as out-of-gamut.
        fuel_gps = engine.fuel_rate_gps(rpm, brake_torque_nm)
        omega = _omega_radps(rpm)
        brake_power = brake_torque_nm * omega   # negative (energy IN to engine)
        g0 = fuel_gps * 1e-3 * engine.lhv_jpkg  # g/s → kg/s → J/s
        return ChitReading(
            rpm=rpm, brake_torque_nm=brake_torque_nm,
            brake_power_w=brake_power, g0_w=g0,
            l_w=float("nan"), chit=float("nan"),
            regime="out_of_gamut_motoring",
            notes="Driven (motoring) operating point. cdv1 c/s/r regimes apply only to driving register.",
        )

    # WOT envelope check.
    try:
        wot = engine.wot_torque_nm(rpm)
        if not math.isnan(wot) and brake_torque_nm > wot * 1.02:
            return ChitReading(
                rpm=rpm, brake_torque_nm=brake_torque_nm,
                brake_power_w=float("nan"), g0_w=float("nan"),
                l_w=float("nan"), chit=float("nan"),
                regime="out_of_gamut_high",
                notes=f"Torque {brake_torque_nm} Nm > WOT envelope {wot:.1f} Nm at {rpm} RPM",
            )
    except Exception:
        pass

    # In-gamut: compute chit.
    fuel_gps = engine.fuel_rate_gps(rpm, brake_torque_nm)
    omega = _omega_radps(rpm)
    brake_power = brake_torque_nm * omega  # W
    g0 = fuel_gps * 1e-3 * engine.lhv_jpkg  # g/s → kg/s → J/s

    if math.isnan(g0) or g0 <= 0:
        return ChitReading(
            rpm=rpm, brake_torque_nm=brake_torque_nm,
            brake_power_w=brake_power, g0_w=g0,
            l_w=float("nan"), chit=float("nan"),
            regime="out_of_gamut_no_fuel",
            notes="Fuel rate zero or NaN (EPA boundary artifact: low-RPM/high-motoring corner).",
        )

    # Standard chit calculation.
    if brake_power <= 0:
        # Idle / no load — chit = 0 exactly.
        chit = 0.0
        l_w = g0
    else:
        l_w = g0 - brake_power
        if l_w <= 0:
            # Physically impossible (would require >100% efficiency)
            return ChitReading(
                rpm=rpm, brake_torque_nm=brake_torque_nm,
                brake_power_w=brake_power, g0_w=g0,
                l_w=l_w, chit=float("nan"),
                regime="out_of_gamut_overunity",
                notes="L ≤ 0: brake_power exceeds fuel energy. Interpolation artifact or impossible point.",
            )
        chit = math.log(g0 / l_w)

    # Regime classification.
    if chit > s_band:
        regime = "c"
    elif chit < -s_band:
        regime = "r"
    else:
        regime = "s"

    return ChitReading(
        rpm=rpm, brake_torque_nm=brake_torque_nm,
        brake_power_w=brake_power, g0_w=g0,
        l_w=l_w, chit=chit, regime=regime,
    )


def chit_grid(
    engine: EngineData,
    rpm_axis: np.ndarray,
    torque_axis: np.ndarray,
    *,
    s_band: float = 0.05,
) -> dict[str, np.ndarray]:
    """Compute chit on a grid for plotting. Returns dict with chit, regime_int, g0, l."""
    chit = np.full((len(torque_axis), len(rpm_axis)), np.nan)
    regime_int = np.full((len(torque_axis), len(rpm_axis)), -1, dtype=int)
    # regime_int legend: 0=r, 1=s, 2=c, -1=out-of-gamut, -2=motoring
    g0 = np.full_like(chit, np.nan)
    l_arr = np.full_like(chit, np.nan)

    for i, tq in enumerate(torque_axis):
        for j, r in enumerate(rpm_axis):
            reading = chit_at(engine, float(r), float(tq), s_band=s_band)
            chit[i, j] = reading.chit
            g0[i, j] = reading.g0_w
            l_arr[i, j] = reading.l_w
            if reading.regime == "c":
                regime_int[i, j] = 2
            elif reading.regime == "s":
                regime_int[i, j] = 1
            elif reading.regime == "r":
                regime_int[i, j] = 0
            elif reading.regime == "out_of_gamut_motoring":
                regime_int[i, j] = -2
            # other out-of-gamut tags stay at -1

    return {"chit": chit, "regime_int": regime_int, "g0_w": g0, "l_w": l_arr}


def chit_max_predicted(thermal_efficiency_max: float) -> float:
    """cdv1 prediction: chit_max ≈ -ln(1 - η_max) at the BSFC sweet spot.

    Derived from W/G_0 = η, L/G_0 = 1 - η, chit = ln(G_0/L) = -ln(1 - η).
    """
    return -math.log(1.0 - thermal_efficiency_max)


__all__ = ["ChitReading", "chit_at", "chit_grid", "chit_max_predicted"]
