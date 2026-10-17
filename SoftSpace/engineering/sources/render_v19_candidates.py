"""Whole actual V19 surfaces with the audited folded-engaged transforms."""
import os,json,math
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
import numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgb
O=P/'engineering-v19-results'/'final-CAD';selected={'sizes':[json.loads(f.read_text()) for f in O.glob('*_cad_report.json')]};recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};cache=[]
for size in ['child_large','adult_small']:
 row=next(r for r in selected['sizes'] if r['size']==size);R=recipes[size]['band_halfspan_mm'];gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);parts=import_parts(row);gmsh.model.occ.synchronize();gmsh.option.setNumber('Mesh.MeshSizeMax',4);gmsh.option.setNumber('Mesh.MeshSizeMin',.5);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',8);gmsh.model.mesh.generate(2);tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);lookup={int(v):i for i,v in enumerate(tags)};surfaces=[]
 for name,dt in parts.items():
  if any(n in name for n in ['MainFoam','SoftGlassesZone','Liner','SpringSpace']):continue
  tris=[]
  for dim,face in gmsh.model.getBoundary([dt],oriented=False):
   if dim!=2:continue
   _,c=gmsh.model.mesh.getElementsByType(2,face)
   if len(c):tris.extend(np.asarray([lookup[int(v)] for v in c]).reshape(-1,3).tolist())
  color='#88b7ac' if 'ContinuousCover' in name or 'CrownPad' in name else '#d59440' if 'HingeBolt' in name or 'HingeNut' in name else '#b77b52' if 'FrictionWasher' in name else '#526d7b'
  if tris:surfaces.append((name,x[np.asarray(tris)],color))
 gmsh.finalize();cache.append((row,R,surfaces))
az=np.deg2rad(-65);el=np.deg2rad(20);D=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)]);H=np.array([-np.sin(az),np.cos(az),0]);V=np.cross(D,H);projection=np.column_stack([H,V])
def pose(row,R,surfaces,phase):
 result=[]
 for name,tri,color in surfaces:
  q=tri.copy()
  if name.startswith(('Left','Right')) and not name.endswith('SliderKnob') and phase!='wear':
   left=name.startswith('Left');i=0 if left else 1;shift=15 if phase=='retracted' else 15-row['fold_extension_mm'][i]
   if phase=='folded' and name.endswith(('Fork','MainFoam','SoftGlassesZone','ContinuousCover','Carrier','Cup','Liner','CupPin','CupPinCap')):
    angle=(-1 if left else 1)*row['fold_angles_deg'][i];a=math.radians(angle);C=math.cos(a);S=math.sin(a);rot=np.array([[C,0,S],[0,1,0],[-S,0,C]]);ctr=np.array([-R if left else R,0,row['pivot_z_mm']]);q=(q-ctr)@rot.T+ctr
   q[:,:,2]+=shift
  result.append((q,color))
 return result

def draw(ax,surfaces,span=None):
 tri=np.concatenate([t for t,c in surfaces]);x=tri.reshape(-1,3);px=x@projection;box=np.ptp(px,axis=0);span=box if span is None else span;colors=[]
 for triangles,color in surfaces:
  n=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1),1e-30)[:,None];shade=.48+.52*np.abs(n@np.array([.35,-.5,.792]));colors.append(np.asarray(to_rgb(color))[None,:]*shade[:,None])
 order=np.argsort((tri@D).mean(axis=1));ax.add_collection(PolyCollection((tri@projection)[order],facecolors=np.concatenate(colors)[order],edgecolors='none',linewidth=0));ctr=(px.max(axis=0)+px.min(axis=0))/2;ax.set_xlim(ctr[0]-.55*span[0],ctr[0]+.55*span[0]);ax.set_ylim(ctr[1]-.55*span[1],ctr[1]+.55*span[1]);ax.set_aspect('equal');ax.set_axis_off();return box
fig,axes=plt.subplots(1,2,figsize=(11,5))
for ax,(row,R,surfaces) in zip(axes,cache):draw(ax,pose(row,R,surfaces,'wear'));ax.set_title(row['size'].replace('_',' ').title(),fontsize=12)
fig.suptitle('V19 passive hinge and wearing stop',fontsize=16);fig.text(.5,.025,'Saved STEP surfaces. Colours do not select materials. These are digital candidates, not manufactured products.',ha='center',fontsize=9);fig.subplots_adjust(0,.06,1,.83,wspace=0);fig.savefig(P/'documents/images/V19_hero.png',dpi=160,facecolor='white');plt.close(fig)
fig,axes=plt.subplots(2,2,figsize=(11,8))
for i,(row,R,surfaces) in enumerate(cache):
 views=[pose(row,R,surfaces,p) for p in ['retracted','folded']];span=np.max([np.ptp(np.concatenate([t.reshape(-1,3) for t,c in v])@projection,axis=0) for v in views],axis=0)
 for j,v in enumerate(views):draw(axes[i,j],v,span);axes[i,j].set_title(row['size'].replace('_',' ').title()+(' retracted' if j==0 else ' folded'),fontsize=11)
fig.suptitle('V19 sampled folding poses',fontsize=16);fig.text(.5,.025,'Same scale within each row. Actual surfaces moved by the checked transforms; friction torque and holding strength remain unvalidated.',ha='center',fontsize=8);fig.subplots_adjust(0,.06,1,.90,wspace=0,hspace=.10);fig.savefig(P/'documents/images/V19_folded_CAD.png',dpi=160,facecolor='white');plt.close(fig)
(O/'whole_image_sources.json').write_text(json.dumps({'sources':[{'file':r['file'],'sha256':r['sha256']} for r,R,s in cache],'method':'Actual STEP surface tessellation and recorded rigid transforms, folded friction hinge without a release pin'},indent=2));print('V19 hero and folded actual surfaces rendered')
