import os,sys,subprocess,json,hashlib
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v18-results';records=[]
for size in ['adult_small','adult_medium','adult_large','child_small','child_medium','child_large']:
 meshes=[]
 for h in [2.5,2.0,1.5,1.25,1.0]:
  target=O/(size+'_full_width_h'+str(h)+'.json')
  if not target.exists():
   with (O/(size+'_band_refine_'+str(h)+'.log')).open('w') as log:
    r=subprocess.run([sys.executable,'v18_band_fixture.py',size,str(h)],cwd=P,env=dict(os.environ,OPENBLAS_NUM_THREADS='1'),stdout=log,stderr=subprocess.STDOUT)
   assert r.returncode==0
  row=json.loads(target.read_text());assert hashlib.sha256(Path(row['source']).read_bytes()).hexdigest()==row['source_sha256'],'Preserve stale results before rerunning';meshes.append(row)
  if len(meshes)>1:
   disp=abs(meshes[-2]['guide_weighted_x_displacement_mm']/row['guide_weighted_x_displacement_mm']-1);stress=abs(meshes[-2]['max_von_mises_centroid_MPa']/row['max_von_mises_centroid_MPa']-1)
   if max(disp,stress)<.05:break
 records.append(dict(size=size,meshes=meshes,last_displacement_change_fraction=disp,last_stress_change_fraction=stress,chosen_5percent_comparison_pass=max(disp,stress)<.05));(O/'band_refinement.json').write_text(json.dumps(dict(cases=records,complete=False),indent=2))
(O/'band_refinement.json').write_text(json.dumps(dict(cases=records,complete=True,all_chosen_comparisons_pass=all(r['chosen_5percent_comparison_pass'] for r in records)),indent=2))
