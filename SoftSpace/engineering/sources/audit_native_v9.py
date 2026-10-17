from pathlib import Path
import json, math, hashlib
P=Path(__file__).parent;O=P/'engineering-v9-results'
v=json.loads((O/'native_verification.json').read_text());s=json.loads((O/'solid_v9_summary.json').read_text())
checks=[]
for c in s['cases']:
    source=Path(c['source'])
    for r in c['meshes']:
        residual=r['relative_free_residual']
        reaction=r['reaction_sum_N']
        checks.append({'size':c['size'],'mesh_mm':r['mesh_max_mm'],
            'positive_jacobians':r['minimum_quadrature_jacobian_mm3']>0,
            'free_residual_below_1e_5':residual<1e-5,
            'reaction_balance_error_N':math.sqrt((reaction[0]+1)**2+reaction[1]**2+reaction[2]**2),
            'positive_strain_energy':r['strain_energy_Nmm']>0,
            'finite_positive_stress':math.isfinite(r['max_von_mises_centroid_MPa']) and r['max_von_mises_centroid_MPa']>0,
            'recorded_source_hash_matches':hashlib.sha256(source.read_bytes()).hexdigest()==c['source_sha256']})
for r in checks:
    r['pass']=all(r[k] for k in ['positive_jacobians','free_residual_below_1e_5','positive_strain_energy','finite_positive_stress','recorded_source_hash_matches']) and r['reaction_balance_error_N']<1e-5
beam=json.loads((O/'verification_beam_h1.5.json').read_text())
j={'status':'complete' if len(s['cases'])==6 else 'partial','all_available_pass':all(c['pass'] for c in checks),'checks':checks,'beam_code_check':{'analytic_mm':beam['beam_with_shear_mm'],'calculated_mm':beam['tip_deflection_mm'],'relative_difference':beam['relative_beam_difference'],'comparison_5pct_pass':beam['relative_beam_difference']<.05},'limitation':'Algebra, mesh and source checks only; physical validation and absolute discretization error are not established.'}
(O/'numerical_audit.json').write_text(json.dumps(j,indent=2));print(json.dumps({'status':j['status'],'mesh_checks':len(checks),'all_pass':j['all_available_pass']}))
