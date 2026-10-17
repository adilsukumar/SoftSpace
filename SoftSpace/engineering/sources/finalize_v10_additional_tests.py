from pathlib import Path
import json,hashlib,subprocess,sys
P=Path(__file__).parent;O=P/'engineering-v10-results';D=P/'documents'
travel=json.loads((O/'intermediate_travel_audit.json').read_text());assert travel['status']=='complete' and travel['pose_count']==42
tol=json.loads((O/'tolerance_budget_expanded.json').read_text());assert tol['case_count']==1296
rows=[
 ('Native CAD and archive checks','Recorded pass for six archives and 18 STEP poses','Geometry evidence only'),
 ('Intermediate travel','Pass' if travel['all_pass'] else 'Fail','42 sampled rigid poses; not a continuous sweep or loaded contact'),
 ('Dimensional tolerance','Not established','Guide to tongue loses positive clearance at assumed 0.2 mm error per part'),
 ('Band stress and displacement refinement','Recorded chosen 5 percent comparisons pass for six sizes','Assumed linear materials and ideal fixtures'),
 ('Headband force','Two recorded 54 case screens','Reduced assumed band slider foam models; not measured worn forces'),
 ('Lock clamp and end stops','Input and modelling required','Need threads torque friction retention and wear'),
 ('Full worn contact','Input and solver work required','Measured heads nonlinear foam cover skin joints and glasses'),
 ('Foam cover and band material behaviour','Physical input required','Compression recovery stretch friction strength creep and fatigue'),
 ('Acoustics and music leakage','Measured geometry properties and laboratory tests required','Earlier cavity model is not a real seal or Sony acoustic result'),
 ('Heat moisture and cleaning','Physical input and sample tests required','Earlier assumed cases included saturation'),
 ('Sony mount and ANC compatibility','User measurements and sample tests required','User owns WH CH720N and will measure later'),
 ('Comfort and sensory acceptance','Voluntary wearer trials required','No simulation can establish individual preference or perceived comfort'),
 ('Cost and production yield','Supplier evidence required','No supplier quote or demonstrated manufacturing tolerance')]
if (O/'stop_onset_audit.json').exists():
 stop=json.loads((O/'stop_onset_audit.json').read_text());over=json.loads((O/'overtravel_audit.json').read_text())
 assert stop['case_count']==12 and over['case_count']==36
 for i,r in enumerate(rows):
  if r[0]=='Lock clamp and end stops':rows[i]=(r[0],'Geometric stop found; loaded validation open','12 contact brackets near 31 mm and 36 diagnostic overtravel poses; threads torque friction stop strength and wear remain open')
(O/'test_register.json').write_text(json.dumps({'updated':'2026-10-14','revision':'V10','tests':[dict(zip(['test','status','scope_or_prerequisite'],r)) for r in rows],'scope':'No physical tests performed by this batch; unfinished tests are explicitly open'},indent=2))
# Keep exact images from the previously inspected previews for regression comparison.
before={str(f.relative_to(D/'qa')):hashlib.sha256(f.read_bytes()).hexdigest() for f in (D/'qa').glob('*/page-*.png')}
(D/'qa'/'before_additional_tests_page_hashes.json').write_text(json.dumps(before,indent=2))
for script in ['build_documents.py','check_document_layout.py','verify_documents.py']:
 subprocess.run([sys.executable,str(D/script)],cwd=P,check=True)
after={str(f.relative_to(D/'qa')):hashlib.sha256(f.read_bytes()).hexdigest() for f in (D/'qa').glob('*/page-*.png')}
result={'unchanged_prior_page_images':sum(after.get(k)==v for k,v in before.items()),'changed_prior_page_images':[k for k,v in before.items() if after.get(k)!=v],'added_page_images':[k for k in after if k not in before],'scope':'Pixel hash comparison of approximate previews only; native Word remains unverified'}
(D/'qa'/'additional_tests_page_comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
