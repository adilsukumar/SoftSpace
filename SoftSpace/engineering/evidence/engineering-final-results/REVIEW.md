# Ear defender and glasses cushion — engineering review

This is a provisional digital design and local simulation package. It is not a finished, manufactured, clinically evaluated or certified product. All numerical material/head/frame inputs are documented assumptions. Local beam and membrane FEM are real numerical solves, but they are reduced models rather than full 3D Fusion contact analysis.

## Current status

| Item | Status |
|---|---|
| CAD and local computational package | completed for the currently saved provisional revision |
| Prototype materials | assumed; supplier characterization missing |
| Peak contact pressure convergence | not passed: refinement remains mesh-sensitive |
| Thermal/moisture design | not passed: saturation persists for several cover scenarios |
| Acoustic attenuation | not validated; only uncalibrated low-frequency sensitivity model |
| Production hardware | not ready: friction stops, retention, fatigue, drop and assembly validation missing |
| Height adjustment and crown padding | three pin positions and 5 mm crown padding exported; scalp contact and retention strength untested |
| Head/ear/scalp fit and sensory acceptance | not validated |
| Replacement brand compatibility | interface blank only; no brand-specific fit established |
| Full Fusion cloud/3D nonlinear study | not run; local reduced FEM calculations provided |

## CAD produced

Adult and separate smaller child cushions have curved contact faces, main/softer foam regions, a solid cover envelope and a mounting carrier blank. Standalone passive defenders include closed cups, liner volume, circular-cap bands, three-position pinned forks, retained pins, 5 mm crown padding and exterior cup bosses. The pivot bore stays in the exterior boss and does not intentionally penetrate the sound cavity. Geometry is shown at the unloaded rest band span; it is not the shape on a wearer.

Cover thickness is 0.2 mm in the vertical/radial envelope construction, not uniform normal thickness. Lofted rims still need production rounding and seam/adhesive construction. The two family sizes are hypotheses; child ear clearance and anatomy have not been established. Source bodies are frozen imports; regenerate from `engineering-final.json` using the saved Fusion builder for geometry changes. Named Fusion parameters are annotations, not live drivers of the imported bodies.

Saved exports:
- ReplacementCushion_V4_adult_20261012_160114.step
- OwnPassiveDefender_V4_adult_20261012_160114.step
- OwnPassiveDefender_V4_adult_20261012_160114.f3d
- ReplacementCushion_V4_child_20261012_160114.step
- OwnPassiveDefender_V4_child_20261012_160114.step
- OwnPassiveDefender_V4_child_20261012_160114.f3d

`cad_final_report.json` records the exact files, volume verification and clearance results. STEP exports select the intended product components, avoiding the duplicate hidden construction solids in the document root. F3D documents contain both the replacement cushion and own-product assembly plus hidden construction geometry; select the intended components before meshing.

## Band and cushion coupling

The band solver uses geometrically nonlinear corotational Euler–Bernoulli beam elements with an assumed linear elastic modulus. Circular-cap centreline dimensions match the JSON/CAD recipe; pinned endpoints and a constant rectangular section are assumed. Local pin lugs are treated as rigid connections, not separately meshed. Material creep, fatigue, stress relaxation and out-of-plane behaviour are not represented.

The coupled model iterates band load and cushion approach until the same lateral force and compressed mounting separation are obtained. It uses a 35 mm mount offset per side and a load-curve interpolation check against direct FEM. Cover bridging is represented by scalar triangle membrane elements under prescribed tension on a nonlinear compressive spring foundation, constrained by a rigid synthetic head and rounded hypothetical frame profile. It excludes actual fabric in-plane displacement, friction, skin deformation and lateral foam coupling.

Illustrative E=2000 MPa, local foam ratio=0.5 and cover tension=1 N/m cases:

| Head scenario | Coupled force per cup N | Sampled contact area | Largest model gap mm |
|---|---:|---:|---:|
| child_small | 0.677 | 51.0% | 1.50 |
| child_medium | 1.437 | 91.9% | 0.67 |
| child_large | 2.640 | 99.9% | 0.24 |
| adult_small | 0.401 | 27.5% | 2.25 |
| adult_medium | 2.037 | 87.5% | 0.58 |
| adult_large | 4.703 | 100.0% | 0.00 |

These forces are not comfortable/safe force limits. The size/material dependence is substantial, so one band is not shown to suit every head. Contact area and gaps are numerical estimates, not proof of an airtight seal.

### Size-specific band recipes

To avoid forcing one rest span onto very different head widths, six numerical band recipes solve for a common 2 N comparison load after cushion compression. This load is an engineering comparison choice, not an acceptable pressure/force threshold. These additional recipes have not been generated as CAD variants. They use E=2000 MPa and the standard rounded hypothetical frame only.

| Head scenario | Unloaded endpoint span mm | Computed comparison force N |
|---|---:|---:|
| child_small | 151.88 | 2.000 |
| child_medium | 163.88 | 2.000 |
| child_large | 175.20 | 2.000 |
| adult_small | 183.75 | 2.000 |
| adult_medium | 200.27 | 2.000 |
| adult_large | 216.67 | 2.000 |

Peak pressure remains mesh-sensitive. The final two refinements change the nominal peak by 15.2% (128x17 to 192x25 nodes). The solver's equilibrium checks pass, but a quantitative peak-pressure comfort claim does not pass this convergence gate. Do not reuse the earlier independent-spring model's claimed pressure reductions as a product outcome.

## Heat and moisture

216 one-hour thermal/vapor cases cover ambient 28/32/36 C, RH 50/70/90%, cover water-vapor transmission hypotheses, water-source rates and foam conductivity. The model conserves water, but is spatially lumped and does not simulate sweat feedback or evaporation cooling.

At 32 C/70% RH and a hypothetical 100 mg/h water input, WVTR=1–500 g/m2/day covers reach saturation in this model. WVTR=1000 gives approximately 85.9% RH. This is a material screening target under defined assumptions, not evidence that a chosen cover will perform that way. Vapor permeation cannot be replaced by acoustic-leaking vents without a separate sound assessment.

## Acoustic sensitivity

60 hypothetical scenarios (4800 frequency rows) use a lumped panel spring/mass/loss DOF, cavity compliance and slit-leak impedance over 31.5–250 Hz. Stiffness, loss and leak sizes are arbitrary sensitivity inputs. Leak dimensions are not derived from the contact model. This is not broadband acoustic FEM and supplies no NRR/SNR or validated dB rating. Cup modes, ears, actual absorber impedance and cover transmission remain unmeasured.

## Verification completed

- Positive-volume curved foam and solid cover wrap in adult and child CAD
- Curved foam volume within 0.05% of the analytic target
- Cup/fork clearance sampled at 1 degree increments from -8 to +8 degrees in both assemblies
- Band-to-fork clearance at all three discrete height positions in both assemblies
- Beam analytic small-opening check and consistent tangent derivative check
- Beam 20/40/80-element mesh comparison
- Membrane constant-displacement null mode, mesh area and T=0 analytic foundation check
- Nodal force balance and projected obstacle-equilibrium residual checks
- Iterated common band/contact force and compressed mount separation
- Thermal temperature bounds and conservative water mass balance

## Required physical evidence

1. Measure foam stress–strain and recovery at relevant temperature/humidity; test both foam regions and their joining method.
2. Measure cover tensile behaviour, pretension, WVTR, seam properties and cleaning durability.
3. Measure actual band force versus spread and compare against FEM; check creep and repeated flexing.
4. Compression-rig and pressure-map tests with real glasses arms; check low, nominal and high host clamp forces for replacement cushions.
5. Measure sound attenuation with/without glasses; measure frequency-response changes on each host headphone model.
6. Voluntary wearer evaluations: texture, heat, pressure, ease of removal and sensory preference. Autism does not determine one universal acceptable fit or sound reduction.
7. Validate dimensions and mounting retention by headphone model; do not advertise universal brand compatibility.

## Reproduction

Run `band_fem.py`, `contact_membrane_fem.py`, `coupled_fit.py`, `size_band_recipes.py`, `environment_acoustic_screen.py`, then `build_review_package.py` using Python with NumPy. `engineering-final.json` is the recipe. The Fusion script `CushionNext/EngineeringFinal.py` produces CAD through the registered `CushionNext` script. The saved CAD includes the discrete-height and crown-padding refinement. Height changes require releasing pins; threads, pull-out strength, scalp contact and gravity are not solved.
