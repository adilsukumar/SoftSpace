"""Independent Boolean checks of STEP-only candidate, discrete slider poses."""
import sys,json
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import gmsh
sizes=json.loads((P/'lower-crown-recipes.json').read_text())
if isinstance(sizes,dict):sizes=sizes['recipes']
results=[]
for r in sizes:
 size=r['name'];path=P/('OwnPassiveDefender_V9Local_'+size+'.step')
 if not path.exists():continue
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);o=gmsh.model.occ;o.importShapes(str(path));o.synchronize()
 bodies=gmsh.model.getEntities(3);bands=[];tongues=[]
 for dt in bodies:
  a,b,c,e,f,g=gmsh.model.getBoundingBox(*dt)
  if a<0<e and 70<c<100 and g>125 and f-b<30:bands.append(dt)
  if 60<c<63 and 133<g<135 and 15<f-b<17 and 3<e-a<8:tongues.append(dt)
 assert len(bands)==1 and len(tongues)==2,(size,bands,tongues)
 def overlap(first,second,shift=0):
  aa=o.copy([first]);bb=o.copy([second])
  if shift:o.translate(bb,0,0,shift)
  out,_=o.intersect(aa,bb);o.synchronize()
  volume=sum(o.getMass(d,t) for d,t in out if d==3)
  if out:o.remove(out,recursive=True);o.synchronize()
  return volume
 static=[{'body_tag':dt[1],'volume_mm3':overlap(bands[0],dt)} for dt in bodies if dt!=bands[0]]
 motion=[{'extension_mm':ext,'tongue_tag':dt[1],'volume_mm3':overlap(bands[0],dt,15-ext)} for ext in range(0,31,5) for dt in tongues]
 row={'size':size,'body_count':len(bodies),'static_checks':static,'slider_checks':motion,'gate_0_01mm3':all(t['volume_mm3']<.01 for t in static+motion)}
 results.append(row);gmsh.finalize();print(size,row['gate_0_01mm3'],flush=True)
out=P/'engineering-v9-local-results'/'clearance.json';out.write_text(json.dumps({'status':'complete','checks':results,'all_pass':len(results)==6 and all(r['gate_0_01mm3'] for r in results),'limitations':['Discrete geometry only; no friction, tolerances or locking retention','Checks changed band against static assembly and sliding tongues; original V8 cup-articulation check not rerun']},indent=2))

