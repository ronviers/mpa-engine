# Data sources

Provenance for substrate data used in this repo. Sources organized by role: **extracted** (data is in the repo, derivable from the cited document), **candidate** (cited but not yet extracted; queued for pull), **bibliography** (literature we read for framing, not data extraction).

---

## 1. Extracted engine characterization data

### Camry 2.4L 2AZ-FE (Ricardo Baseline Standard Car) — extracted

**Source.** U.S. EPA, *Process for Generating Engine Fuel Consumption Map: Ricardo Baseline Standard Car Engine Tier 2 Fuel.* NCAT, National Vehicle and Fuel Emissions Laboratory, Office of Transportation and Air Quality. Version 2016-06-20.

**URL.** https://19january2021snapshot.epa.gov/regulations-emissions-vehicles-and-engines/process-generating-engine-fuel-consumption-map-ricardo-0_.html

**Direct PDF.** https://19january2021snapshot.epa.gov/sites/static/files/2016-10/documents/std-car-camry-2.4l-engine-mapping-process2016-06-20.pdf

**Local cache.** `data/sources/epa-camry-mapping-2016-06-20.pdf` (303 KB)

**Retrieved.** 2026-05-11.

**Contents.**
- 2.4 L, 4-cyl spark ignition, 118 kW peak, inertia 0.12 kg·m². Modelled on 2007-era Toyota Camry 2.4L (2AZ-FE family).
- WOT (maximum torque) curve, 9 points, 615–6603 RPM.
- Motoring (minimum torque) curve, 6 points, friction saturates at −30.05 Nm above ~1765 RPM.
- Fuel consumption map: 36 RPM × 29 torque grid (1044 entries), 0–7000 RPM, −50 to 230 Nm, fuel rate in g/s.
- Designed idle: 680 RPM.
- RICARDO_GASOLINE fuel: LHV 44 MJ/kg, density 0.738 kg/L at 15°C, carbon weight fraction 0.887.

**Caveats.**
- *Modelled* engine (Ricardo EASY5 simulation), not raw bench data. Substrate-conditional content is what Ricardo's model produces; regulatory-grade but one degree removed from physical measurement.
- BSFC map covers torque down to −50 Nm (motoring region) — *driven* operating points, distinct from *driving* points cdv1's c/s/r regimes cover. Out-of-gamut for the regime structure.

---

## 2. Candidate engine characterization data (queued for pull)

### Mazda Skyactiv 2.0L (2014) — candidate, open, EPA

**Source.** U.S. EPA, *Process for Generating Engine Fuel Consumption Map — 2014 Mazda Skyactiv 2.0L.*

**URL / Direct PDF.** https://www.epa.gov/sites/default/files/2016-11/documents/procs-gen-eng-fuel-cons-map-2014-mazda-2-0l-skyact.pdf

**Why it matters.** Different from the Camry on two axes: NA-DI (vs Camry's NA-PI) and *real bench data* (vs Camry's Ricardo simulation). Same EPA methodology, so the calibration record schema is portable. High Atkinson-cycle effective compression makes Skyactiv interesting on the chit-range axis — peak thermal efficiency ~40% would push chit-max toward 0.51 vs Camry's ~0.43.

### Honda Civic 1.5L L15B7 (2016, turbo) — candidate, open, PMC peer-reviewed

**Source.** EPA/PMC, *Benchmarking a 2016 Honda Civic 1.5-liter L15B7 Turbocharged Engine.*

**URL.** https://pmc.ncbi.nlm.nih.gov/articles/PMC6604863/

**Why it matters.** Peer-reviewed, includes spark-timing and cam-phasing maps in addition to BSFC. Turbocharged → richer operating envelope than NA engines. Third tech generation for the cross-engine fingerprint (NA-PI, NA-DI, turbo-DI).

### Ricardo 24-bar EGR Boost DI — candidate, open, EPA

**Source.** U.S. EPA, *Process for Generating Engine Fuel Consumption Map — Ricardo Cooled EGR Boost DI.*

**Direct PDF.** https://www.epa.gov/sites/default/files/2016-11/documents/procs-gen-eng-fuel-cons-map-ricardo-cool-egr-boost.pdf

**Why it matters.** Same EPA methodology and Ricardo simulation provenance as the Camry, but on an advanced DI engine with cooled EGR. Directly comparable to the Camry record; tests whether technology-generation differences show up cleanly in the chit profile.

### Brunel Hydra single-cylinder research engine (Zhao thesis) — candidate, open

**Source.** Yan Zhao, *Investigation of CAI Combustion in a Ricardo Hydra Research Engine* (PhD thesis, Brunel University).

**URL.** https://bura.brunel.ac.uk/bitstream/2438/3016/1/FulltextThesis.pdf

**Why it matters.** Real single-cylinder research-engine bench data (vs the modelled Camry). Operating-range data with combustion-stability measurements; potentially gives FDR-like fluctuation signatures.

### EPA SAE 2018-01-1412 — candidate, methodology paper, open

**Source.** EPA, *Constructing Engine Maps for Full Vehicle Simulation,* SAE 2018-01-1412.

**URL.** https://www.epa.gov/sites/default/files/2018-10/documents/sae-paper-2018-01-1412.pdf

**Role.** Methodology paper. Not data, but documents EPA's calibration discipline (sweep design, motoring measurement, idle definition) — useful for the calibration record's `methodology` field.

### Random forest BSFC datasets — candidate, open, PMC

**Source.** *Random forest method for estimation of brake specific fuel consumption,* PMC10584861.

**URL.** https://pmc.ncbi.nlm.nih.gov/articles/PMC10584861/

**Why it matters.** Two BSFC datasets used as ML-training data; explicit speed/load grids. Could supply additional engines for the cross-engine fingerprint or a falsifier substrate (if any dataset doesn't fit cdv1's chit-range prediction).

### OSTI DSCC2019-9110 — candidate, open, four diesels

**Source.** Pelletier & Brennan, *Dimensional Analysis of Engine Fuel Consumption Maps,* ASME DSCC 2019.

**URL.** https://www.osti.gov/servlets/purl/1561789

**Why it matters.** Four diesel engines, dimensionless BSFC scaling. Diesel is a separate substrate-class from gasoline SI — different combustion mode, different stall threshold semantics. If we extend the substrate-class taxonomy, diesel is its own driver profile; for v0.x we either skip or annotate as gamut extension.

---

## 3. Cross-engine idle RPM data (Priority 2)

### Service manuals — carbureted era

| Engine | Source | URL |
|---|---|---|
| Suzuki GS1000 motorcycle (carb, ≥1980) | Factory service manual | https://gsarchive.bwringer.com/mtsac/~cliff/storage/gs/GS1000_C-E-S-L_Manual.pdf |
| 1985 Toyota Truck (carb M/T, A/T; EFI) | Factory repair manual | https://documents.cdn.ifixit.com/OuKnukjQbwi5tojE.pdf |
| Ford Sierra (VV / Weber 2V carbs) | Factory service manual | https://s3cf792cad773e861.jimcontent.com/download/version/1612109662/module/12670983322/name/Ford%20Sierra%20Service%20And%20Repair%20Manual.pdf |
| Mercedes-Benz early FI (engines 119 CFI, 104 LH-SFI, etc., 1980s transition) | Factory service manual | https://www.startekinfo.com/service/download-document/outside/11832/Resources/201Create/PDF/80001a.pdf |
| Lycoming O-320 aviation (carb piston) | Operator's manual | https://www.lycoming.com/sites/default/files/attachments/O-320%2520Operator%2520Manual%252060297-30.pdf |
| AVStar fuel system (aviation, carb) | O&M manual | http://avstardirect.com/wp-content/uploads/AFS-IOM-01.pdf |
| Nissan / Datsun archive (mixed carb / EFI) | Manuals archive (nicoclub.com) | https://www.nicoclub.com/nissan-service-manuals |

### ECU-era / regulatory / structural

| Engine / source | What it gives | URL |
|---|---|---|
| GM (HPTuners parameter reference) | ECU-controlled idle RPM tables, stall-saver RPM thresholds, PID idle-control parameters | https://www.hptuners.eu/help/vcm_editor_parameters_gm_eng_idle_rpm.htm |
| PennDOT inspection program (Chapter 177) | *Regulatory upper bound* on idle: ≤4 cyl 1600 rpm max, >4 cyl 1200 rpm max | https://www.pa.gov/content/dam/copapwp-pagov/en/penndot/documents/public/dvspubsforms/bmv/bmv-publications/pub_763.pdf |
| Mechanics StackExchange thread | Discussion: relationship between flywheel inertia, stall margin, and minimum sustainable RPM | https://mechanics.stackexchange.com/questions/18928/minimum-rpm-at-idle-speed |
| VehiclePhysics.com simulation reference | Idle RPM, Stall RPM, friction torque at idle, friction at stall as explicit configurable parameters — *structural confirmation* that idle/stall gap is a real engineering quantity | https://vehiclephysics.com/blocks/engine/ |

**Coverage note.** Priority 2 yields fewer engines than ideal (~10–15 specific idle values vs the 20–40 target). Carb-era is over-represented in motorcycles/aviation; modern auto ECU specs come mostly from HPTuners' GM parameter doc. Cross-engine fingerprint will have visible carb/EFI split but lower statistical power than a full systematic dataset would give.

---

## 4. Return-to-idle transient literature (Priority 3)

### Open access

| Source | What it gives | URL |
|---|---|---|
| EPA SAE 2017-01-0533, *Characterizing Factors Influencing SI Engine Transient Fuel Consumption* | Time-series chassis-dyno data of measured-vs-mapped fuel flow during DFCO (deceleration fuel cutoff) and return-to-fuel events. **Most directly relevant open paper for CK-aging test.** | https://www.epa.gov/sites/default/files/2017-06/documents/sae-2017-01-0533-characterizing-factors-influencing-si-engine-transient-fuel-consumption-alpha.pdf |
| DTIC ADA129168, *Engine Handling* | Military aero-engine "Bodie" maneuver data (MIL-IDLE-MIL): severe deceleration transients with time-series RPM, thermal dynamics, stall-margin discussion | https://apps.dtic.mil/sti/tr/pdf/ADA129168.pdf |
| Loughborough thesis (transient mapping) | Transient engine-mapping methodology; throttle-body transient data with time-dependent covariates on a test bed | https://repository.lboro.ac.uk/articles/thesis/Transient_engine_model_for_calibration_using_two-stage_regression_approach/9219371 |
| Univ. of Alberta (Balazadeh) | Transient model + experimental tip-out torque profiles with NOx penalties | https://sites.ualberta.ca/~mahdi/Docs/57_CICS_2023_Paper_Balazadeh.pdf |
| Stanford thesis (Bernard Johnson) | Low-load and idle operation challenges, transient calibration, Stanford engine lab data | https://stacks.stanford.edu/file/druid:cp633zj5935/thesis_BernardJohnson-augmented.pdf |
| METU MSc (sub-idle turboshaft) | Shaft dynamics equations for sub-idle transients, low- vs high-frequency transient modeling | https://open.metu.edu.tr/bitstream/handle/11511/114021/10711575.pdf |
| EPA Diesel Emissions VII | 1970s-era light-duty diesel transient cycle data, second-by-second RPM and load | https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=9101VK3U.TXT |
| NCDOT On-Board Emissions | Second-by-second vehicle activity protocol, modal emissions and RPM time-series datasets | https://connect.ncdot.gov/projects/research/RNAProjDocs/1999-08FinalReport.pdf |

### Paywalled (would require institutional access; deferred)

| Source | Relevance |
|---|---|
| SAE 850967, *Vehicle Response to Throttle Tip-In/Tip-Out* | Directly relevant. Driveline torque transients during return-to-idle. |
| SAE 770046, *Transient Response of a Carburetor Engine* (1977) | Carb-era transient fuel/air flow with discussion of deceleration lags. Pre-ECU baseline. |
| SAE 820902, *Single Point Electronic Injection System* | Comparison of transient response: single-point EFI vs carb vs multi-point. Transition-era baseline. |

---

## 5. Adjacent literature — idle as nonlinear / dissipative dynamics

### Open access — substantive cdv1 touchpoints

| Source | Why it touches cdv1 | URL |
|---|---|---|
| Bemporad et al., *Model Predictive Idle Speed Control,* IEEE Control Systems | Treats engine idle as a constrained multivariable nonlinear control problem; includes time-series disturbance rejection data | http://cse.lab.imtlucca.it/~bemporad/publications/papers/ieeecst-idlespeed.pdf |
| Atlantis Press review, *Engine idle speed control research status and development trend* | Explicitly characterizes engine idle as "nonlinear, time-varying, uncertain dynamics" — **framing language overlaps cdv1 substantively** | https://www.atlantis-press.com/article/25844909.pdf |
| Univ. of Michigan DeepBlue, *Time-Delay Systems: Analysis and Control Using the Lambert W Function* | Lambert W applied to engine idle speed control with **self-excited limit-cycle oscillation analysis** — directly maps onto cdv1 §Stability's DDE Hopf and Wall-forces-NRT chain | https://deepblue.lib.umich.edu/bitstreams/61aef63c-c146-4d10-9271-90c5d3e25f91/download |
| DTIC ADA260871, *Nonlinear Vibrations, Stability, and Dynamics of Structures* | Saddle-node + period-doubling bifurcations in mechanical systems; methodological background for engine idle as bifurcation problem | https://apps.dtic.mil/sti/tr/pdf/ADA260871.pdf |
| MDPI Applied Sciences, *Dynamic Modelling of Resonance Behavior in Four Cylinder Engines* | Engine vibration transients converging to stable periodic attractors; dissipative energy flow at idle stability | https://www.mdpi.com/2076-3417/16/5/2225 |

### Paywalled

| Source | Relevance |
|---|---|
| ScienceDirect, *Automotive engine idle speed controller: NMPC utilizing firefly algorithm* | FPGA-oriented NMPC, framing idle as nonlinear optimization with state constraints |

### Bibliography pointers

- White Rose eTheses, *Effect of Fuel Content on the Human Perception of Engine Idle Quality* (https://etheses.whiterose.ac.uk/id/eprint/15056/1/425574.pdf) — cites SAE 860412 ("Engine idle stability analysis and control") and SAE 970035 ("Relating subjective idle quality to engine combustion"). Useful for tracking down 1980s–1990s idle-stability SAE literature if we go deeper.
