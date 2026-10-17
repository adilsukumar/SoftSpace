# Reproducing the loaded pin assessment

Use the bundled Python runtime and the saved solver-libraries and cad-validation-libraries paths. Run from the project directory. The supplied source identities are required; do not substitute another STEP without repeating geometry extraction and verification.

1. extract_v17_guide_geometry.py checks both pilot sources and extracts guide intervals.
2. run_v17_contact_return.py runs the analytic and reversal controls, 90 contact cases, 1080 friction comparisons and selected mesh refinements. It saves six array archives.
3. v17_spring_tradeoff.py screens 300 nominal spring designs under the explicitly recorded illustrative bounds.
4. render_v17_contact_results.py makes the diagnostic figure from saved results.
5. close_v17_digital_assessment.py records the production hold, completion matrix and remaining dependencies. It preserves the earlier pilot evidence.
6. verify_v17_closeout.py independently checks source hashes, saved-array force and moment balance, finite values and the unreleased product status. It creates a blank loaded-pin record only if that file does not exist.
7. Rebuild BOTH Word reports using their SHA guard, preserve history, render available previews and inspect changed pages. Native Word pagination is unverified in this environment because the bundled LibreOffice renderer is unavailable.
8. Preserve the document quality record and add the latest assessment state before packaging. Run package_v17_study.py for archive integrity verification.

The assessment does not provide a manufactured spring specification or a validated product. It deliberately leaves actual friction, guide stiffness, material properties, fasteners, complete 3D contact, sensory acceptance, physical acoustics, durability and cost unqualified. No physical tests or supplier messages were performed.

The first contact mesh contained a near-duplicate 0.001 mm interval. Its poor conditioning prevented convergence. The accepted mesher divides exact geometry intervals separately. The final calculations use that corrected code, with the analytic control and equilibrium checks passing. No result from the failed mesh is treated as a pass.
