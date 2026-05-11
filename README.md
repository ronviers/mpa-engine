# mpa-engine

The cdv1 reading on internal-combustion engines characterized at the dynamometer. First substrate-class instance of cdv1 outside its laser-derived origin domain: an engine is a one-mode driven-dissipative NESS held against friction-and-pumping losses by combustion energy supplied per cycle. The dyno is its calibration apparatus; published dyno data is its archive.

## What this substrate is

A real driven-dissipative NESS whose three regimes are all reachable from the same operating envelope:

- **c-regime** — engine running under load. chit = ln(G₀/L) > 0; combustion power exceeds losses by the brake work delivered to the dyno.
- **s-regime** — engine at idle. Brake power = 0 by definition of idle (else the load accelerates), so G₀ = L and **chit = 0 exactly**. cdv1 §Pattern formation predicts feedback-coupled NESS self-organises to chit ≈ 0 as a parameter-space attractor; the ECU's idle-control loop is the SOC self-tuning that lands the engine there.
- **r-regime** — engine off, or below stall threshold. No sustained rotation.

Engines never operate at chit much above ~0.5 — the operating envelope is narrow, clustered near the s-regime, which is exactly the framework's prediction for feedback-coupled NESS over-represented near critical.

## What this repo contains

- A driver profile for the substrate-class (`reference-driver/ic-engine-dyno.md`), shaped per [mpa-atlas RFC-S §4](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-S_Scale-Management.md#4-driver-profile).
- One worked calibration record (`reference-driver/camry-2.4l-2az-fe-calibration.json`), shaped per [mpa-atlas RFC-C §2](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-C-Calibration.md#2-shape).
- Engine data (`data/`): extracted from EPA's [Process for Generating Engine Fuel Consumption Map (Ricardo Baseline Standard Car Engine Tier 2 Fuel)](https://19january2021snapshot.epa.gov/regulations-emissions-vehicles-and-engines/process-generating-engine-fuel-consumption-map-ricardo-0_.html), based on the 2007-era Toyota Camry 2.4L 2AZ-FE engine.
- A Python kernel (`mpa_engine_packs/`) that computes chit at any (RPM, torque) operating point from a calibration record.
- Experiments (`experiments/`) that produce a chit profile across the operating envelope.

## What this repo does not contain

- Substrate physics derivations or thermodynamic modelling. The engine's internals are out of scope; we read the dyno's input-output map as substrate-conditional content.
- mpa-atlas schemas. Those live upstream; this repo references them.
- Engine controller (ECU) code or models. The controller is part of the substrate; we observe its outputs (designed idle RPM, idle stability) and read them, not model them.

## Run

Smoke (chit profile for the EPA Camry across its operating envelope, ~1 s):

```
python H:/mpa-engine/experiments/chit_camry.py
```

## Discipline

See [CLAUDE.md](CLAUDE.md) for the implementation-not-protocol carve-out (same shape as mpa-bridge). Protocol artifacts (`reference-driver/*.md`, calibration record JSON) follow mpa-atlas's thin-RFC discipline; everything else is normal engineering.

## Coordinates

| Document | Where |
|---|---|
| Open work | [docs/handoff_next_session.md](docs/handoff_next_session.md) |
| Substrate-conditional findings | [docs/journey/FOOTING.md](docs/journey/FOOTING.md) |
| Driver profile (this substrate's mpa-atlas RFC-S §4 artifact) | [reference-driver/ic-engine-dyno.md](reference-driver/ic-engine-dyno.md) |
| First calibration record | [reference-driver/camry-2.4l-2az-fe-calibration.json](reference-driver/camry-2.4l-2az-fe-calibration.json) |
| cdv1 (the framework being instanced) | [mpa-atlas/framework/cdv1_compressed.md](https://github.com/ronviers/mpa-atlas/blob/main/framework/cdv1_compressed.md) |
| RFC-S (driver profile shape) | [mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-S_Scale-Management.md) |
| RFC-C (calibration-record shape) | [mpa-atlas/rfcs/MPA-RFC-C-Calibration.md](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-C-Calibration.md) |
