# Engineering record

[Project overview](../../README.md) Ã‚Â· [SoftSpace](../README.md) Ã‚Â· [SoftSpace Flex](../../SoftSpace%20Flex/README.md)

This directory contains a curated snapshot of saved research files. The publication manifest records original source hashes and published hashes. Text-only machine paths were normalized to `${WORKSPACE}` or `${USER_HOME}`; CAD and numerical arrays remain unchanged. Old technical filenames are preserved to connect results with their source geometry.

## Read first

| Location | Meaning |
| :--- | :--- |
| [evidence/engineering-v19-results/test_register.json](evidence/engineering-v19-results/test_register.json) | Current V19 evidence register, including limits and missing measurements |
| [evidence/engineering-v19-results/workstream_status.csv](evidence/engineering-v19-results/workstream_status.csv) | Completed finite checks versus open/model/input-dependent work |
| [evidence/engineering-v19-results/prototype-handoff](evidence/engineering-v19-results/prototype-handoff) | Nominal dimensions, proposal, sample forms and assembly-review sequence |
| [evidence/engineering-v19-results/quadratic-contact](evidence/engineering-v19-results/quadratic-contact) | Four accepted outward higher-order cases and their arrays/audits |
| [evidence/engineering-v19-results/quadratic-inward](evidence/engineering-v19-results/quadratic-inward) | Four accepted inward higher-order cases and their arrays/audits |
| [CAD](CAD) | Current V19 source assemblies; older CAD is in the complete bundle |
| [sources](sources) | Current simulation/CAD/report scripts plus historical utilities |
| [publication_manifest.json](publication_manifest.json) | Provenance and integrity mapping for the curated research snapshot |

Failures are retained. In particular, early linear mesh comparisons, iteration-limit trials, the inverted adult high-order mesh and the rejected exact-helix experiment must not be interpreted as accepted physical results.

## Verify the repository snapshot

From the repository root, using Python:

```console
python "SoftSpace/engineering/tools/verify_repository.py"
```

This checks file hashes, required research assets, DOCX ZIP integrity, selected recorded-audit structure, Python parsing, local documentation links and obvious credential patterns. It does not rerun the finite-element models or independently validate the physics.

## Prepare a workspace for the saved-result checks

The historical scripts expect a flat project directory. Create a fresh ignored workspace rather than editing archived results in place:

```console
python "SoftSpace/engineering/tools/prepare_workspace.py" --output .workspaces/v19
python -m pip install --target .workspaces/v19/solver-libraries -r SoftSpace/engineering/requirements-numerics.txt
cd .workspaces/v19
python verify_v19_quadratic.py
python verify_v19_quadratic.py engineering-v19-results/quadratic-inward
```

Preparation restores the expected file layout and rebases recorded workspace paths. The current inward study also hashes its original outward mesh archive; the mesh arrays are copied byte-for-byte.

The listed versions are recorded study dependencies, not a new clean-room reproducibility certification. Gmsh may require platform graphics/system libraries. CAD-generation and Open Cascade audit utilities additionally used `cadquery-ocp 7.8.1.1.post1` and `vtk 9.3.1` in the original Windows environment. Some historical source files control a local Fusion session or use Windows-specific document/font paths; they are retained as research history, not advertised as portable entry points.

The two commands above **reassemble equations and audit saved solutions**. They do not run new physical tests, calibrate material laws or resolve a real bolt, bearing, thread or full worn headset. They can use substantial memory. The original laptop had 16 GB RAM; this is a recorded condition, not a guaranteed requirement or upper bound.

## Reports and evidence categories

Both living reports share one evidence date and must be updated together after meaningful changes. Their source is in [sources/documents](sources/documents). Public copies are in each product's `reports` folder. The published reports use the SoftSpace and SoftSpace Flex names; historical filenames remain in provenance records.

Keep these categories separate:

- **Geometry check:** file validity, sampled motion, reimport or intersection query.
- **Numerical calculation:** assumptions, equations, loads, solver/convergence and mesh sensitivity.
- **Manufacturer reference:** published properties or product statements; not measurements of this prototype.
- **Physical measurement:** traceable samples, methods, conditions, uncertainty and repetitions.
- **Wearer feedback:** individual, voluntary observations; not universal sensory acceptance.

Native Word rendering was unavailable in the recorded environment. The reports passed structural checks and approximate page-preview review; native Word pagination remains unverified. No supplier quotation, physical comfort pass, acoustic qualification or manufacturing release is implied by this publication.

## Historical binary archive

The [complete research bundle](https://github.com/adilsukumar/SoftSpace/releases/download/v19-research/SoftSpace_Complete_V19_Research.zip) preserves older CAD and raw arrays. Git retains their source scripts, summaries and failure records, plus all eight current higher-order solution arrays. To replay older routes, use the full bundle. The publication manifest records the bundle hash and the files retained in Git.

## V20 pre prototype evidence

Read [the bounded study and purchase recommendation](evidence/engineering-v20-results/README.md). The new pad bodies are reference geometry; the standalone V19 CAD is unchanged. `v20_preprototype_screen.py`, `build_v20_flex_reference.py` and `verify_v20_screen.py` can be run in a prepared workspace. New CAD is also retained under `engineering-v20-results/CAD` so saved file paths resolve. The complete V19 archive is an older snapshot and does not include this increment.

## V21 additional software review

Read [the review, failures and remaining work](evidence/engineering-v21-results/README.md). New scripts run in a prepared workspace. Raw V19 solutions are unchanged. The four new finer equilibrium solves, stress recovery, hotspot diagnostics and six compact poses are recorded separately. Neither the older immutable release nor V20 closes these new issues.

<!-- BLOCK_SOLVER:BEGIN -->
## Joint solver update 26 October 2026

The lower memory V26B pilot reduced stored factor entries from 92.64 to 27.78 million. Its second linear solve failed the unchanged accuracy gate, so there is **no accepted new strength result**. Both reports retain this failure. Full headset validation and exact Sony replacement fit remain open.
<!-- BLOCK_SOLVER:END -->

<!-- MATERIAL_LOADING:BEGIN -->
## Named material loading screen 26 October 2026

The [new material screen](evidence/material-screen-2026-10-26/README.md) uses source-checked loading points for eight named Confor grades rather than an assumed foam law. Of 1152 cases, 559 are solved within the published strain range and 593 are left outside the supported domain. Cases with higher local pressure are retained. One 8 N reference gives about 35 percent lower calculated glasses-strip pressure with CF-40M in a CF-42M ring; this is a simplified uncovered 12.7 mm reference, **not pain relief, seal, fit or product validation**.

Both illustrated reports are updated together and native Word layouts checked. Grade availability and price in India are unverified. The loading-input gap has advanced; unloading, recovery, cover, mounting and full product gates remain open. Source URLs, hashes, extracted facts and all scenario results are published; manufacturer PDFs remain local for source checking.
<!-- MATERIAL_LOADING:END -->

<!-- VALIDATION_DECISION:BEGIN -->
## Software validation decision

**Neither product has passed full software validation or is approved for manufacturing release.** The evidence assessment is complete; outstanding tests are not complete. SoftSpace has unresolved joint strength and full assembly validation. Flex lacks verified Sony mounting geometry. Both routes still need qualified inputs and complete contact, sound, heat and durability models; wearer acceptance needs people.

The [decision and requirement register](evidence/validation-decision/README.md) identifies existing evidence, missing inputs and acceptance requirements. Both Word reports contain the same final decision. This review reused saved results and ran no new simulation campaign. Further computation should address a specific changed design or newly qualified input; repeated assumed runs cannot supply missing measurements or mounting dimensions.
<!-- VALIDATION_DECISION:END -->

<!-- V26:BEGIN -->
## V26 rounded local joint trials

Two separate local CAD candidates investigate the failed stress predictions. Candidate A meets the fork mesh comparison but still fails the tongue checks, and introduces folding interference at two sampled angles. Candidate B relieves that corner and passes all 25 local folding samples plus both wearing-stop checks. These two-part candidates are **not integrated full headset releases**. Read the [CAD, raw fields and failure records](evidence/engineering-v26-results/README.md).

Candidate B has **no accepted strength field**: low-memory solvers failed their accuracy gates, and the stronger attempt was stopped at a five-minute operational cap with about 8.7 GB committed. That stop does not prove physical weakness or mathematical divergence. Both illustrated Word reports are updated together and checked in native Word. The [remaining requirements](evidence/engineering-v26-results/remaining_test_register.csv) still apply to both projects. **Full product software and physical validation remain open.** Sony fit, comfort, sound, heat and durability gains remain unproved.
<!-- V26:END -->

<!-- V25:BEGIN -->
## V25 surface calculation investigation

Three new child-large outward reference calculations test quadratic surface contact and consistent surface loads. All numerical consistency controls pass. Increasing integration accuracy changes sampled peaks by less than 0.4 percent, but mesh changes still give roughly 6 to 19 percent differences: **0 of 4 mesh comparisons pass** the chosen 5 percent check. This candidate does not fix reliable stress prediction or establish strength. Read the [pilot evidence and raw fields](evidence/engineering-v25-results/README.md).

Both illustrated Word reports are updated together and checked in native Word. A [manufacturer input review](evidence/engineering-v25-results/manufacturer_input_review.json) records specific BASF, Rogers and Sony sources; it does not turn typical data into a complete foam law or verified Sony mount. The [remaining requirements](evidence/engineering-v25-results/remaining_test_register.csv) still include actual joint details, material condition, cushion contact, exact mounting, sound, heat and durability. **Neither product has full software or physical sign off.** No product performance or prototype purchase release is claimed.
<!-- V25:END -->

<!-- V24:BEGIN -->
## V24 corrected joint verification

Four new corrected virtual-spacer reference calculations use finer 1.5 mm target meshes on both joint families and load directions. Only 2 of 16 refined peak comparisons meet the fixed 5 percent limit. Their [raw results and stress comparisons](evidence/engineering-v24-results/README.md) retain every failed comparison. Numerical consistency does not establish reliable whole-part stress or physical strength.

Primary CAD source loaders now resolve the moved workspace by recorded hashes. Four exact historical V12 sources are restored separately; all 304 recorded source path/hash pairs match. Both illustrated Word reports are updated together. Read the [remaining test register](evidence/engineering-v24-results/remaining_test_register.csv): actual material curves, detailed joints, Sony mounting, sound and heat inputs remain unresolved. This completed numerical campaign is **not all product software testing completed**. No physical validation or product performance claim is added.
<!-- V24:END -->

<!-- V23:BEGIN -->
## V23 corrected joint verification

Eight new corrected virtual-spacer reference calculations cover two joint families, two meshes and both load directions. Their [raw results and stress comparisons](evidence/engineering-v23-results/README.md) retain every failed comparison. Numerical consistency does not establish reliable whole-part stress or physical strength.

Both illustrated Word reports are updated together. Read the [remaining test register](evidence/engineering-v23-results/remaining_test_register.csv): actual material curves, detailed joints, Sony mounting, sound and heat inputs remain unresolved. This completed numerical campaign is **not all product software testing completed**. No physical validation or product performance claim is added.
<!-- V23:END -->

<!-- V22:BEGIN -->
## V22 numerical confidence checks

[V22 evidence and reproduction notes](evidence/engineering-v22-results/README.md) include raw fields, operator checks, material assumptions, targeted mesh comparisons and the full test register. The original contact model and proposed objective virtual-spacer reference are identified separately. Read the exact converged statuses and limits; no globally bounded stress or physical qualification is claimed.
<!-- V22:END -->

