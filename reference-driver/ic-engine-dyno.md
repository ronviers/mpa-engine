# Reference driver — IC engine at dynamometer

**Substrate-class:** `ic-engine-gasoline-spark-ignition-4-stroke`
**Status:** v0.1 — first thin-RFC pass. One calibration record (Camry 2.4L 2AZ-FE) lands first; cross-engine fingerprint follows.
**Targets:** [cdv1 (compressed)](https://github.com/ronviers/mpa-atlas/blob/main/framework/cdv1_compressed.md), [v9 (compressed)](https://github.com/ronviers/mpa-atlas/blob/main/framework/v9_compressed.md).
**Shape:** [RFC-S §4 driver profile](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-S_Scale-Management.md#4-driver-profile).

---

## 1. Substrate-class declaration

A four-stroke spark-ignition internal-combustion engine, characterized at brake dynamometer. The coherence is sustained crankshaft rotation under load; combustion energy per cycle supplies G₀, friction + pumping + thermal losses constitute L. The substrate-class spans displacement, cylinder count, induction (naturally aspirated, turbo, supercharged), and fuel-system generation (carbureted, port-injected, direct-injected) — all read through the same cdv1 primitives. Specific engine instances declare their own gamut and amplitudes in per-engine calibration records.

## 2. Header

| Field | Value |
|---|---|
| `profile_version` | 0.1 |
| `target_rfc_versions` | RFC-S v0.2, RFC-C v0.2, cdv1 (compressed) |
| `substrate_class` | `ic-engine-gasoline-spark-ignition-4-stroke` |
| `characterization_date` | 2026-05-11 |
| `authority` | mpa-engine v0 scaffold |
| `validation_history` | none yet (first calibration record pending) |

## 3. Operating envelope

Substrate-class-conditional. Per-engine specifics declared in the calibration record.

- **RPM range:** [stall_RPM, redline_RPM]. Designed idle sits low in this range; cdv1 predicts it lands at chit ≈ 0 by SOC self-tuning of the engine's idle controller (ECU or, historically, carburetor adjustment).
- **Torque range:** [motoring_torque(RPM), WOT_torque(RPM)]. Motoring is negative (dyno drives engine); WOT is the maximum sustained torque the engine produces at full throttle.
- **Thermal envelope:** the engine has a coolant-temperature operating window outside which combustion quality drifts. Substrate-conditional; calibration records may declare a `thermal_state` field.

## 4. Gamut

| Axis | Substrate-declared content |
|---|---|
| Drive axis (G₀) | Fuel mass flow × LHV. Range: idle fuel rate to WOT fuel rate. Cessation point: throttle fully closed at zero RPM, fuel cut. |
| Loss axis (L) | Motoring torque × RPM + thermal losses. Range: zero (engine off) to motoring power at redline. |
| Observer scale τ_obs | Single combustion cycle (~2 crank revolutions for 4-stroke) to engine lifetime. Canonical τ_obs for cdv1 reading: averaging window over many cycles, sized to demand. |
| Reachable regimes | c (under load), s (idle), r (below stall). Engines never reach k_frust (single-mode). |
| Persistence depth | Limited — engines do not tower in the cdv1 §Heat-tax sense. The substrate is one-level. |

## 5. Translation field (substrate-native → canonical)

| Substrate-native observable | Canonical | Read |
|---|---|---|
| Crankshaft RPM | ρ (coherence amplitude) | Direct: RPM is the sustained-rotation amplitude. |
| Brake torque × RPM | Brake power | Direct: G₀ − L = brake power, so any two of (G₀, L, brake_power) give the third. |
| Fuel mass flow × LHV | G₀ | Multiplication by fuel LHV; LHV declared in calibration record. |
| Motoring torque × RPM | L (substrate-instrumented) | Direct measurement: drive engine without fuel, measure required torque. |
| Brake_power = 0 (idle) | chit = 0 | Tautological: G₀ = L when brake_power = 0. The non-tautological prediction is *that the ECU/carb chooses an idle RPM at which this holds*, which is the SOC-attractor claim. |

## 6. Intents

Per RFC-S §3, the five intents:

| Intent | Applies to engines? | Notes |
|---|---|---|
| I1 regime-preserving | yes | Cross-engine fingerprint reads chit-regime structure across many engines. |
| I2 drive-faithful | yes | Per-engine calibration records preserve exact G₀ and L at calibrated operating points. |
| I3 capacity-preserving | partial | Engines are single-mode; capacity dynamics (Erlang-B closure of cdv1 §Capacity) collapse to the trivial one-channel case. I3 is vacuous here unless multi-cylinder cross-saturation is read as a multi-mode kernel — open. |
| I4 persistence-preserving | N/A | Engines are one-level; no persistence tower. |
| I5 signature-preserving | open | gFDR signatures in idle stability and return-to-idle transients are the cross-engine universality test. Falsifier: substrate-class CK aging signature in well-tuned engine return-to-idle (cdv1 §Stability s-regime algebraic settling). Pending Priority 3 transient data. |

## 7. Reference outputs

Canonical test inputs and expected substrate responses, for round-trip validation:

- **Idle (brake_torque = 0):** chit = 0 exactly. Pass criterion: G₀(idle_RPM, 0) = L(idle_RPM, 0) within fuel-rate measurement uncertainty.
- **WOT at peak torque RPM:** chit = ln(fuel_rate × LHV / (fuel_rate × LHV − peak_brake_power)). For the Camry: chit ≈ 0.42.
- **Peak efficiency point:** chit ≈ ln(1/(1 − η_thermal,max)). For modern gasoline engines (η_max ≈ 0.35): chit ≈ 0.43.
- **Operating-envelope chit range:** [0, ~0.5] for normal automotive engines. Substrates outside this range (higher peak efficiency, e.g., Atkinson-cycle hybrids reaching ~0.45 efficiency) are gamut-edge cases worth flagging.

## 8. Metadata

Methodology: dyno data (steady-state mapping). Transient response (return-to-idle, idle stability) is a separate measurement modality and is recorded under a `transient_measurements` section in the calibration record when available.

Known limitations:
- Steady-state mapping does not give CK aging tails. Priority 3 (return-to-idle transients) addresses this gap.
- ECU controllers introduce closed-loop dynamics not visible in static dyno data. The "designed idle RPM" reflects the ECU's setpoint, not the open-loop equilibrium. cdv1 §Active modulation handles plant+controller decomposition; engines instance it.
- Modelled engines (Ricardo simulation) vs measured engines (physical bench data) may differ at fine scale. Calibration records declare which.

Versioning: v0.1 covers the Camry instance; v0.2 adds cross-engine fingerprint; v0.3 (or v1.0) lands transient signature data.

## Page-budget self-check

Target: ≤1 page per [thin-RFC discipline](https://github.com/ronviers/mpa-atlas/blob/main/CLAUDE.md). This driver profile runs ~2 pages. The growth past target is driven by the eight-section structure of RFC-S §4 and the substrate-class enumeration in §6 (intent applicability) and §7 (reference outputs). The first per-engine calibration record (Camry) will land at one page or less.

**Debt-marker:** §6 I3 ("partial") and §6 I5 ("open") are not yet resolved. I3 closes when we decide whether multi-cylinder cross-saturation reads as multi-mode (then I3 has content) or as one mode (then I3 is vacuous and the table simplifies). I5 closes when Priority 3 transient data lands or definitively doesn't. Revert condition: both intents resolve to clear yes/no, table tightens, body shrinks under one page.
