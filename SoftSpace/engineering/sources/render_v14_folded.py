"""Actual V14 whole STEP surfaces, same display scale within each row."""
import os,json
os.environ['OPENBLAS_NUM_THREADS']='1'
from v12_geometry import P,gmsh,import_parts
O=P/'engineering-v14-results'
import numpy as np,matplotlib
matplotlib.use('Agg');import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgb
cad=json.loads((O/'cad_report.json').read_text());fig=plt.figure(figsize=(11,8));sources=[]
recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};packing={r['size']:r for r in json.loads((O/'packing_summary.json').read_text())['sizes']}
for ri,size in enumerate(['child_medium','adult_medium']):
 row=next(r for r in cad['sizes'] if r['size']==size);views=[]
 for phase in ['Latched']:
  path=P/('EarDefender_V14_'+size+'_'+phase+'.step');gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(row);occ.synchronize();gmsh.option.setNumber('Mesh.MeshSizeMax',4);gmsh.option.setNumber('Mesh.MeshSizeMin',.5);gmsh.option.setNumber('Mesh.MeshSizeFromCurvature',8);gmsh.model.mesh.generate(2);tags,xyz,_=gmsh.model.mesh.getNodes();x=np.asarray(xyz).reshape(-1,3);lookup={int(v):i for i,v in enumerate(tags)};surfaces=[]
  for names,dt in parts.items():
   if any(n in names for n in ['MainFoam','SoftGlassesZone','Liner','SpringSpace']):continue
   tris=[]
   for dim,face in gmsh.model.getBoundary([dt],oriented=False):
    if dim!=2:continue
    _,c=gmsh.model.mesh.getElementsByType(2,face)
    if len(c):tris.extend(np.asarray([lookup[int(v)] for v in c]).reshape(-1,3).tolist())
   color='#88b7ac' if 'ContinuousCover' in names or 'CrownPad' in names else '#d59440' if 'LockPin' in names else '#526d7b'
   if tris:surfaces.append((names,x[np.asarray(tris)],color))
  nominal=[(tri,color) for name,tri,color in surfaces];points=np.concatenate([tri.reshape(-1,3) for tri,color in nominal]);views.append((points,nominal));folded=[];R=recipes[size]['band_halfspan_mm'];L,T=packing[size]['angles_deg']
  for name,tri,color in surfaces:
   q=tri.copy()
   if name.endswith(('LockPin','PullKnob')):q[:,:,1]-=6
   if name.startswith(('Left','Right')) and not name.endswith('SliderKnob'):
    left=name.startswith('Left');prefix='Left' if left else 'Right';q[:,:,2]+=15 if left else -15
    if name not in [prefix+'Tongue',prefix+'ForkPin',prefix+'ForkPinCap']:
     ctr=np.array([-R if left else R,0,80 if left else 50]);a=np.deg2rad(-L if left else T);C=np.cos(a);S=np.sin(a);rot=np.array([[C,0,S],[0,1,0],[-S,0,C]]);q=(q-ctr)@rot.T+ctr
   folded.append((q,color))
  points=np.concatenate([tri.reshape(-1,3) for tri,color in folded]);views.append((points,folded));gmsh.finalize();sources.append(str(path))
 az=np.deg2rad(-65);el=np.deg2rad(20);D=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)]);H=np.array([-np.sin(az),np.cos(az),0]);V=np.cross(D,H);projection=np.column_stack([H,V]);span=np.max(np.asarray([np.ptp(x@projection,axis=0) for x,_ in views]),axis=0)
 for ci,(x,surfaces) in enumerate(views):
  ax=fig.add_subplot(2,2,ri*2+ci+1);all_tri=[];all_color=[]
  for triangles,color in surfaces:
   n=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1),1e-30)[:,None];shade=.48+.52*np.abs(n@np.array([.35,-.5,.792]));all_tri.append(triangles);all_color.append(np.asarray(to_rgb(color))[None,:]*shade[:,None])
  tri=np.concatenate(all_tri);colors=np.concatenate(all_color);order=np.argsort((tri@D).mean(axis=1));ax.add_collection(PolyCollection((tri@projection)[order],facecolors=colors[order],edgecolors='none',linewidth=0));px=x@projection;ctr=(px.max(axis=0)+px.min(axis=0))/2
  ax.set_xlim(ctr[0]-.55*span[0],ctr[0]+.55*span[0]);ax.set_ylim(ctr[1]-.55*span[1],ctr[1]+.55*span[1]);ax.set_aspect('equal');ax.set_axis_off();ax.set_title(size.replace('_',' ').title()+(' nominal' if ci==0 else ' sampled fold'),fontsize=11)
fig.suptitle('V14 CAD and recorded folding poses',fontsize=15);fig.text(.5,.025,'Same display scale within each row. Nominal STEP surfaces use the recorded rigid fold transforms. Triangles are not fabric texture.',ha='center',fontsize=9);fig.subplots_adjust(0,.06,1,.90,wspace=0,hspace=.10);target=P/'documents'/'images'/'V14_folded_CAD.png';fig.savefig(target,dpi=160,facecolor='white');plt.close(fig);(O/'folded_image_sources.json').write_text(json.dumps({'image':str(target),'sources':sources,'scope':'Actual nominal STEP surfaces tessellated once and moved by the recorded rigid fold transforms; equal scale per size row; no physical product or carrying test'},indent=2));print(target)
