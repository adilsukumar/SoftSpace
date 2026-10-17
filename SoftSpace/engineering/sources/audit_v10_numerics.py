from pathlib import Path
import json,hashlib,math
P=Path(__file__).parent;O=P/'engineering-v10-results';s=json.loads((O/'solid_v10_summary.json').read_text());rows=[]
groups=[('band',r,1) for c in s['cases'] for r in c['meshes']]
sl=O/'slider_compliance.json'
if sl.exists():groups += [('slider',r,2) for c in json.loads(sl.read_text())['cases'] for r in c['meshes']]
fw=O/('full_width_sizes_summary.json' if (O/'full_width_sizes_summary.json').exists() else 'adult_small_full_width_summary.json')
if fw.exists():
 full=json.loads(fw.read_text());full_cases=full.get('cases',[full]);groups += [('full_width_band',r,2) for c in full_cases for r in c['meshes']]
for group,r,F in groups:
 reaction=r['reaction_sum_N'];balance=math.sqrt((reaction[0]+F)**2+reaction[1]**2+reaction[2]**2)
 j={'group':group,'size':r.get('size'),'extension_mm':r.get('extension_mm'),'mesh_mm':r['mesh_max_mm'],'positive_jacobians':r['minimum_quadrature_jacobian_mm3']>0,'free_residual_below_1e_5':r['relative_free_residual']<1e-5,'reaction_error_N':balance,'positive_energy':r['strain_energy_Nmm']>0,'source_hash_matches':hashlib.sha256(Path(r['source']).read_bytes()).hexdigest()==r['source_sha256']}
 quality=O/('mesh_quality_'+r.get('size','')+'_h'+str(r['mesh_max_mm'])+'_3d.json') if group=='band' else None
 if quality and quality.exists():j['adaptive_Jacobian_pass']=json.loads(quality.read_text())['pass']
 if group in ['slider','full_width_band']:j['adaptive_Jacobian_pass']=r.get('minimum_adaptive_Jacobian_mm3',0)>0
 j['pass']=all(j[k] for k in ['positive_jacobians','free_residual_below_1e_5','positive_energy','source_hash_matches']) and balance<1e-5 and j.get('adaptive_Jacobian_pass',True);rows.append(j)
full_status=json.loads(fw.read_text())['status'] if fw.exists() else 'not run'
out={'status':'complete' if s['status']=='complete' and full_status=='complete' else 'partial','full_width_refinement_status':full_status,'mesh_checks':rows,'all_available_pass':all(r['pass'] for r in rows),'limits':['Algebra and source checks only; not physical verification or absolute discretization error']}
out['quarter_sampled_stress_comparisons_pass']=s.get('all_stress_comparisons_pass',False)
out['actual_width_stress_refinement_status']=full.get('stress_refinement_status','not recorded') if fw.exists() else 'not recorded'
out['actual_width_sampled_stress_comparisons_pass']=full.get('all_available_stress_comparisons_pass',False) if fw.exists() else False
out['limits'].append('Completed checks of accepted solutions do not imply that all pending refinement studies or physical tests have passed.')
(O/'numerical_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'status':out['status'],'mesh_checks':len(rows),'all_pass':out['all_available_pass']}))
