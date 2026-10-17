import json,hashlib,subprocess,sys
from pathlib import Path
P=Path(__file__).parent;D=P/'documents';O=P/'engineering-v19-results'
baseline=D/'qa/before_v19_page_hashes.json'
if baseline.exists():before=json.loads(baseline.read_text())
else:
 before={str(f.relative_to(D/'qa')):hashlib.sha256(f.read_bytes()).hexdigest() for f in (D/'qa').glob('*/page-*.png')};baseline.write_text(json.dumps(before,indent=2))
for script in ['build_documents.py','check_document_layout.py','verify_documents.py']:
 subprocess.run([sys.executable,str(D/script)],cwd=P,check=True)
after={str(f.relative_to(D/'qa')):hashlib.sha256(f.read_bytes()).hexdigest() for f in (D/'qa').glob('*/page-*.png')};comparison=dict(unchanged_prior_page_images=sum(after.get(k)==v for k,v in before.items()),changed_prior_page_images=[k for k,v in before.items() if after.get(k)!=v],added_page_images=[k for k in after if k not in before],scope='Approximate preview hashes, not native Word pagination');(D/'qa/additional_tests_page_comparison.json').write_text(json.dumps(comparison,indent=2))
s=json.loads((D/'document_status.json').read_text());r=json.loads((O/'test_register.json').read_text());s['latest_study']=dict(revision=r['revision'],source='engineering-v19-results/test_register.json',local_STEP_sizes=6,saved_poses=18,motion_sample_count=r['motion_sample_count'],joint_cases=len(r['joint_cases']),joint_array_audits=r['joint_array_audits'],quadratic_cases=len(r.get('quadratic_contact_model',{}).get('status',{}).get('cases',[])),quadratic_comparisons=r.get('quadratic_contact_model',{}).get('verification',{}).get('mesh_comparisons',[]),quadratic_inward_cases=len(r.get('quadratic_inward_model',{}).get('status',{}).get('cases',[])),quadratic_inward_comparisons=r.get('quadratic_inward_model',{}).get('verification',{}).get('mesh_comparisons',[]),physical_measurements=0,all_requested_computer_models_complete=False,product_complete=False,manufacturing_release=False,native_Fusion_revision='V10');(D/'document_status.json').write_text(json.dumps(s,indent=2));print(json.dumps(comparison,indent=2))
