from pathlib import Path
import json,zipfile,hashlib
p=Path(__file__).parent;o=p/'engineering-v6-results'
with zipfile.ZipFile(p/'EarDefender_V6_CAD_and_Evidence.zip') as z:
 assert z.testzip() is None
 manifest=json.loads(z.read('cad_manifest.json'))
 assert len(manifest)==30
 for item in manifest:
  data=z.read('cad/'+item['file']);assert len(data)==item['bytes'];assert hashlib.sha256(data).hexdigest()==item['sha256']
 for name in ['results/band_3d.png','results/acoustic_proxy.png','results/review.html','results/REVIEW.md','results/market_sample.csv','results/BOM_geometry.csv','results/acoustic_3d_verification.json','results/solid_3d_summary.json']:assert name in z.namelist()
for filename in ['solid_band_3d.py','acoustic_3d_v6.py','CushionNext/EngineeringV6.py','CushionNext/RepairV6Exports.py']:
 compile((p/filename).read_text(),filename,'exec')
print('Package integrity, 30 CAD hashes, required artifacts and Python syntax passed')
