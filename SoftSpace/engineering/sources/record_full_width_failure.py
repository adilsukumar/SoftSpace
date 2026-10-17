from pathlib import Path
import json
P=Path(__file__).parent;O=P/'engineering-v10-results';coarse=json.loads((O/'adult_small_full_width_h2.0.json').read_text())
result={'status':'incomplete refinement','size':'adult_small','meshes':[coarse],'failed_mesh_mm':1.5,'error':'ArrayMemoryError during CSR stiffness assembly: unable to allocate117 MiB for30677085 int32 indices. No finer solution was saved.','compliance_gate_5pct':False,'limits':coarse['limits']+['One coarse solution; no mesh refinement comparison pass','Other sizes have no complete actual-width fixture study']}
(O/'adult_small_full_width_summary.json').write_text(json.dumps(result,indent=2));print(result['status'])
