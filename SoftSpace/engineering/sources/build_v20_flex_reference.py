"""Actual STEP body candidates using an aftermarket envelope, not a fitted Sony mount."""
from pathlib import Path
import sys,json,hashlib,math
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'))
import gmsh,numpy as np,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgb
O=P/'engineering-v20-results';C=O/'CAD';C.mkdir(exist_ok=True);I=P/'documents/images'
records=[];cache=[]
def ring(rx,ry,ix,iy,z,h):
 occ=gmsh.model.occ
 # OCC requires the major ellipse radius first. Orient that major axis along Y.
 outer=occ.addDisk(0,0,z,ry,rx,zAxis=[0,0,1],xAxis=[0,1,0]);inner=occ.addDisk(0,0,z,iy,ix,zAxis=[0,0,1],xAxis=[0,1,0])
 face,_=occ.cut([(2,outer)],[(2,inner)])
 return [dt for dt in occ.extrude(face,0,0,h) if dt[0]==3]
for soft,zone_height in [(False,0),(True,18),(True,32)]:
 name='SoftSpace_Flex_V20_'+('uniform_control' if not soft else 'soft_zone' if zone_height==18 else 'broad_soft_zone')
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.add(name);occ=gmsh.model.occ
 whole=ring(40,50,25,35,0,30)
 foam=ring(39.65,49.65,25.35,35.35,.35,29.3)
 cover,_=occ.cut(whole,occ.copy(foam))
 if soft:
  box=(3,occ.addBox(0,15-zone_height/2,0,50,zone_height,30))
  zone,_=occ.intersect(occ.copy(foam),[box])
  main,_=occ.cut(foam,occ.copy(zone));parts=[('MainFoam',main[0]),('SoftGlassesZone',zone[0]),('ContinuousCover',cover[0])]
 else:parts=[('UniformFoam',foam[0]),('ContinuousCover',cover[0])]
 occ.synchronize();volumes={n:occ.getMass(*dt) for n,dt in parts};bounds={n:gmsh.model.getBoundingBox(*dt) for n,dt in parts}
 expected=math.pi*(40*50-25*35)*30
 assert abs(sum(volumes.values())/expected-1)<1e-8
 for n,dt in parts:
  g=gmsh.model.addPhysicalGroup(3,[dt[1]]);gmsh.model.setPhysicalName(3,g,n)
 f=C/(name+'.step');gmsh.write(str(f));gmsh.finalize()
 # Independent import of saved file, positive volume and closure count, not just a successful exporter.
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.model.add('reimport');gmsh.model.occ.importShapes(str(f));gmsh.model.occ.synchronize();solids=gmsh.model.getEntities(3)
 assert len(solids)==len(parts)
 imported=[gmsh.model.occ.getMass(*dt) for dt in solids];assert min(imported)>0 and abs(sum(imported)/expected-1)<1e-8
 gmsh.option.setNumber('Mesh.MeshSizeMax',3);gmsh.option.setNumber('Mesh.MeshSizeMin',.35);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',8);gmsh.model.mesh.generate(2)
 tags,xyz,_=gmsh.model.mesh.getNodes();x=np.array(xyz).reshape(-1,3);lookup={int(t):j for j,t in enumerate(tags)};surfaces=[]
 for dt in solids:
  volume=gmsh.model.occ.getMass(*dt);matched=min(volumes,key=lambda n:abs(volumes[n]-volume))
  col='#dfad70' if matched=='SoftGlassesZone' else '#7eafa1' if matched=='ContinuousCover' else '#617781'
  tri=[]
  for dim,face in gmsh.model.getBoundary([dt],oriented=False):
   if dim==2:
    _,nodes=gmsh.model.mesh.getElementsByType(2,face)
    if len(nodes):tri.extend([[lookup[int(t)] for t in row] for row in np.array(nodes).reshape(-1,3)])
  if tri:surfaces.append((matched,x[np.array(tri)],col))
 cache.append((name,surfaces));gmsh.finalize()
 records.append(dict(name=name,zone_height_mm=zone_height,path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),parts=volumes,part_bounds_mm=bounds,solid_count=len(solids),expected_volume_mm3=expected,reimport_volume_mm3=sum(imported),reimport_pass=True,envelope_source='Brainwavz aftermarket compatibility listing',opening_and_cover='Assumed design variables',Sony_mount_fit_verified=False,scope='Sharp-edge solid idealization for comparison and foam cutting. Corners, real seams, adhesive, stretch skirt and manufacturing process remain supplier development. No cut-through glasses slot.'))

# True surfaces rendered with both a complete-cover view and a cutaway for the soft insert.
az,el=np.deg2rad([-65,25]);D=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)]);H=np.array([-np.sin(az),np.cos(az),0]);V=np.cross(D,H);proj=np.column_stack([H,V])
fig,axs=plt.subplots(1,3,figsize=(12,4.3))
for ax,(name,surf),cut in zip(axs,[cache[0],cache[1],cache[2]],[False,True,True]):
 chosen=[(n,t,c) for n,t,c in surf if not(cut and n=='ContinuousCover')];tri=np.concatenate([t for n,t,c in chosen]);colors=[]
 for n,t,c in chosen:
  normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-20);shade=.5+.5*abs(normal@D);colors.append(np.array(to_rgb(c))[None,:]*shade[:,None])
 order=np.argsort((tri@D).mean(axis=1));ax.add_collection(PolyCollection((tri@proj)[order],facecolors=np.concatenate(colors)[order],edgecolors='none'));p=tri.reshape(-1,3)@proj;lo=p.min(0);hi=p.max(0);ax.set_xlim(lo[0]-8,hi[0]+8);ax.set_ylim(lo[1]-8,hi[1]+8);ax.set_aspect('equal');ax.axis('off')
 ax.set_title(('Broad 32 mm zone cutaway' if 'broad' in name else 'Narrow 18 mm zone cutaway') if cut else 'Uniform control with cover',fontsize=11)
fig.suptitle('SoftSpace Flex V20 reference pad bodies',fontsize=16);fig.text(.5,.045,'80 x 100 x 30 mm aftermarket envelope. Assumed 50 x 70 mm opening. Sony mounting skirt is not dimensioned or fit-verified.',ha='center',fontsize=9);fig.tight_layout(rect=[0,.1,1,.92]);fig.savefig(I/'V20_flex_CAD.png',dpi=180);plt.close(fig)

# 1:1 template for comparing the gross body envelope, never a mounting pattern.
fig,ax=plt.subplots(figsize=(8.27,11.69));from matplotlib.patches import Ellipse
ax.add_patch(Ellipse((0,0),80,100,fill=False,lw=1.3));ax.add_patch(Ellipse((0,0),50,70,fill=False,lw=1.1,ls='--'));ax.plot([-25,25],[-65,-65],color='black',lw=2);ax.text(0,-71,'50 mm print scale check',ha='center');ax.text(0,72,'V20 reference envelope',ha='center',fontsize=17);ax.text(0,62,'Not a Sony mount template',ha='center',fontsize=12);ax.set_xlim(-80,80);ax.set_ylim(-110,110);ax.set_aspect('equal');ax.axis('off');fig.subplots_adjust(left=(8.27-160/25.4)/2/8.27,right=1-(8.27-160/25.4)/2/8.27,bottom=(11.69-220/25.4)/2/11.69,top=1-(11.69-220/25.4)/2/11.69);fig.savefig(O/'Flex_V20_reference_template.pdf');plt.close(fig)
(O/'CAD_verification.json').write_text(json.dumps(dict(revision='V20 reference pad bodies',cases=records,scope='CAD volume and STEP reimport checks only. No fitted mounting interface or calibrated pressure/acoustic model.'),indent=2),encoding='utf-8')
print(json.dumps([dict(name=r['name'],solids=r['solid_count'],pass_reimport=r['reimport_pass']) for r in records]),flush=True)
