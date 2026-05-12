# Handoff — next session

## FROZEN — 2026-05-11

This handoff is frozen. Cross-substrate damping-universality work has moved to [mpa-relaxation](https://github.com/ronviers/mpa-relaxation); the engine work below (Phase B Skyactiv cross-engine fingerprint, Phase C transient signature, Phase D mpa-atlas validation) is deferred indefinitely.

**What stands:** F-001 confirmed (chit_max ≈ -ln(1 - η_thermal,max), observed +0.410 vs. predicted +0.432 on Camry 2.4L 2AZ-FE). F-002 provisional (idle as cdv1 SOC attractor; cross-engine evidence not pursued).

**Why frozen:** The carb-tuning scenario that motivated F-003 maps onto loudspeakers more cleanly than onto engines — Q_ts is a one-number damping dial, CSD measurement archives are free and abundant, and modern ECU dashpot algorithms partly erase the natural physical decay structure F-003 was trying to detect. Loudspeakers don't have that engineered overlay. mpa-relaxation carries the cross-substrate test with engines cited (this repo) and loudspeakers as substrate zero.

The original plan is preserved below as a record.

---

## Current state (2026-05-11, v0 scaffold + research landed)

**Scaffolding landed (commit 9ea2adc).** Repo structure matches `mpa-brain` pattern. Protocol-shaped artifacts carry mpa-atlas thin-RFC discipline; everything else is normal engineering.

**Substrate identified.** Internal-combustion engines characterized at the dynamometer. cdv1 reads:

- Coherence: sustained crankshaft rotation under load.
- G₀: combustion energy delivery rate (fuel mass flow × LHV at the operating point).
- L: friction + pumping + thermal losses. Measured directly via motoring curve when available.
- chit = ln(G₀/L). At idle, brake_power = 0 → G₀ = L → **chit = 0 exactly**.

**Camry 2.4L 2AZ-FE data secured.** EPA Ricardo simulation; full BSFC map, WOT curve, motoring curve, idle. See `data/sources/SOURCES.md` §1.

**Priority 2/3/Adjacent research landed (2026-05-11).** Source pointers organized in `data/sources/SOURCES.md` §2–§5:
- §2: Six candidate additional engines (Mazda Skyactiv 2.0L NA-DI, Honda L15B7 1.5L turbo, Ricardo EGR-Boost DI, Brunel Hydra single-cylinder, plus EPA methodology paper and PMC random-forest BSFC datasets).
- §3: ~10–15 cross-engine idle RPMs across carb-era service manuals + ECU-era HPTuners + PennDOT regulatory bounds + VehiclePhysics structural confirmation.
- §4: Open-access transient literature (EPA SAE 2017-01-0533 covers DFCO; DTIC Bodie maneuvers; theses). Prime SAE papers (850967, 770046) paywalled, deferred.
- §5: **Two substantive cdv1 touchpoints in adjacent literature** — Lambert W self-excited limit cycle at idle (UMich DeepBlue), and Atlantis Press review framing idle as "nonlinear, time-varying, uncertain dynamics." Both pre-date cdv1; engineering literature has been reaching for what cdv1 names.

## What's queued

In recommended order:

### Phase A: Camry first end-to-end (no external research needed beyond Priority 1 already in hand)

1. **Extract Camry data to JSON.** Transcribe EPA PDF tables into `data/camry-2.4l-2az-fe.json`. Single self-contained file. Schema: `{engine: {...spec...}, wot_curve: [{rpm, torque_nm}, ...], motoring_curve: [{rpm, torque_nm}, ...], bsfc_map: {rpm_grid, torque_grid, fuel_rate_gps_grid}, idle: {rpm}, fuel: {lhv_mjpkg, density_kgpl, ...}}`.
2. **Implement `mpa_engine_packs.engine_data`.** Loaders + interpolation. Honest gamut handling: BSFC values at (RPM=0, any) and at brake_torque < 0 are out-of-gamut for cdv1's driving register.
3. **Implement `mpa_engine_packs.chit_profile`.** `chit(rpm, brake_torque) = ln(G_0 / (G_0 - brake_power))` with `G_0 = fuel_rate(rpm, brake_torque) * LHV`. Return chit + regime classification.
4. **Camry calibration record.** `reference-driver/camry-2.4l-2az-fe-calibration.json` conforming to [calibration-record.v0.1.json](https://github.com/ronviers/mpa-atlas/blob/main/schema/calibration-record.v0.1.json). SOP refs point at the EPA PDF; cessation-trace ref at the motoring curve.
5. **Smoke experiment.** `experiments/chit_camry.py` computes chit at idle, peak power, peak efficiency, several WOT points. Writes JSON to `docs/results/`. Verifies SOC-attractor: chit ≈ 0 at idle, narrow chit range (~[0, 0.5]) across envelope.
6. **First FOOTING entry.** F-001: "Engine chit range bounded by thermal efficiency" — chit_max ≈ −ln(1 − η_thermal,max). Substrate-class universality conjecture for the cross-engine fingerprint to test.

### Phase B: Cross-engine fingerprint (uses Priority 1 candidate engines + Priority 2 idle data)

7. **Pull Mazda Skyactiv 2.0L data.** Repeat steps 1–4 for the Skyactiv. Calibration record + chit profile. **Expected difference from Camry:** higher peak thermal efficiency (~40% vs ~35%) → chit_max ~0.51 vs ~0.43. If FOOTING F-001 holds, this should be quantitative.
8. **Pull Honda L15B7 turbo data.** Same. Turbocharged → broader operating envelope, possibly different chit-range fingerprint.
9. **Idle-vs-stall fingerprint table.** Pull idle RPMs from §3 service manuals. Extract carb-vs-EFI split. For each engine where stall RPM is known or extractable, compute idle-RPM / stall-RPM ratio. **cdv1 prediction:** ratio clusters tighter (smaller, just-above-1) for ECU-controlled engines; broader for carbureted. PennDOT regulatory bound (1200/1600 RPM) sits well above the substrate-class typical idle — confirms regulatory envelope is set by stability margin not optimum efficiency.
10. **FOOTING F-002:** the idle-vs-stall fingerprint result.

### Phase C: Transient signature (CK-aging test) — uses Priority 3 + Adjacent

11. **Pull EPA SAE 2017-01-0533.** Extract time-series fuel-flow data during DFCO and return-to-fuel events. Most directly relevant open data.
12. **Pull UMich Lambert W thesis.** Read for the self-excited limit cycle model at idle. Compare its DDE structure to cdv1 §Stability's Wall-forces-NRT chain. Two outcomes: (a) the DDE Hopf bifurcation cdv1 predicts is recognizable in the Lambert W framework → strong cdv1 touchpoint; (b) the two formalisms describe distinct phenomena → weaker but still informative.
13. **Pull Atlantis Press review.** Read for the "nonlinear, time-varying, uncertain dynamics" framing and any survey of published return-to-idle transient data.
14. **Compute return-to-idle decay tail.** If §11 data permits, fit exponential vs power-law tail to RPM(t) after tip-out. cdv1 §Stability predicts algebraic settling at chit-zero (well-tuned engines); exponential elsewhere.
15. **FOOTING F-003:** the transient signature result (or honest null finding if data is insufficient).

### Phase D: Validate against mpa-atlas

16. **Run `mpa-bridge validate` on each calibration record.** Surface any schema or RFC-S §5 round-trip failures.
17. **Surface RFC-C invariant 6 question to mpa-atlas.** RFC-C §3 invariant 6 ("drive sweep through chit → 0 aligns regime transitions with chit-predicted threshold") is awkward for engines: chit-zero IS idle, not a separately-measurable threshold. Substrate-conditional reading of invariant 6 may be needed.

## Gotchas surfaced

- BSFC map covers torque values down to −50 Nm (motoring region) — these are *driven* operating points, distinct from *driving* points. Out-of-gamut for cdv1's c/s/r regime structure.
- Fuel rate at (0 RPM, any torque) is reported nonzero in the BSFC map — interpolation/boundary artefact, not physical. Out-of-gamut on the low-RPM side.
- BSFC = ∞ at zero brake power. chit reading handles this naturally (G₀ = L, chit = 0), but BSFC-as-a-map has a singular line at brake_torque = 0 that must not be silently interpolated through.
- Modelled engines (Ricardo simulation: Camry, Ricardo-EGR) vs measured engines (Mazda Skyactiv, Honda L15B7): calibration records should declare which, and the cross-engine fingerprint should not pool the two without acknowledging the methodological boundary.

## Open RFC-C invariant question

(Carried from v0.) RFC-C §3 invariant 6 ("drive sweep through chit → 0 aligns regime transitions with chit-predicted threshold") is awkward for engines because chit-zero IS idle, not a separately-measurable threshold. Worth surfacing back to mpa-atlas as a finding once `mpa-bridge validate` is actually run on the Camry calibration record.

## Coordinates

- Upstream framework: [mpa-atlas/framework/cdv1_compressed.md](https://github.com/ronviers/mpa-atlas/blob/main/framework/cdv1_compressed.md)
- Validator tool: [mpa-bridge](https://github.com/ronviers/mpa-bridge)
- Sibling substrate repos: [mpa-brain](https://github.com/ronviers/mpa-brain), [mpc-glass](https://github.com/ronviers/mpc-glass)
