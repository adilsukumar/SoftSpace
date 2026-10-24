from pathlib import Path
import ast,sys,hashlib,json,zipfile,os
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));import numpy as np;import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
O=P/'engineering-v23-results';summary=json.loads((O/'review_status.json').read_text());comparisons=summary['stress_comparisons'];assert summary['all_numerical_controls_pass']
s=(P/'v23_review.py').read_text();start=s.index("selected=[r for r in comparisons");end=s.index("text=f'''# V23",start);exec(s[start:end])
# Replace only the newly added V23 image, preserving older media and all XML.
D=P/'documents';status=json.loads((D/'document_status.json').read_text());image=(D/'images/V23_corrected_mesh.png').read_bytes()
for row in status['documents']:
 f=Path(row['path']);temp=f.with_suffix('.v23.tmp');matches=0
 with zipfile.ZipFile(f) as zin,zipfile.ZipFile(temp,'w') as zout:
  xml=zin.read('word/document.xml').decode();rels=zin.read('word/_rels/document.xml.rels').decode()
  from lxml import etree
  root=etree.fromstring(zin.read('word/document.xml'));ns={'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
  ids=[]
  for drawing in root.xpath('//wp:inline',namespaces=ns):
   if 'Same corrected reference equations' in drawing.xpath('./wp:docPr',namespaces=ns)[0].get('descr',''):ids.extend(drawing.xpath('.//a:blip/@r:embed',namespaces=ns))
  relroot=etree.fromstring(zin.read('word/_rels/document.xml.rels'));targets=['word/'+r.get('Target') for r in relroot if r.get('Id') in ids];assert len(targets)==1
  for info in zin.infolist():
   data=zin.read(info.filename)
   if info.filename in targets:data=image;matches+=1
   zout.writestr(info,data)
 assert matches==1;os.replace(temp,f);row['sha256']=hashlib.sha256(f.read_bytes()).hexdigest();row['bytes']=f.stat().st_size
(D/'document_status.json').write_text(json.dumps(status,indent=2))
print('V23 chart legend moved above bars in both reports')
