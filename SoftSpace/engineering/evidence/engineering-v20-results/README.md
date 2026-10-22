# Pre prototype evidence review

Updated 21 October 2026. SoftSpace remains the V19 standalone headphone concept. SoftSpace Flex adds V20 reference pad bodies. This folder records a bounded computer study, not completion of every requested model or a product validation.

## Decision

Proceed with small material, pad and bench-hinge samples. Do not commit to production tooling, a batch of complete headphones, or a custom Sony mounting carrier based only on these files. There is no credible probability of success to quote. The work is more informed than an arbitrary purchase because it records dimensions, controls, sensitivities and failures, but its real-world predictive accuracy is unknown.

The user does not need to measure their own Sony now. A supplier or workshop can use one correctly labelled WH-CH720N replacement pad or a host headphone as its mounting reference. Published aftermarket outside dimensions allow pad-body exploration; they do not supply the exact groove or skirt dimensions.

## New evidence

| Item | Result | Meaning |
|---|---|---|
| Published compatible-pad envelope | 80 mm wide, 100 mm high, 30 mm thick | Brainwavz aftermarket dimensions, not Sony OEM metrology |
| Sony mount instructions | Groove attachment and top/bottom alignment | Does not establish precise skirt dimensions |
| Three V20 STEP pad bodies | Reimport and volume checks passed | Uniform control, 18 mm zone, 32 mm zone; no mounting skirt release |
| Four-area contact model | 11,664 paired scenarios saved | Synthetic foam laws and forces, not measured Sony or worn-head contact |
| Compression screen | 438 cases above the chosen 40% cutoff flagged | Not accepted as reliable high-compression predictions; cutoff is not a foam qualification |
| Narrow 12 mm zone | 624 eligible cases increased local pressure, up to 3.76% | A misplaced patch can be counterproductive; counts are not failure probabilities |
| Wider 18, 24, 32 mm zones | No pressure increase within the eligible finite scenario set | Not universal glasses coverage or proven comfort |
| Separate scalar calculation | 12 selected pressure comparisons below the chosen 1% difference | Different integration/root implementation, same reduced physical assumptions |
| Eight V19 joint result audits | All passed on a fresh workspace | Same-equation reassembly and saved-array checks; not a new physical test or independent FE solver |
| Hinge settings | 5 of 36 assumed combinations had negative holding margin | Torque must be measured after assembly and locking |
| Pin and bore scenarios | 33 of 54 assumed combinations had nonpositive remaining clearance | Printer/supplier capability cannot be presumed from nominal CAD |

## Reproduce the bounded screens

Materialize the published workspace as described in the engineering guide and install the recorded numerical dependencies. Run the following from that workspace:

```console
python v20_preprototype_screen.py
python build_v20_flex_reference.py
python verify_v20_screen.py
```

The separate V19 saved-array audit uses `verify_v19_quadratic.py` for the `quadratic-contact` and `quadratic-inward` folders. Original raw solutions remain unchanged. `saved_audit_rerun.json` records the audit performed in the prepared workspace. The local orchestration wrapper has machine-specific paths; it is retained as a historical execution record, not a portable entry point.

The contact model integrates an elliptical annulus with outside semiaxes 40 and 50 mm and inside semiaxes 25 and 35 mm. It divides the face into four areas based on membership in the soft zone and glasses strip. At fixed per-cup force it solves the common closure so the sum of pressure times area equals that force. Negative closure permits nonglasses areas to detach.

Pressure in N/mm2 is `E * (max(closure + protrusion, 0) / 30)^n + kcover * max(closure + protrusion, 0)`. `E` is an assumed scale in MPa, not a measured modulus or fitted foam grade. The zone scales the first term by the chosen ratio. The cover term is a synthetic parallel-stiffness bracket, not a biaxial membrane solution. There is no foam lateral coupling, shaped skin, pinna, fabric shear, real seams, glasses bending or host-force calibration.

The sweep uses per-cup forces 2/4/8 N; E 0.01/0.03/0.1 MPa; exponent 1/2; cover stiffness 0/0.0002/0.001 N/mm3; arm protrusion 1/2/4 mm; arm centres 8/15/24 mm above pad centre; widths 3/5/8 mm; zone heights 12/18/24/32 mm; and stress ratios 0.25/0.5. The zone is on the right half of the pad, centred 15 mm above pad centre. Only the uniform, 18 mm and 32 mm geometries are exported as CAD.

`contact_controls.json` records uniform-pressure and force-balance checks and a selected 160/320/640 grid comparison. `verification.json` separately checks 12 cases using exact ellipse-strip quadrature and a scalar Brent root. These are implementation checks, not evidence that the model describes an actual wearer.

The open-slit screen uses the steady laminar rectangular-slit conductance `w*h^3/(12*mu*L)`, with width 5 mm, path 15 mm and air viscosity 1.81e-5 Pa s. This is an airflow sensitivity illustration. It is not an acoustic transfer function, attenuation rating, outgoing music level or ANC simulation. A continuous cover removes a deliberately cut-through slot but does not prove a worn seal.

## Prototype purchase sequence

1. Small traceable open-cell foam samples in at least two stiffnesses and at least two cover samples. Request compression/recovery data, grade, lot and thickness; do not buy by a generic memory-foam label alone. Cover permeability and stiffness can change sealing and the pressure benefit.
2. One model-specific reference replacement pad or access to a supplier-held WH-CH720N. Confirm actual attachment before a custom skirt. No purchase was made in this work.
3. Matched uniform, 18 mm and 32 mm zone pad samples, at 100 x 80 x 30 mm gross size with an initial assumed 50 x 70 mm opening. These are comparison samples, not a final fit specification. Preserve the original pad for baseline tests.
4. One bench hinge and pin-fit sample using the V19 nominal handoff for supplier review. Use dimensional inspection and bore finishing as needed; do not assume raw printed holes meet the proposed tight clearance allocation. Measure breakaway/running torque in both directions and recheck after locking.
5. Only then one adult fixture assembly. Material and assembly changes need updated models and tests before child/wearer trials or claims of safety, comfort, isolation or robustness.

Production drawings, tool access, pin drive/runout, actual spring setting, nut locking, cover seams/bond and the mounting skirt are not manufacturing released. The V20 files deliberately do not invent these missing interfaces.

## Grant evidence wording

We developed six adjustable headphone concepts, documented sampled folding checks and conditional joint calculations, and created three reference cushion designs from published aftermarket dimensions. A bounded sensitivity study identified a narrow-zone pressure risk and assembly-setting risks. We seek prototype funding to measure the missing inputs, refine the model and test the proposed comfort and sealing benefits.

This supports an early research and prototype proposal. It does not establish a clinical benefit, user acceptance, superior market performance, a verified Sony fit, zero leakage, an attenuation rating, a lowest-cost claim or a quantified product success probability. No grant eligibility decision or application submission is part of this packet.

## Evidence handling

Raw CSVs, JSON assumptions, source URLs, CAD hashes, recorded failures and actual source screenshots are supplied. The plots are calculated figures, not experimental photographs. The source screenshots were captured from the named pages; they were not recreated as fake manufacturer or Fusion output. Both living Word reports include the same new findings and purchase recommendation. Native Word pagination remains unverified because LibreOffice was unavailable and no connected Word session was present; approximate previews were reviewed separately.

The complete V19 release bundle is an older immutable snapshot. This V20 update is additional evidence and does not retroactively change that bundle or relabel earlier failures as passes.
