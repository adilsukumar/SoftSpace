"""Fetch the exact public source PDFs for reproducing the named-material screen."""
from pathlib import Path
import json,hashlib,urllib.request,urllib.parse
P=Path(__file__).resolve().parent;O=P/'material-screen-2026-10-26';rows=json.loads((O/'sources.json').read_text())
for r in rows:
 if r['id'] not in ['Trelleborg_Confor','Rogers_4701_40_battery']:continue
 assert urllib.parse.urlsplit(r['url']).hostname in ['www.trelleborg.com','www.rogerscorp.com']
 f=O/(r['id']+'.pdf')
 if f.exists():data=f.read_bytes()
 else:
  data=urllib.request.urlopen(r['url'],timeout=30).read(2000001);assert len(data)<=2000000 and data.startswith(b'%PDF')
 assert hashlib.sha256(data).hexdigest()==r['sha256'],'Manufacturer source changed; review before using'
 if not f.exists():f.write_bytes(data)
 print(r['id'],'source hash verified')
