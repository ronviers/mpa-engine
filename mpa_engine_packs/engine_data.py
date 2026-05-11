"""Loaders + interpolation for engine substrate data.

Reads the substrate-conditional JSON produced from EPA / SAE / OEM sources
and returns interpolators for the BSFC map, WOT curve, and motoring curve.

The substrate-class is fixed at "four-stroke spark-ignition IC engine on
brake dynamometer"; per-engine specifics (displacement, fuel LHV, idle
RPM, map shape) come from the JSON.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.interpolate import RegularGridInterpolator, interp1d


@dataclass(frozen=True)
class EngineData:
    """A loaded engine characterization. Immutable after load."""

    raw: dict[str, Any]

    @property
    def name(self) -> str:
        return self.raw["engine"]["name"]

    @property
    def lhv_jpkg(self) -> float:
        """Fuel lower heating value in J/kg."""
        return self.raw["fuel"]["lhv_MJpkg"] * 1e6

    @property
    def idle_rpm(self) -> float:
        return self.raw["idle"]["rpm"]

    @property
    def peak_power_w(self) -> float:
        return self.raw["engine"]["peak_power_kW"] * 1e3

    @property
    def rpm_range(self) -> tuple[float, float]:
        """(min, max) RPM of the BSFC map grid."""
        grid = self.raw["fuel_map"]["rpm_grid"]
        return float(grid[0]), float(grid[-1])

    @property
    def torque_range(self) -> tuple[float, float]:
        """(min, max) torque-Nm of the BSFC map grid."""
        grid = self.raw["fuel_map"]["torque_Nm_grid"]
        return float(grid[0]), float(grid[-1])

    def fuel_rate_gps(self, rpm: float, torque_nm: float) -> float:
        """Interpolate fuel rate (g/s) at (rpm, torque). Out-of-grid returns NaN."""
        result = _fuel_rate_interp(self)(np.array([[torque_nm, rpm]]))
        return float(result[0])

    def wot_torque_nm(self, rpm: float) -> float:
        """Maximum torque at this RPM (the WOT envelope). NaN outside WOT range."""
        return float(_wot_interp(self)(rpm))

    def motoring_torque_nm(self, rpm: float) -> float:
        """Motoring (minimum) torque at this RPM — the engine's friction signature."""
        return float(_motoring_interp(self)(rpm))


# ── Internal: interpolator factories (cached on the EngineData instance) ──


_FUEL_INTERP_CACHE: dict[int, RegularGridInterpolator] = {}
_WOT_INTERP_CACHE: dict[int, Any] = {}
_MOT_INTERP_CACHE: dict[int, Any] = {}


def _fuel_rate_interp(engine: EngineData) -> RegularGridInterpolator:
    key = id(engine)
    cached = _FUEL_INTERP_CACHE.get(key)
    if cached is not None:
        return cached
    fmap = engine.raw["fuel_map"]
    torque_grid = np.asarray(fmap["torque_Nm_grid"], dtype=float)
    rpm_grid = np.asarray(fmap["rpm_grid"], dtype=float)
    rates = np.asarray(fmap["fuel_rate_gps"], dtype=float)
    # rates shape: (len(torque_grid), len(rpm_grid))
    interp = RegularGridInterpolator(
        (torque_grid, rpm_grid), rates, bounds_error=False, fill_value=np.nan
    )
    _FUEL_INTERP_CACHE[key] = interp
    return interp


def _wot_interp(engine: EngineData):
    key = id(engine)
    cached = _WOT_INTERP_CACHE.get(key)
    if cached is not None:
        return cached
    curve = engine.raw["wot_curve"]
    rpms = np.array([p["rpm"] for p in curve])
    torques = np.array([p["torque_Nm"] for p in curve])
    interp = interp1d(rpms, torques, bounds_error=False, fill_value=np.nan)
    _WOT_INTERP_CACHE[key] = interp
    return interp


def _motoring_interp(engine: EngineData):
    key = id(engine)
    cached = _MOT_INTERP_CACHE.get(key)
    if cached is not None:
        return cached
    curve = engine.raw["motoring_curve"]
    rpms = np.array([p["rpm"] for p in curve])
    torques = np.array([p["torque_Nm"] for p in curve])
    interp = interp1d(rpms, torques, bounds_error=False, fill_value=np.nan)
    _MOT_INTERP_CACHE[key] = interp
    return interp


# ── Loader ────────────────────────────────────────────────────────────────


def load(path: str) -> EngineData:
    """Load an engine characterization JSON from disk."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # Sanity checks: BSFC matrix shape matches grid sizes
    fmap = raw["fuel_map"]
    n_torque = len(fmap["torque_Nm_grid"])
    n_rpm = len(fmap["rpm_grid"])
    rates = fmap["fuel_rate_gps"]
    assert len(rates) == n_torque, (
        f"fuel_rate_gps has {len(rates)} rows, expected {n_torque} (torque_Nm_grid)"
    )
    for i, row in enumerate(rates):
        assert len(row) == n_rpm, (
            f"fuel_rate_gps row {i} has {len(row)} entries, expected {n_rpm} (rpm_grid)"
        )
    return EngineData(raw=raw)


__all__ = ["EngineData", "load"]
