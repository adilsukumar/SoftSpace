# V10 CAD candidates and recorded numerical checks

Updated 14 October 2026. This package records concept geometry and calculations. It does not establish comfort, sound reduction, sensory acceptance, pain prevention, market superiority, zero leakage or production readiness.

The mechanical calculations use local Python, Gmsh and SciPy on the saved STEP geometry. Runtime versions are recorded in runtime_versions.json. Library installations remain in the local project and are not bundled in this ZIP.

All six native Fusion candidates were exported as six F3D archives and 18 nominal/endpoint STEP poses. Each STEP contains 28 solids and passes the all-body intersection audit at a 0.01 mm3 overlap tolerance. Each F3D was reopened in Fusion and its V10 component contained 28 solids. Native and local band shapes agree within the 0.01 mm3 volume comparison tolerance. Source hashes are saved.

Current CAD hashes also match the files used in the recorded checks. archive_integrity.json is an earlier inventory: its reopening flags were recorded before the native reopening check, and its Python reader could not verify an unsupported compression method. native_archive_reopen.json records the later Fusion reopening results. The outer deliverable ZIP receives a separate CRC and file-hash check.

The wider V9 audit found shortest-setting guide/pivot-pin clashes in all six sizes and extra knob/fork clashes in the child sizes. Earlier selected-body checks had omitted these parts. V10 trims the guide bottoms by 2 mm and raises the clamp bores and knobs by 4 mm. The intended slider range remains 0 to 30 mm. Nominal selected gaps are 0.217157 mm for guide/tongue, 1 mm for guide/pin and 0.5 mm for knob/fork. These are CAD gaps, not proven factory tolerances. The clamp reach audit checks 84 positions geometrically; it does not prove locking or retention.

Changed-guide quarter-band sampled stress comparisons meet the chosen 5% limit in 6 of six sizes. All six guide-displacement comparisons meet that limit. The earlier adult-medium 8.37% and 18% changes remain in history. The quarter model mirrors the front-only bore onto the rear wall. Its nominal geometric approximation remains even after numerical refinement.

The separate actual-width ideal-fixture study covers 6 of six sizes. Its sampled stress comparisons meet 5% in 6 of those sizes. Guide compliance and stress are reported separately; displacement stability alone is not peak-stress stability. The actual-width model retains the real front-only bore, but its crown restraints and surface loading differ from the quarter model. It does not isolate symmetry error or solve the worn assembly.

Slider segment checks use consistent surface loads at 0, 15 and 30 mm adjustment. The reduced force screens combine ideal band/slider compliance with scalar foam/cover contact and synthetic heads. They omit real guide rotations, clamp friction, pin bearing and scalp contact. All material properties and mounting offsets remain assumed. They do not establish a comfort or sound-seal threshold.

The invalid first adult-large quarter mesh and earlier memory, export, load and solver failures are retained. Accepted element-quality, residual and force-balance checks are numerical evidence, not physical verification. Last-two-mesh peak comparisons are not absolute continuum error bounds.

Sony WH-CH720N is the selected replacement-pad host. The user owns it and will measure its mount later. The generic pad is not claimed compatible. Host force, mounting dimensions, driver/vent geometry, incoming noise, outgoing music, response, ANC and wearer comfort remain untested. Existing replacement-pad competitors are recorded in both reports; no superiority or confirmed Indian market absence is claimed.

Remaining work includes measured foam/cover/band properties, real locking and retention, joints and worn-head contact, manufacturing tolerances, thermal/moisture checks, calibrated acoustic comparisons and voluntary sensory feedback. These dependencies prevent a finished commercial-product claim.

Both Word reports were updated together. Their structure and approximate previews were checked. Native Word pagination remains unverified: desktop control returned unavailable elements and activation failures, followed by GetCursorPos Access is denied (0x80070005).

The actual-width reduced force screen contains 54 assumed-input cases. The older quarter-fixture screen remains separately recorded.

The conditional nominal-setting material screen contains 36 cases. A sampled-stress margin of 3 would require up to 28.611 MPa under these assumptions. It uses the largest observed accepted-mesh centroid peak, not a proven continuum upper bound. Margins of 2 and 3 are illustrative; no measured yield, creep, fatigue or durability pass follows.

Additional V10 check: 42 sampled rigid slider poses cover six sizes at 5 mm intervals. All pass: True. Within-group pairs use rigid-transform invariance after their first check. This is not continuous swept-volume clearance or loaded contact. The 1296-case expanded dimensional budget does not establish manufacturing clearance: the guide/tongue 0.217157 mm nominal gap cannot guarantee clearance at assumed 0.2 mm normal error per part. No CAD revision was made. test_register.json lists unresolved tests and their prerequisites. Timing fields are elapsed wall time and may include interruption; they are not CPU benchmarks.

Further stop check: 12 guide/tongue contact searches locate an existing stop shoulder near 31 mm extension in all six sizes, roughly 1 mm beyond the intended range. The 36 imposed overtravel poses include blocking intersections at 40 to 60 mm. Separated imposed shapes beyond those intersections do not show a reachable extraction path. Stop strength, loaded retention and locking remain untested; no geometry was changed.
