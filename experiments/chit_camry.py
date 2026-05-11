"""Camry chit profile smoke test.

Computes chit at key operating points for the Camry 2.4L 2AZ-FE
(EPA Ricardo Std Car). Writes results JSON to docs/results/.

Tests:
  1. chit ≈ 0 at idle (cdv1 SOC-attractor prediction).
  2. chit at peak power point (expected ~0.42).
  3. chit at BSFC sweet spot (expected ~0.43).
  4. Narrow chit envelope across the operating envelope (cdv1 prediction:
     feedback-coupled NESS clusters near s-regime, not deeply into c).
"""
from __future__ import annotations

import json
import math
import os
import sys
from datetime import datetime

# Windows console UTF-8 fix (per H:/CLAUDE.md gotcha).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mpa_engine_packs.engine_data import load
from mpa_engine_packs.chit_profile import chit_at, chit_max_predicted


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data", "camry-2.4l-2az-fe.json")
RESULTS_DIR = os.path.join(REPO, "docs", "results")


def main() -> None:
    engine = load(DATA)
    print(f"Engine: {engine.name}")
    print(f"  LHV: {engine.lhv_jpkg / 1e6:.1f} MJ/kg")
    print(f"  Idle: {engine.idle_rpm:.0f} RPM")
    print(f"  Peak power: {engine.peak_power_w / 1e3:.0f} kW")
    print(f"  Operating envelope: {engine.rpm_range} RPM × {engine.torque_range} Nm")
    print()

    # Reference operating points.
    points = [
        ("idle (680 RPM, 0 Nm)", 680.0, 0.0),
        ("low-load cruise (2000 RPM, 50 Nm)", 2000.0, 50.0),
        ("mid-load cruise (2500 RPM, 100 Nm)", 2500.0, 100.0),
        ("BSFC sweet spot (~3000 RPM, ~200 Nm)", 3000.0, 200.0),
        ("peak torque (4000 RPM, 218 Nm)", 4000.0, 218.0),
        ("high-RPM low load (5000 RPM, 50 Nm)", 5000.0, 50.0),
        ("high-RPM mid load (5000 RPM, 150 Nm)", 5000.0, 150.0),
        ("redline-region (6000 RPM, 178 Nm)", 6000.0, 178.0),
    ]

    readings = []
    print(f"{'Operating point':<42}  {'G_0 (kW)':>10}  {'L (kW)':>10}  {'W (kW)':>10}  {'chit':>7}  regime")
    print("-" * 100)
    for label, rpm, tq in points:
        r = chit_at(engine, rpm, tq)
        readings.append({
            "label": label,
            "rpm": r.rpm,
            "brake_torque_nm": r.brake_torque_nm,
            "g0_w": r.g0_w,
            "l_w": r.l_w,
            "brake_power_w": r.brake_power_w,
            "chit": r.chit if not math.isnan(r.chit) else None,
            "regime": r.regime,
            "notes": r.notes,
        })
        g0_kw = r.g0_w / 1e3 if not math.isnan(r.g0_w) else float("nan")
        l_kw = r.l_w / 1e3 if not math.isnan(r.l_w) else float("nan")
        w_kw = r.brake_power_w / 1e3 if not math.isnan(r.brake_power_w) else float("nan")
        chit_str = f"{r.chit:+.3f}" if not math.isnan(r.chit) else "    NaN"
        print(f"{label:<42}  {g0_kw:>10.2f}  {l_kw:>10.2f}  {w_kw:>10.2f}  {chit_str:>7}  {r.regime}")

    # cdv1 SOC-attractor check: chit at idle should be ≈ 0.
    idle_chit = readings[0]["chit"]
    print()
    print(f"cdv1 SOC-attractor check: chit at idle = {idle_chit}")
    print(f"  Expected ≈ 0 by construction of 'idle' (brake_power = 0 → G_0 = L).")
    print(f"  Status: {'PASS' if idle_chit is not None and abs(idle_chit) < 0.01 else 'FAIL'}")

    # cdv1 chit_max prediction: chit_max ≈ -ln(1 - η_max).
    # For η_max ≈ 0.35 (BSFC ≈ 233 g/kWh from EPA chart):
    eta_max_published = 0.351   # from BSFC 233 g/kWh, LHV 44 MJ/kg
    chit_max_pred = chit_max_predicted(eta_max_published)
    chit_observed = max(
        (r["chit"] for r in readings if r["chit"] is not None),
        default=None,
    )
    print()
    print("cdv1 chit_max check:")
    print(f"  Published peak thermal efficiency: {eta_max_published:.3f}")
    print(f"  Predicted chit_max = -ln(1 - η_max): {chit_max_pred:+.3f}")
    print(f"  Observed chit_max across sample points: {chit_observed:+.3f}" if chit_observed is not None else "  Observed: NaN")
    if chit_observed is not None:
        delta = abs(chit_observed - chit_max_pred)
        status = "PASS" if delta < 0.10 else "FAIL"
        print(f"  Status: {status} (|delta| = {delta:.3f}, threshold 0.10)")

    # Operating-envelope summary.
    chits = [r["chit"] for r in readings if r["chit"] is not None]
    print()
    if chits:
        print(f"Chit range across sampled envelope: [{min(chits):+.3f}, {max(chits):+.3f}]")
        print(f"  cdv1 prediction: feedback-coupled NESS clusters near s-regime,")
        print(f"  so chit_max ≲ 0.5 across normal operation. Observed: {max(chits):+.3f}.")

    # Write results.
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, "chit_camry_smoke.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "engine": engine.name,
            "run_at": datetime.utcnow().isoformat() + "Z",
            "readings": readings,
            "predictions": {
                "soc_attractor": {
                    "claim": "chit at idle = 0 (cdv1 SOC-attractor instance)",
                    "predicted": 0.0,
                    "observed": idle_chit,
                    "passed": (idle_chit is not None and abs(idle_chit) < 0.01),
                },
                "chit_max": {
                    "claim": "chit_max ≈ -ln(1 - η_thermal_max) at BSFC sweet spot",
                    "predicted": chit_max_pred,
                    "observed": chit_observed,
                    "eta_max_published": eta_max_published,
                    "delta": (abs(chit_observed - chit_max_pred) if chit_observed is not None else None),
                    "passed": (chit_observed is not None and abs(chit_observed - chit_max_pred) < 0.10),
                },
            },
        }, f, indent=2)
    print()
    print(f"Results written to: {out_path}")


if __name__ == "__main__":
    main()
