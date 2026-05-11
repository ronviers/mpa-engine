# Discipline: implementation, not protocol

This repo is a **substrate characterization** under the mpa framework. It instances cdv1 ([mpa-atlas/framework/cdv1_compressed.md](https://github.com/ronviers/mpa-atlas/blob/main/framework/cdv1_compressed.md)) on a real substrate (internal-combustion engines, characterized at the dynamometer) using publicly-archived data.

## What thin-RFC discipline does and does not govern here

[mpa-atlas](https://github.com/ronviers/mpa-atlas) carries [thin-RFC discipline](https://github.com/ronviers/mpa-atlas/blob/main/CLAUDE.md). That discipline governs **protocol-shaped artifacts** — RFC documents, schema files, exchange contracts. Same carve-out as `mpa-bridge` and `mpa-character`:

- **Protocol artifacts** (`reference-driver/*.md`, calibration record JSON, driver profile shape) — thin-RFC discipline applies. Half-page targets, six-field templates where applicable, point at mpa-atlas RFCs for rigor.
- **Source code** (`mpa_engine_packs/**`) — normal engineering. Write what's clearest; refactor when shape demands; no page budget.
- **Experiments** (`experiments/**`) — normal engineering. Small scripts that exercise the kernel against the data.
- **Docs and READMEs** — operational meta, written for clarity over brevity. Still: short is better.
- **Substrate-conditional findings** (`docs/journey/FOOTING.md`) — append-only journey log. Each footing entry is one finding with its substrate evidence. Not prose.

## What this repo is for

- Verify that the mpa-atlas protocol surface (driver profile, calibration record) fills out cleanly for a substrate cdv1 was *not* derived from.
- Compute the cdv1 chit reading across the engine's operating envelope from published BSFC + WOT + motoring data.
- Test cdv1's SOC-attractor prediction: feedback-coupled NESS lands at chit ≈ 0; idle is the engine's instance of this attractor.

## What this repo is not for

- **Substrate physics derivations.** The engine's internals (combustion thermodynamics, valve timing, knock physics) are out of scope. We read the dyno's input-output map as the substrate's exchange surface.
- **mpa-atlas schema authoring.** Schemas live upstream. This repo references them.
- **ECU controller modeling.** The controller is part of the substrate. We observe its outputs (designed idle RPM, idle stability), not model its internals.
- **Other engine families.** v0 is gasoline IC engines on a dyno. Diesel, two-stroke, gas turbine, electric — each is its own substrate-class and gets its own repo or driver profile if it earns one.

## Substrate-neutral content lives upstream

cdv1's universality classes, posit structure, and protocol invariants are framework content and live in [mpa-atlas/framework/cdv1_compressed.md](https://github.com/ronviers/mpa-atlas/blob/main/framework/cdv1_compressed.md). This repo does not restate them; it cites them and supplies *substrate-conditional amplitudes* per [cdv1 Open items](https://github.com/ronviers/mpa-atlas/blob/main/framework/cdv1_compressed.md#open-items) "Two classes of residual: (i) empirical coupling parameter, (ii) substrate-thermodynamic derivation."

If you find yourself encoding cdv1 universality content inside this repo, stop — that belongs in mpa-atlas.

## Coordinates

| Document | Where |
|---|---|
| Open work | [docs/handoff_next_session.md](docs/handoff_next_session.md) |
| Substrate-conditional findings | [docs/journey/FOOTING.md](docs/journey/FOOTING.md) |
| cdv1 (framework being instanced) | [mpa-atlas/framework/cdv1_compressed.md](https://github.com/ronviers/mpa-atlas/blob/main/framework/cdv1_compressed.md) |
| RFC-S (driver profile shape) | [mpa-atlas/rfcs/MPA-RFC-S_Scale-Management.md](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-S_Scale-Management.md) |
| RFC-C (calibration-record shape) | [mpa-atlas/rfcs/MPA-RFC-C-Calibration.md](https://github.com/ronviers/mpa-atlas/blob/main/rfcs/MPA-RFC-C-Calibration.md) |
