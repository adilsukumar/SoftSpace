from pathlib import Path
import json,subprocess,sys,os,hashlib
P=Path(__file__).parent;O=P/'engineering-v10-results';env=dict(os.environ,OPENBLAS_NUM_THREADS='1');cases=[]
if len(sys.argv)>1 and sys.argv[1]=='optimize':env['V10_OPTIMIZE_HIGH_ORDER']='1'
for size in ['adult_small','child_small','child_medium','child_large','adult_medium','adult_large']:
 meshes=[]
 for h in [2.0,1.5,1.25,1.0]:
  f=O/(size+'_h'+str(h)+'.json')
  if not f.exists():subprocess.run([sys.executable,str(P/'solid_band_v10.py'),size,str(h)],cwd=P,env=env,check=True)
  r=json.loads(f.read_text())
  if hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()!=r['source_sha256']:raise RuntimeError('Cached mesh source changed '+str(f))
  meshes.append(r)
  if len(meshes)>1:
   a,b=meshes[-2:];ds=abs(b['max_von_mises_centroid_MPa']/a['max_von_mises_centroid_MPa']-1);du=abs(b['guide_mean_x_displacement_mm']/a['guide_mean_x_displacement_mm']-1)
   print(json.dumps({'size':size,'mesh':h,'stress_change':ds,'guide_change':du}),flush=True)
   if ds<.05 and du<.05:break
 cases.append({'size':size,'source':meshes[-1]['source'],'source_sha256':meshes[-1]['source_sha256'],'meshes':meshes,'stress_relative_mesh_change':ds,'deflection_relative_mesh_change':du,'stress_gate_5pct':ds<.05,'deflection_gate_5pct':du<.05})
 j={'status':'complete' if len(cases)==6 else 'partial','source_kind':'STEP-only V10 geometry','cases':cases,'all_stress_comparisons_pass':all(c['stress_gate_5pct'] for c in cases),'all_deflection_comparisons_pass':all(c['deflection_gate_5pct'] for c in cases),'limits':['Changed guide, ideal load at z82mm, E2000MPa nu0.35','Quarter X/Y symmetry mirrors the front-only clamp bore; not the actual full-width rear wall','No actual locking or worn-assembly contact','No native Fusion archive unless separately built and verified']}
 (O/'solid_v10_summary.json').write_text(json.dumps(j,indent=2))
