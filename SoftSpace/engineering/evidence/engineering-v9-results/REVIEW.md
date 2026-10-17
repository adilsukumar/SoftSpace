# Native V9 CAD and structural review

## Subsequent all body audit supersedes the earlier motion clearance conclusion

The later all-body audit imported all18 nominal/endpoint STEP files and tested every possible body pair, with bounding-box filtering and a0.01mm3 positive-intersection threshold. All six shortest-setting exports FAIL: two slider-pivot-pin/guide intersections per size; the three child sizes also have two clamp-knob/fork intersections. Nominal and maximum-setting exports pass this check. See all_pose_pairs.json. The earlier motion check omitted the pivot pins and clamp knobs. V9 is NOT a cleared full-travel design. Its nominal bare-band mesh results remain evidence for that particular load case only. V10 changes the guide bottoms and clamp positions and requires fresh structural checks. The original V9 ZIP is a historical snapshot, superseded on adjustment clearance by this later audit.

Native geometry exported for 6 of 6 sizes. Digital check status: complete bounded digital checks. This is an experimental design package; product validation is unfinished.

Eight internal vertical slider corners were rounded by 0.5 mm. All available STEP imports contain 28 solids and the recorded band static/slider overlap checks passed. Each size has a nominal STEP, two slider endpoint STEP files and a matching local Fusion archive. The six sizes are synthetic width variants, not an anthropometric fit guarantee.

adult_small: last stress mesh change 1.913%; guide displacement change 0.017%. Latest centroid stress 3.9707MPa under assumed E2000MPa, nu0.35, ideal2N/side. No material-strength or comfort claim.

child_small: last stress mesh change 2.785%; guide displacement change 0.015%. Latest centroid stress 3.6237MPa under assumed E2000MPa, nu0.35, ideal2N/side. No material-strength or comfort claim.

child_medium: last stress mesh change 2.858%; guide displacement change 0.023%. Latest centroid stress 3.5456MPa under assumed E2000MPa, nu0.35, ideal2N/side. No material-strength or comfort claim.

child_large: last stress mesh change 3.963%; guide displacement change 0.020%. Latest centroid stress 3.4477MPa under assumed E2000MPa, nu0.35, ideal2N/side. No material-strength or comfort claim.

adult_medium: last stress mesh change 3.797%; guide displacement change 0.012%. Latest centroid stress 4.5690MPa under assumed E2000MPa, nu0.35, ideal2N/side. No material-strength or comfort claim.

adult_large: last stress mesh change 2.019%; guide displacement change 0.014%. Latest centroid stress 3.7632MPa under assumed E2000MPa, nu0.35, ideal2N/side. No material-strength or comfort claim.

Nominal hybrid force screen: 18 cases, middle slider setting only, calculated force 2.275 to 3.522 N per side; maximum foam compression 4.107 to 5.700 mm. Native linear band compliance is coupled to the earlier scalar pad model. Materials, heads and 35 mm mount offset are assumed. No comfort threshold or full 3D worn-contact result.

Archive check: six local Fusion archive container directories are readable. Their member compression is unsupported by the bundled ZIP checker, so member integrity/native reopening is unverified. Independent nominal and endpoint STEP imports and volume preservation checks passed.

V9 refines the V8 standalone band. The V8 replacement cushion is unchanged. Keep the V8 package for its pad, force sensitivity and acoustic screening evidence. No real sound leakage, wearer comfort or physical strength result has been added.

Desktop control recovered and the remaining native builds ran. Old local STEP-only failures remain separate. Native mesh results apply only to their recorded geometry and ideal load. They do not verify scalp contact, slider locking, material yield, fatigue, drops or the whole assembly.

Before fabrication, choose actual foam, cover and band materials and measure their properties. Fit a complete assembly and calculate nonlinear contact using those measurements. Test slider retention and manufacturing tolerances. Acoustic attenuation needs a calibrated physical setup with and without glasses; music-out tests need a specific host headphone. Sensory acceptance requires voluntary wearer feedback. These cannot be replaced by assuming favourable inputs.

No market superiority is established. Our calculated stress/displacement cannot be ranked against market products whose geometry, materials and matched measured tests are unavailable. The market review covers a selected sample, not every model.

Both Word documents were updated together. Their native Word layout remains unverified; independent approximate previews and structural checks are available.
