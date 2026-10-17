"""Refine actual-width sampled stress separately from guide compliance.
No physical strength result follows from a numerical comparison pass.
"""
from pathlib import Path
import json,hashlib,math
import v10_full_width_band as b
P=Path(__file__).parent;O=P/'engineering-v10-results'
summary=json.loads((O/'full_width_sizes_summary.json').read_text())
assert summary['status']=='complete' and len(summary['cases'])==6
for c in summary['cases']:
 rows=c['meshes']
 def change():return abs(rows[-1]['max_von_mises_centroid_MPa']/rows[-2]['max_von_mises_centroid_MPa']-1)
 try:
  for h in [1.25,1.0]:
   if change()<.05:break
   if h>=rows[-1]['mesh_max_mm']:continue
   f=O/(c['size']+'_full_width_h'+str(h)+'.json')
   r=json.loads(f.read_text()) if f.exists() else b.run(c['size'],h)
   assert hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256']
   assert r['minimum_adaptive_Jacobian_mm3']>0 and r['relative_free_residual']<1e-5
   rx=r['reaction_sum_N'];assert math.sqrt((rx[0]+2)**2+rx[1]**2+rx[2]**2)<1e-5
   rows.append(r)
 except Exception as e:
  c['stress_refinement_failure']=str(e)
  (O/(c['size']+'_actual_width_stress_refinement_failure.json')).write_text(json.dumps({'status':'failed numerical refinement attempt','size':c['size'],'error':str(e),'completed_meshes_mm':[r['mesh_max_mm'] for r in rows],'limit':'No physical failure or strength pass follows.'},indent=2))
 c['compliance_relative_mesh_change']=abs(rows[-1]['compliance_mm_per_N']/rows[-2]['compliance_mm_per_N']-1)
 c['compliance_gate_5pct']=c['compliance_relative_mesh_change']<.05
 c['stress_relative_mesh_change']=change();c['stress_gate_5pct']=change()<.05
 (O/(c['size']+'_full_width_summary.json')).write_text(json.dumps(c,indent=2))
 summary['all_compliance_comparisons_pass']=all(v['compliance_gate_5pct'] for v in summary['cases'])
 summary['all_available_stress_comparisons_pass']=all(v.get('stress_gate_5pct',False) for v in summary['cases'])
 summary['stress_refinement_status']='complete' if all('stress_gate_5pct' in v for v in summary['cases']) else 'partial'
 (O/'full_width_sizes_summary.json').write_text(json.dumps(summary,indent=2))
 print(json.dumps({'size':c['size'],'stress_change':c['stress_relative_mesh_change'],'stress_pass':c['stress_gate_5pct'],'compliance_pass':c['compliance_gate_5pct']}),flush=True)
print(json.dumps({'status':summary['stress_refinement_status'],'all_stress_pass':summary['all_available_stress_comparisons_pass']}),flush=True)
