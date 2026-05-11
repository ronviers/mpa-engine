# Handoff — next session

## Current state (2026-05-11, v0 scaffold)

**Scaffolding landed.** Repo structure follows `mpa-brain` pattern (README, CLAUDE.md, docs/, experiments/, mpa_engine_packs/, data/, reference-driver/). Protocol-shaped artifacts (`reference-driver/*.md`, calibration record JSON) carry the thin-RFC discipline; everything else is normal engineering.

**Substrate identified.** Internal-combustion engines characterized at the dynamometer. cdv1 reads:

- Coherence: sustained crankshaft rotation under load.
- G₀: combustion energy delivery rate (fuel mass flow × LHV at the operating point).
- L: friction + pumping + thermal losses. Measured directly via motoring curve when available.
- chit = ln(G₀/L). At idle, brake_power = 0 by definition → G₀ = L → **chit = 0 exactly**. This is the cdv1 SOC-attractor prediction confirmed at one engine; cross-engine fingerprint is the sharper test.

**Reference data secured.** EPA's Ricardo Baseline Standard Car Engine (2007-era Toyota Camry 2.4L 2AZ-FE):

- Full BSFC map: 36 RPM × 29 torque grid (1044 (RPM, torque, fuel_rate) entries), 0–7000 RPM × −50 to +230 Nm
- WOT curve: 9 points, peak torque 218.25 Nm at 3999 RPM
- Motoring curve: 6 points, friction saturates at −30.05 Nm above ~1765 RPM
- Designed idle: 680 RPM
- Fuel: LHV 44 MJ/kg, density 0.738 kg/L
- Peak efficiency: BSFC 233 g/kWh (≈35% thermal efficiency) at ~3000 RPM, ~200 Nm
- Provenance: [EPA / Ricardo, 2016-06-20 PDF](https://19january2021snapshot.epa.gov/regulations-emissions-vehicles-and-engines/process-generating-engine-fuel-consumption-map-ricardo-0_.html)

## What's in this commit

- Repo scaffold (README, CLAUDE.md, .gitignore, docs/, experiments/, mpa_engine_packs/, data/, reference-driver/)
- This handoff document
- Empty FOOTING.md (substrate-conditional findings log, append-only)
- Empty mpa_engine_packs/ stub
- Driver profile stub (reference-driver/ic-engine-dyno.md) at thin-RFC weight — enough to declare substrate-class and gamut, deferring measurement-protocol detail to follow-on commits

## What's queued

In recommended order:

1. **Extract Camry data to JSON.** Transcribe the EPA PDF tables (WOT, motoring, BSFC map, idle, engine spec) into `data/camry-2.4l-2az-fe.json`. Source PDF cached at `data/sources/`. Single self-contained file so future readers can re-derive without re-pulling the EPA PDF.
2. **Implement `mpa_engine_packs.engine_data`.** Loaders + interpolation for BSFC map, WOT curve, motoring curve. Honest about the BSFC map's interpolation behaviour at the boundaries (some operating points report fuel_rate = 0 in the EPA data; the cdv1 reading needs to handle these as out-of-gamut or vacuous).
3. **Implement `mpa_engine_packs.chit_profile`.** chit(RPM, brake_torque) = ln(G₀ / (G₀ − brake_power)), with G₀ = fuel_rate × LHV. Return chit + regime classification per cdv1.
4. **Worked calibration record.** `reference-driver/camry-2.4l-2az-fe-calibration.json` conforming to [calibration-record.v0.1.json schema](https://github.com/ronviers/mpa-atlas/blob/main/schema/calibration-record.v0.1.json). Provenance: SOP refs point at the EPA PDF; cessation-trace ref points at the motoring curve.
5. **Smoke experiment.** `experiments/chit_camry.py` computes chit at idle, at peak power, at peak efficiency, at WOT low/mid/high. Writes JSON to `docs/results/`. Verifies the SOC-attractor prediction (chit ≈ 0 at idle, narrow chit range across envelope).
6. **Cross-engine fingerprint** (after outside-models Priority 2 lands). Idle RPMs and stall thresholds across 20–40 engines, carb vs ECU split. Test cdv1's "idle just above stall" prediction across engine classes. Add per-engine calibration records under `reference-driver/`.
7. **CK-aging in return-to-idle** (after outside-models Priority 3 lands, if data surfaces). Time-series transient data for one or more well-tuned engines. Predict slower-than-exponential decay tail at long times (cdv1 §Stability s-regime algebraic settling).

## Gotchas surfaced from the EPA PDF

- The BSFC map covers torque values down to −50 Nm (motoring region) — these are NOT brake operating points but the simulated motoring response. Treat as substrate-conditional: at brake_torque < 0, the engine is being driven by the dyno, not by combustion. The chit reading on this region is the *driven* register, distinct from the *driving* register that cdv1's c/s/r regimes are about.
- BSFC = ∞ at zero brake power. The chit reading handles this naturally (G₀ = L, chit = 0), but BSFC-as-a-map has a singular line at brake_torque = 0 that must not be silently interpolated through.
- Fuel rate at (0 RPM, any torque) is reported nonzero in the BSFC map — this is interpolation/boundary artefact, not physical. Out-of-gamut on the low-RPM side.
- Designed idle (680 RPM) is below the lowest WOT data point (615 RPM). The engine's gamut on the upper torque envelope doesn't extend down to idle RPM. This is correct: at idle, brake torque is zero, well below the WOT curve.

## Open RFC-C invariant question

RFC-C §3 invariant 6 ("drive sweep through chit → 0 aligns regime transitions with chit-predicted threshold"): the engine's chit-zero crossing happens at idle, not at a separately-measurable threshold. Whether this counts as "drive sweep through chit → 0" or whether the engine substrate-class requires a substrate-conditional reading of invariant 6 is open. Worth surfacing back to mpa-atlas as a finding once the calibration record actually fails or passes this invariant in `mpa-bridge validate`.

## Coordinates

- Upstream framework: [mpa-atlas/framework/cdv1_compressed.md](https://github.com/ronviers/mpa-atlas/blob/main/framework/cdv1_compressed.md)
- Validator tool: [mpa-bridge](https://github.com/ronviers/mpa-bridge) — once calibration record is written, run `mpa-bridge validate` on it
- Sibling substrate repos: [mpa-brain](https://github.com/ronviers/mpa-brain), [mpc-glass](https://github.com/ronviers/mpc-glass)
