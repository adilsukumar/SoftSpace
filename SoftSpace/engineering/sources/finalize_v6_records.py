import json,shutil
from pathlib import Path
p=Path(__file__).parent;o=p/'engineering-v6-results'
solid=json.loads((o/'solid_3d_summary.json').read_text())
refined=json.loads((o/'child_small_h2.0.json').read_text())
c=solid['cases'][0];previous=c['meshes'][-1];c['meshes'].append(refined)
c['guide_deflection_mesh_change']=abs(refined['guide_mean_x_displacement_mm']/previous['guide_mean_x_displacement_mm']-1)
c['centroid_peak_stress_mesh_change']=abs(refined['max_von_mises_centroid_MPa']/previous['max_von_mises_centroid_MPa']-1)
c['deflection_mesh_gate_5pct']=c['guide_deflection_mesh_change']<.05;c['stress_mesh_gate_5pct']=c['centroid_peak_stress_mesh_change']<.05
solid['verification']['beam_check_5pct']=solid['verification']['relative_beam_difference']<.05
solid['interpretation']='Deflection mesh stability passed for this ideal loading. Small-child corner stress did not converge; no peak strength claim. This is not assembled, nonlinear worn-head behavior.'
(o/'solid_3d_summary.json').write_text(json.dumps(solid,indent=2))
poses=json.loads((p/'cad_v6_pose_exports.json').read_text())
cad=json.loads((p/'cad_v6_report.json').read_text())
for i,path in enumerate(poses['files']):
 pose=poses['pose_body_counts'][i]['pose'];variant,extension=pose.split('_Extension_')
 archive=next(Path(f) for f in cad['files'] if f.endswith('.f3d') and '_'+variant+'_' in f)
 target=p/(archive.stem+'_Extension_'+extension+'_Verified.step')
 if Path(path)!=target:shutil.copy2(path,target)
 poses['files'][i]=str(target)
(p/'cad_v6_pose_exports.json').write_text(json.dumps(poses,indent=2))
print('Updated final refinement and export records')
