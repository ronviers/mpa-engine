"""Camry visualization — Track 1 of the mpa-view duo.

Renders four panels to docs/results/:
  1. BSFC contour map (substrate-native).
  2. chit profile across the operating envelope (canonical cdv1 reading).
  3. Operating envelope outlined (WOT + motoring curves, idle marked).
  4. chit-vs-brake-power at peak torque RPM (regime walk).

Matplotlib only. No live server, no MCP plumbing — just images.
"""
from __future__ import annotations

import os
import sys

# Windows console UTF-8 fix (per H:/CLAUDE.md gotcha).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

from mpa_engine_packs.engine_data import load
from mpa_engine_packs.chit_profile import chit_grid


REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(REPO, "data", "camry-2.4l-2az-fe.json")
RESULTS_DIR = os.path.join(REPO, "docs", "results")


def main() -> None:
    engine = load(DATA)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # ── Grids ────────────────────────────────────────────────────────────
    rpm_grid = np.array(engine.raw["fuel_map"]["rpm_grid"], dtype=float)
    torque_grid = np.array(engine.raw["fuel_map"]["torque_Nm_grid"], dtype=float)
    fuel_rate = np.array(engine.raw["fuel_map"]["fuel_rate_gps"], dtype=float)

    # BSFC = fuel_rate / brake_power. Singular at brake_torque = 0.
    omega = rpm_grid * 2 * np.pi / 60.0  # rad/s
    # BSFC has units g/(kW·h) — convert:
    # fuel_rate [g/s] / brake_power [kW] = fuel_rate [g/s] / (T * omega / 1000) [kW]
    # then × 3600 to get g/(kW·h)
    T_grid, R_grid = np.meshgrid(torque_grid, rpm_grid, indexing="ij")
    Omega_grid = R_grid * 2 * np.pi / 60.0
    brake_power_kw = T_grid * Omega_grid / 1000.0
    bsfc = np.where(brake_power_kw > 0, fuel_rate * 3600.0 / brake_power_kw, np.nan)

    # ── Panel 1: BSFC contour (substrate-native) ─────────────────────────
    fig, ax = plt.subplots(figsize=(9, 6))
    bsfc_clip = np.clip(bsfc, 200, 800)  # clip extreme values for readability
    levels = [210, 220, 230, 240, 250, 260, 275, 290, 310, 330, 360, 400, 450, 500, 600, 800]
    cs = ax.contour(R_grid, T_grid, bsfc_clip, levels=levels, cmap="viridis")
    ax.clabel(cs, inline=True, fontsize=8, fmt="%.0f")
    cf = ax.contourf(R_grid, T_grid, bsfc_clip, levels=levels, cmap="viridis", alpha=0.3)
    fig.colorbar(cf, ax=ax, label="BSFC (g/kWh) — lower is better")

    # Overlay WOT + motoring curves.
    wot_rpms = np.array([p["rpm"] for p in engine.raw["wot_curve"]])
    wot_torques = np.array([p["torque_Nm"] for p in engine.raw["wot_curve"]])
    ax.plot(wot_rpms, wot_torques, "k-", lw=2, label="WOT envelope")

    mot_rpms = np.array([p["rpm"] for p in engine.raw["motoring_curve"]])
    mot_torques = np.array([p["torque_Nm"] for p in engine.raw["motoring_curve"]])
    ax.plot(mot_rpms, mot_torques, "k--", lw=1.5, label="Motoring (L)")

    # Idle point.
    ax.plot(engine.idle_rpm, 0, "r*", markersize=20, label=f"Idle (680 RPM)")
    # Peak BSFC point (rough).
    ax.plot(3000, 200, "ms", markersize=12, label="BSFC sweet spot (~233 g/kWh)")

    ax.set_xlabel("Engine speed (RPM)")
    ax.set_ylabel("Brake torque (Nm)")
    ax.set_title(f"{engine.name} — substrate-native BSFC contour")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "01_bsfc_contour.png"), dpi=110)
    plt.close(fig)
    print(f"Wrote 01_bsfc_contour.png")

    # ── Panel 2: chit profile (canonical cdv1 reading) ───────────────────
    # Restrict to driving region (torque >= 0).
    driving_torque = torque_grid[torque_grid >= 0]
    rpm_eval = rpm_grid[rpm_grid >= 600]  # below 600 RPM the EPA grid is artifactual

    grid = chit_grid(engine, rpm_eval, driving_torque)
    chit = grid["chit"]

    fig, ax = plt.subplots(figsize=(9, 6))
    T_eval, R_eval = np.meshgrid(driving_torque, rpm_eval, indexing="ij")
    chit_levels = np.arange(0, 0.55, 0.05)
    cs = ax.contour(R_eval, T_eval, chit, levels=chit_levels, cmap="plasma")
    ax.clabel(cs, inline=True, fontsize=9, fmt="%.2f")
    cf = ax.contourf(R_eval, T_eval, chit, levels=chit_levels, cmap="plasma", alpha=0.4)
    fig.colorbar(cf, ax=ax, label="chit = ln(G₀/L)  (cdv1 canonical)")

    # Mark regime boundaries via shading.
    # s-regime ≈ chit < 0.05; c-regime ≈ chit > 0.05.
    ax.contour(R_eval, T_eval, chit, levels=[0.05], colors=["white"], linewidths=2, linestyles="--")

    # Overlay WOT + motoring.
    ax.plot(wot_rpms, wot_torques, "k-", lw=2, label="WOT envelope")
    ax.axhline(0, color="white", linestyle=":", lw=1.5, label="Idle locus (chit=0, s-regime)")
    ax.plot(engine.idle_rpm, 0, "r*", markersize=20, label="Designed idle")

    ax.set_xlabel("Engine speed (RPM)")
    ax.set_ylabel("Brake torque (Nm)")
    ax.set_title(f"{engine.name} — cdv1 chit profile (canonical reading)")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "02_chit_profile.png"), dpi=110)
    plt.close(fig)
    print(f"Wrote 02_chit_profile.png")

    # ── Panel 3: Operating envelope, regime overlay ──────────────────────
    fig, ax = plt.subplots(figsize=(9, 6))
    # Regime int legend: 0=r, 1=s, 2=c, -1=oog, -2=motoring
    # Color: r=gray, s=yellow, c=cornflower, motoring=lavender
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cmap = ListedColormap([
        "#e0d4f0",  # -2 motoring
        "#cccccc",  # -1 oog
        "#dddddd",  # 0 r (not really expected in driving)
        "#fff2a8",  # 1 s
        "#a8c8f0",  # 2 c
    ])
    norm = BoundaryNorm([-2.5, -1.5, -0.5, 0.5, 1.5, 2.5], cmap.N)

    # Full envelope including motoring.
    full_grid = chit_grid(engine, rpm_grid, torque_grid)
    ax.imshow(
        full_grid["regime_int"],
        origin="lower",
        extent=[rpm_grid[0], rpm_grid[-1], torque_grid[0], torque_grid[-1]],
        aspect="auto",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
    )

    ax.plot(wot_rpms, wot_torques, "k-", lw=2, label="WOT envelope")
    ax.plot(mot_rpms, mot_torques, "k--", lw=1.5, label="Motoring")
    ax.axhline(0, color="red", linestyle=":", lw=1.5, alpha=0.6)
    ax.plot(engine.idle_rpm, 0, "r*", markersize=20, label="Idle")

    # Custom legend for regime colors.
    from matplotlib.patches import Patch
    legend_patches = [
        Patch(facecolor="#a8c8f0", label="c-regime (chit > 0.05)"),
        Patch(facecolor="#fff2a8", label="s-regime (|chit| < 0.05) — SOC attractor"),
        Patch(facecolor="#e0d4f0", label="motoring (out of cdv1 driving register)"),
    ]
    ax.legend(handles=legend_patches + [
        plt.Line2D([0], [0], color="k", lw=2, label="WOT"),
        plt.Line2D([0], [0], color="k", lw=1.5, ls="--", label="Motoring T"),
        plt.Line2D([0], [0], marker="*", color="w", markerfacecolor="r", markersize=15, label="Idle", linestyle=""),
    ], loc="upper right", fontsize=9)

    ax.set_xlabel("Engine speed (RPM)")
    ax.set_ylabel("Brake torque (Nm)")
    ax.set_title(f"{engine.name} — regime map (cdv1 c/s/r over operating envelope)")
    ax.grid(True, alpha=0.3, color="black")
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "03_regime_map.png"), dpi=110)
    plt.close(fig)
    print(f"Wrote 03_regime_map.png")

    # ── Panel 4: chit-vs-brake-power at peak-torque RPM (regime walk) ─────
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Sweep brake torque at 4000 RPM from 0 to WOT.
    rpm_sweep = 4000.0
    torque_sweep = np.linspace(0, 218, 80)
    chit_sweep = []
    for tq in torque_sweep:
        grid_pt = chit_grid(engine, np.array([rpm_sweep]), np.array([tq]))
        chit_sweep.append(grid_pt["chit"][0, 0])
    chit_sweep = np.array(chit_sweep)
    brake_power_sweep = torque_sweep * rpm_sweep * 2 * np.pi / 60.0 / 1000.0  # kW

    ax1.plot(brake_power_sweep, chit_sweep, "b-", lw=2)
    ax1.axhline(0, color="red", linestyle=":", label="chit = 0 (s-regime / SOC attractor)")
    ax1.axhline(0.05, color="orange", linestyle=":", alpha=0.5, label="s → c boundary (s_band = 0.05)")
    ax1.set_xlabel(f"Brake power (kW) at {rpm_sweep:.0f} RPM")
    ax1.set_ylabel("chit = ln(G₀/L)")
    ax1.set_title("Regime walk: chit vs brake power at peak-torque RPM")
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # Sweep RPM at fixed brake torque (50% WOT).
    rpm_axis = np.linspace(800, 6500, 60)
    chit_walk = []
    for r in rpm_axis:
        grid_pt = chit_grid(engine, np.array([r]), np.array([100.0]))
        chit_walk.append(grid_pt["chit"][0, 0])
    ax2.plot(rpm_axis, chit_walk, "g-", lw=2, label="100 Nm")
    chit_walk2 = []
    for r in rpm_axis:
        grid_pt = chit_grid(engine, np.array([r]), np.array([200.0]))
        chit_walk2.append(grid_pt["chit"][0, 0])
    ax2.plot(rpm_axis, chit_walk2, "m-", lw=2, label="200 Nm (near WOT)")
    ax2.axhline(0, color="red", linestyle=":", label="chit = 0 (idle locus)")
    ax2.set_xlabel("Engine speed (RPM)")
    ax2.set_ylabel("chit = ln(G₀/L)")
    ax2.set_title("Regime walk: chit vs RPM at fixed brake torque")
    ax2.grid(True, alpha=0.3)
    ax2.legend()

    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS_DIR, "04_regime_walks.png"), dpi=110)
    plt.close(fig)
    print(f"Wrote 04_regime_walks.png")

    print()
    print(f"All panels in: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
