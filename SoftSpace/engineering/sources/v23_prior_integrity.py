from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;O=P/'engineering-v23-results'
# Preserve previously published solution hashes as a regression check.
previous=json.loads((P/'engineering-v22-results/quadrature_mesh_audit.json').read_text())
checked={}
for r in previous['cases']:
 f=P/r['source'];actual=hashlib.sha256(f.read_bytes()).hexdigest();assert actual==r['source_sha256'];checked[str(f.relative_to(P))]=actual
for side in ['outward','inward']:
 r=json.loads((P/'engineering-v22-results/spacer_candidate_residual_check.json').read_text())
 for row in r['cases']:
  kind=row['kind'];label=('adult_fork_local_0.9_' if kind=='original' else 'objective_spacer_')+row['direction']+'.npz';f=P/'engineering-v22-results'/label;actual=hashlib.sha256(f.read_bytes()).hexdigest();assert actual==row['source_sha256'];checked[str(f.relative_to(P))]=actual
(O/'prior_field_integrity.json').write_text(json.dumps(dict(date='2026-10-24',unchanged_fields=len(checked),sha256=checked),indent=2))
print('Prior numerical fields unchanged:',len(checked))
