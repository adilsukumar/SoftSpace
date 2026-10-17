from pathlib import Path
f=Path(__file__).parent/'package_v10_verified.py';s=f.read_text(encoding='utf-8')
start=s.index("review='''")
end=s.index("(O/'REVIEW.md').write_text",start)
replacement='''full=json.loads((O/'adult_small_full_width_summary.json').read_text())
full_sizes=json.loads((O/'full_width_sizes_summary.json').read_text()) if (O/'full_width_sizes_summary.json').exists() else None
full_force=json.loads((O/'adjustment_force_full_width.json').read_text()) if (O/'adjustment_force_full_width.json').exists() else None
strength=json.loads((O/'conditional_strength_screen.json').read_text()) if (O/'conditional_strength_screen.json').exists() else None
quarter_pass=sum(c['stress_gate_5pct'] for c in stress['cases'])
actual_changes=[abs(c['meshes'][-1]['max_von_mises_centroid_MPa']/c['meshes'][-2]['max_von_mises_centroid_MPa']-1) for c in full_sizes['cases']] if full_sizes else []
actual_pass=sum(v<.05 for v in actual_changes)
review=f"""# V10 CAD candidates and recorded numerical checks

Updated 14 October 2026. This package records concept geometry and calculations. It does not establish comfort, sound reduction, sensory acceptance, pain prevention, market superiority, zero leakage or production readiness.

All six native Fusion candidates were exported as six F3D archives and 18 nominal/endpoint STEP poses. Each STEP contains 28 solids and passes the all-body intersection audit at a 0.01 mm3 overlap tolerance. Each F3D was reopened in Fusion and its V10 component contained 28 solids. Native and local band shapes agree within the 0.01 mm3 volume comparison tolerance. Source hashes are saved.

The wider V9 audit found shortest-setting guide/pivot-pin clashes in all six sizes and extra knob/fork clashes in the child sizes. Earlier selected-body checks had omitted these parts. V10 trims the guide bottoms by 2 mm and raises the clamp bores and knobs by 4 mm. The intended slider range remains 0 to 30 mm. Nominal selected gaps are 0.217157 mm for guide/tongue, 1 mm for guide/pin and 0.5 mm for knob/fork. These are CAD gaps, not proven factory tolerances. The clamp reach audit checks 84 positions geometrically; it does not prove locking or retention.

Changed-guide quarter-band sampled stress comparisons meet the chosen 5% limit in {quarter_pass} of six sizes. All six guide-displacement comparisons meet that limit. The earlier adult-medium 8.37% and 18% changes remain in history. The quarter model mirrors the front-only bore onto the rear wall. Its nominal geometric approximation remains even after numerical refinement.

The separate actual-width ideal-fixture study covers {len(actual_changes)} of six sizes. Its sampled stress comparisons meet 5% in {actual_pass} of those sizes. Guide compliance and stress are reported separately; displacement stability alone is not peak-stress stability. The actual-width model retains the real front-only bore, but its crown restraints and surface loading differ from the quarter model. It does not isolate symmetry error or solve the worn assembly.

Slider segment checks use consistent surface loads at 0, 15 and 30 mm adjustment. The reduced force screens combine ideal band/slider compliance with scalar foam/cover contact and synthetic heads. They omit real guide rotations, clamp friction, pin bearing and scalp contact. All material properties and mounting offsets remain assumed. They do not establish a comfort or sound-seal threshold.

The invalid first adult-large quarter mesh and earlier memory, export, load and solver failures are retained. Accepted element-quality, residual and force-balance checks are numerical evidence, not physical verification. Last-two-mesh peak comparisons are not absolute continuum error bounds.

Sony WH-CH720N is the selected replacement-pad host. The user owns it and will measure its mount later. The generic pad is not claimed compatible. Host force, mounting dimensions, driver/vent geometry, incoming noise, outgoing music, response, ANC and wearer comfort remain untested. Existing replacement-pad competitors are recorded in both reports; no superiority or confirmed Indian market absence is claimed.

Remaining work includes measured foam/cover/band properties, real locking and retention, joints and worn-head contact, manufacturing tolerances, thermal/moisture checks, calibrated acoustic comparisons and voluntary sensory feedback. These dependencies prevent a finished commercial-product claim.

Both Word reports were updated together. Their structure and approximate previews were checked. Native Word pagination remains unverified because desktop control returned unavailable elements and failed to activate the captured window.
"""
if full_force:
 review+=f"\\nThe actual-width reduced force screen contains {full_force['case_count']} assumed-input cases. The older quarter-fixture screen remains separately recorded.\\n"
if strength:
 review+=f"\\nThe conditional nominal-setting material screen contains {strength['case_count']} cases. A sampled-stress margin of 3 would require up to {strength['minimum_strength_for_margin_3_over_all_nominal_cases_MPa']:.3f} MPa under these assumptions. It uses the largest observed accepted-mesh centroid peak, not a proven continuum upper bound. Margins of 2 and 3 are illustrative; no measured yield, creep, fatigue or durability pass follows.\\n"
'''
s=s[:start]+replacement+s[end:]
compile(s,str(f),'exec');f.write_text(s,encoding='utf-8')
print('Package review now reports fixture scopes and passes dynamically.')
