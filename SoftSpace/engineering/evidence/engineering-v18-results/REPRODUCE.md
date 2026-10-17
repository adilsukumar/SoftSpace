# Reproducing V18 checks

Use the existing EarDefenderProject working directory. environment.json records this run. Scientific packages are in solver-libraries; OCP packages are in cad-validation-libraries. The archive records evidence and scripts but does not bundle those third party libraries or a Fusion installation.

If restoring from the cumulative ZIP, restore sources/*.py to a project root, evidence/engineering-v*-results folders to that root, saved CAD files to the original basenames in that root, document sources to documents and images to documents/images. Historical JSON sources contain absolute paths; relocate and rehash identity records deliberately before use, rather than disabling source identity checks. Keep originals unchanged for audit.

Use a compatible Python environment and run each heavy finite-element solve in a fresh process with one BLAS thread. Do not run several large meshes together on this laptop.

1. run_v18_sizes.py builds six nominal candidates and audits finite motion and outward stop queries. It replaces generated candidate STEP files, whose resulting hashes must be used by later checks.
2. complete_v18_torque.py reads current saved solids and runs the assumed density and proposed direct torque comparison. v18_equivalence.py tests listed component identity. The child Band common operation did not establish identity; band fixtures are independently recomputed.
3. export_v18_poses.py writes and independently reimports18 saved poses. render_v18_candidates.py and render_v18_details.py draw actual source surfaces and sections.
4. run_v18_fixtures.py computes two meshes for each stop family and initial adult band meshes. refine_v18_bands.py continues bands until both chosen5percent comparisons pass or the finite mesh list ends. Existing result reuse must only occur when source hashes match; for a rebuild, preserve and move old output records before rerunning.
5. summarize_v18_checks.py verifies source identity and saved array equations and writes the revision-specific test register. Physical records are blank.
6. documents/build_documents.py rebuilds both living Word files together, refusing an unexpected user edit. Native Word pagination remains unverified because the packaged renderer is unavailable here. check_document_layout.py produces approximate previews, which need visual review before record_preview_review.py is used.

The small-displacement elastic component fixtures, finite rigid poses and static uniform-friction calculation do not replace a coupled joint solution or physical product tests. Source scripts and the saved rejected trials preserve the known limits.

## Additional fork fixture commands

run_v18_forks.py computes the initial two meshes for each family. The child peak-stress comparison exceeded5percent. Additional child meshes at1.25and1.0mm were solved with v18_fork_fixture.py. close_v18_component_testing.py independently verifies all six added saved arrays,compares the last meshes and updates the remaining-input matrix. render_v18_fork_results.py draws actual undeformed FE boundaries. The final comparison passes the chosen gate,but the complete assembled joint remains unsolved.
