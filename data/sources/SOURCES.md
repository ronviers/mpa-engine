# Data sources

Provenance for substrate data used in this repo. Each entry: source, what it gives us, citation, retrieval date.

## Camry 2.4L 2AZ-FE (Ricardo Baseline Standard Car)

**Source.** U.S. EPA, *Process for Generating Engine Fuel Consumption Map: Ricardo Baseline Standard Car Engine Tier 2 Fuel.* National Center for Advanced Technology, National Vehicle and Fuel Emissions Laboratory, Office of Transportation and Air Quality. Version 2016-06-20.

**URL.** https://19january2021snapshot.epa.gov/regulations-emissions-vehicles-and-engines/process-generating-engine-fuel-consumption-map-ricardo-0_.html

**Direct PDF.** https://19january2021snapshot.epa.gov/sites/static/files/2016-10/documents/std-car-camry-2.4l-engine-mapping-process2016-06-20.pdf

**Retrieved.** 2026-05-11.

**Contents.**
- Engine spec: 2.4 L, 4-cyl spark ignition, 118 kW peak, inertia 0.12 kg·m². Modelled on a 2007-era Toyota Camry 2.4L (2AZ-FE family).
- WOT (maximum torque) curve, 9 points, 615–6603 RPM.
- Motoring (minimum torque) curve, 6 points, 0–7593 RPM. Friction saturates at −30.05 Nm.
- Fuel consumption map: 36 RPM × 29 torque grid (1044 data points). RPM 0–7000 in 200-RPM steps; torque −50 to 230 Nm in 10-Nm steps. Fuel rate in g/s.
- Designed idle: 680 RPM (71.21 rad/s).
- Reference fuel (RICARDO_GASOLINE): LHV 44 MJ/kg, density 0.738 kg/L at 15°C, carbon weight fraction 0.887.

**License.** Public. EPA regulatory document, no copyright restriction on U.S. government works.

**Authority.** Ricardo, Inc. produced the original engine simulation as part of the EPA/NHTSA MY2017-2025 light-duty greenhouse-gas final rulemaking. The data has regulatory standing.

**Caveats.**
- This is a *modelled* engine, not a physical-test characterization. Ricardo's simulation matches a 2007 Camry's published characteristics; substrate-conditional content is what Ricardo's model produces, not raw bench data. For mpa-engine v0 this is fine — the simulation is regulatory-grade and the model's BSFC behaviour is consistent with the production engine's known characteristics.
- The BSFC map covers torque values down to −50 Nm (motoring region). These are *driven* operating points (dyno turns the engine), not *driving* operating points (engine turns the dyno). The cdv1 chit reading on the driven region is a distinct register; out-of-gamut for cdv1's c/s/r regime structure.

## (Future entries)

Cross-engine idle RPM dataset and return-to-idle transient data, when outside-models Priority 2 and Priority 3 research lands. Each engine added gets its own subsection with the same provenance fields.
