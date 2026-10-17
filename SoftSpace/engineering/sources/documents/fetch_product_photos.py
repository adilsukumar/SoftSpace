"""Small sourced manufacturer photographs for the requested comparison documents."""
import urllib.request,json,re,html
from pathlib import Path
O=Path(__file__).parent/'images'
photos=[('sony','https://shopatsc.com/cdn/shop/files/A__2500x2500_L.jpg?v=1745490355'),('syga','https://syga.in/cdn/shop/files/61XJpmPW3wL_59efb040-3dbf-473a-b1db-a085e1e0fe32.jpg?v=1736625373')]
results=[]
for name,url in photos:
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(req,timeout=15) as resp:data=resp.read()
  path=O/(name+'.jpg');path.write_bytes(data);results.append({'file':str(path),'url':url,'bytes':len(data)})
 except Exception as e:results.append({'name':name,'error':str(e)})
(O/'product_photo_sources.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
