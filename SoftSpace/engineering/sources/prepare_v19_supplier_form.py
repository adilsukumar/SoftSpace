"""Prepare a local quotation form; do not contact a supplier."""
import csv,json
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v19-results';D=O/'prototype-handoff';rows=[]
for f in sorted((O/'final-CAD').glob('*_cad_report.json')):
 r=json.loads(f.read_text())
 for name,volume in r['part_volumes_mm3'].items():
  candidate=('Sample compression curves required; no final foam' if any(x in name for x in ['Foam','GlassesZone','Liner','CrownPad']) else 'Continuous skin-contact cover; grade stretch friction permeance and bond data required' if 'Cover' in name else 'Catalogue disc 000600B; supplier confirmation required' if 'DiscSpring' in name else 'Metal candidate; grade certificate thread class process and locking proof required' if any(x in name for x in ['Bolt','Nut','BackupWasher','CupPin']) else 'Friction material sample and measured torque required' if 'FrictionWasher' in name else 'Unqualified structural material candidate; reference FE properties are not a grade release')
  rows.append(dict(size=r['size'],part=name,quantity_per_assembly=1,volume_mm3=volume,CAD_sha256=r['sha256'],material_request=candidate,supplier='',proposed_material_and_process='',tolerance_capability='',MOQ='',sample_cost_INR='',unit_cost_INR='',tooling_cost_INR='',lead_time_days='',data_sheet_and_lot='',quote_date='',status='No quotation obtained'))
target=D/'Supplier_quotation_request_BLANK.csv'
if not target.exists():
 with target.open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Local quotation form prepared; no supplier was contacted')
