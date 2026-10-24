# Engineering record

[Project overview](../../README.md) Â· [SoftSpace](../README.md) Â· [SoftSpace Flex](../../SoftSpace%20Flex/README.md)

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

<!-- V22:BEGIN -->
## V22 numerical confidence checks

[V22 evidence and reproduction notes](evidence/engineering-v22-results/README.md) include raw fields, operator checks, material assumptions, targeted mesh comparisons and the full test register. The original contact model and proposed objective virtual-spacer reference are identified separately. Read the exact converged statuses and limits; no globally bounded stress or physical qualification is claimed.
<!-- V22:END -->

