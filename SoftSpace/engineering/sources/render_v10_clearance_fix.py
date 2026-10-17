"""Before/after drawings from actual shortest-setting STEP slices."""
from pathlib import Path
import os,sys,json,hashlib
os.environ['OPENBLAS_NUM_THREADS']='1'
P=Path(__file__).parent;sys.path.insert(0,str(P/'solver-libraries'))
import gmsh,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
v=json.loads((P/'engineering-v9-results'/'native_verification.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())}
fig,axes=plt.subplots(2,2,figsize=(9,7));sources=[]
for row,(size,mode,y,zmin,zmax) in enumerate([('adult_small','pin',9,62,74),('child_small','knob',15,72,90)]):
 for col,version in enumerate(['V9','V10']):
  path=next(Path(f) for f in v['files'] if '_'+size+'_' in Path(f).name and '_Extension_0.step' in f) if version=='V9' else P/('OwnPassiveDefender_V10Local_'+size+'_Extension_0.step')
  R=recipes[size]['band_halfspan_mm'];gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;occ.importShapes(str(path));occ.synchronize();bounds={dt:gmsh.model.getBoundingBox(*dt) for dt in gmsh.model.getEntities(3)}
  if mode=='pin':
   a=next(dt for dt,b in bounds.items() if b[0]<-75 and b[3]>75 and 64.99<b[2]<67.01 and b[4]-b[1]<30)
   b=next(dt for dt,q in bounds.items() if q[0]>0 and abs((q[2]+q[5])/2-65)<.01 and q[4]-q[1]>35 and q[3]-q[0]<5)
   names=['Guide wall','Pivot pin']
  else:
   a=next(dt for dt,q in bounds.items() if q[0]>0 and abs(q[2]-31)<.01 and abs(q[5]-79)<.01)
   b=next(dt for dt,q in bounds.items() if q[0]>0 and abs(q[1]-8)<.01 and abs(q[4]-16)<.01 and abs((q[5]-q[2])-9)<.01)
   names=['Child fork','Thumb knob']
  occ.remove([dt for dt in bounds if dt not in [a,b]],recursive=True);shapes=[]
  for dt in [a,b]:
   cutter=occ.addBox(R-6,y-.1,zmin,12,.2,zmax-zmin);clipped,_=occ.intersect([dt],[(3,cutter)]);shapes.append(clipped[0])
  overlap,_=occ.intersect(occ.copy([shapes[0]]),occ.copy([shapes[1]]));occ.synchronize()
  gmsh.option.setNumber('Mesh.MeshSizeMax',.35);gmsh.option.setNumber('Mesh.MeshSizeMin',.1);gmsh.model.mesh.generate(2)
  tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);mapping={int(t):i for i,t in enumerate(tags)}
  ax=axes[row,col]
  for dt,color,label in [(shapes[0],'#7898a4',names[0]),(shapes[1],'#e4b06b',names[1])]+[(dt,'#b53c35','Intersection') for dt in overlap if dt[0]==3]:
   tris=[]
   for d,face in gmsh.model.getBoundary([dt],oriented=False):
    if d!=2:continue
    kinds,_,arrays=gmsh.model.mesh.getElements(2,face)
    for kind,conn in zip(kinds,arrays):
     if kind==2:tris.extend(np.asarray([mapping[int(i)] for i in conn]).reshape(-1,3).tolist())
   if tris:
    coords=x[np.asarray(tris)][:,:,[0,2]].copy();coords[:,:,0]-=R;ax.add_collection(PolyCollection(coords,facecolors=color,edgecolors='none',label=label))
  ax.set_xlim(-6,6);ax.set_ylim(zmin,zmax);ax.set_aspect('equal');ax.set_title(version+' shortest setting',loc='left');ax.set_xlabel('Across the part (mm)');ax.set_ylabel('Height (mm)');ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False,fontsize=8,loc='upper left')
  ax.text(.03,.03,('Clash in V9' if version=='V9' else ('1.0 mm pin gap' if mode=='pin' else '0.5 mm knob gap')),transform=ax.transAxes,fontsize=9,bbox={'facecolor':'white','edgecolor':'none','alpha':.85})
  gmsh.finalize();sources.append({'version':version,'size':size,'slice_y_mm':y,'slice_thickness_mm':.2,'file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
fig.suptitle('Actual CAD sections show the shortest-setting fixes',fontsize=14,y=.99);fig.tight_layout(rect=(0,.02,1,.96));target=P/'documents'/'images'/'V10_clearance_fix.png';fig.savefig(target,dpi=180,facecolor='white')
(P/'engineering-v10-results'/'section_sources.json').write_text(json.dumps(sources,indent=2));print(target)
