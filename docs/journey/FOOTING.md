# FOOTING — substrate-conditional findings

Append-only log of substrate-conditional findings: things measured in this repo that the framework needs to know about engines as a substrate-class. Each entry is one finding with its evidence.

Pattern follows mpa-brain/docs/journey/FOOTING.md (F-001, F-002, F-003): code, name, date, claim, evidence, framework implication.

---

## F-001 · Engine chit envelope bounded by thermal efficiency · 2026-05-11

**Claim.** For an IC engine on a brake dynamometer, the chit envelope is bounded above by

$$\text{chit}_{\max} \approx -\ln(1 - \eta_{\text{thermal,max}})$$

where η is peak thermal efficiency. The bound is saturated at the BSFC sweet spot.

**Evidence.** Camry 2.4L 2AZ-FE (Ricardo Std Car, EPA modelled). Published peak thermal efficiency 0.351 (from BSFC 233 g/kWh at the sweet spot, LHV 44 MJ/kg). Predicted chit_max = −ln(1 − 0.351) = +0.432. Observed chit_max across sampled envelope = +0.410 at the BSFC sweet spot region. |Δ| = 0.022; under threshold of 0.10. Smoke output at [`docs/results/chit_camry_smoke.json`](../results/chit_camry_smoke.json); plots at [`docs/results/01_bsfc_contour.png`](../results/01_bsfc_contour.png) through [`04_regime_walks.png`](../results/04_regime_walks.png).

**Framework implication.** cdv1's chit unit, applied to engines, places the substrate-class operating ceiling at ~0.4–0.5 (modern gasoline) — narrow, clustered near s-regime as cdv1 §Pattern formation predicts for feedback-coupled NESS. The bound is a **substrate-class fingerprint**: engines of higher thermal efficiency (Atkinson-cycle hybrids ~0.40, advanced DI ~0.42, diesel ~0.45) shift chit_max upward. Falsifier: an engine whose observed chit_max exceeds −ln(1 − η_published) by more than 0.10 would invalidate either the chit definition or the published efficiency, and demands investigation.

**Cross-engine test condition.** F-001 should hold for Mazda Skyactiv 2.0L (η ~0.40 → chit_max ~0.51), Honda L15B7 turbo (η ~0.38 → chit_max ~0.48), Ricardo EGR-Boost DI (η ~0.42 → chit_max ~0.54). Phase B will run these.

## F-002 · Idle as cdv1 SOC-attractor · 2026-05-11 (provisional)

**Claim.** Designed idle is the engine's instance of cdv1's SOC self-tuning attractor. At idle, brake torque = 0 by definition, so G₀ = L exactly and chit = 0 exactly. The ECU (or, historically, carburettor adjustment) drives the engine to this attractor by choosing the lowest RPM at which combustion remains stable.

**Evidence.** Camry 2.4L: designed idle 680 RPM. At this operating point, smoke confirms chit = 0.000 (G₀ = L = 8.65 kW). See [`docs/results/chit_camry_smoke.json`](../results/chit_camry_smoke.json).

**Caveat.** chit = 0 at idle is *tautological* on one engine because "idle" is defined as zero brake power. The non-tautological prediction is the *RPM choice*: that idle RPM lands just above the stall threshold, with the gap (idle_RPM − stall_RPM) small relative to the operating envelope. Single-engine evidence cannot test this; the cross-engine fingerprint (Phase B) is the sharper test. F-002 promotes from *provisional* to *confirmed* when cross-engine idle/stall ratios cluster near unity for feedback-controlled engines and broader for carbureted ones.

**Framework implication.** Once cross-engine evidence lands, F-002 will be a substantive substrate-class confirmation of cdv1 §Pattern formation's parameter-space attractor claim — feedback-coupled NESS self-organises to chit ≈ 0.
