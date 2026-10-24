from project_paths import verified_source
"""Independent motion audit without deep geometric copies.
OCC deep-copying this imported fork produces an empty identical-solid common.
Located original shapes and topology-only copies pass that positive control.
"""
import sys,json,math,time,hashlib
from pathlib import Path
P=Path(__file__).parent;sys.path.insert(0,str(P/'cad-validation-libraries'))
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.gp import gp_Trsf,gp_Vec,gp_Ax1,gp_Pnt,gp_Dir,gp_Ax2
from OCP.TopLoc import TopLoc_Location
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
O=P/'engineering-v14-results';cad=json.loads((O/'cad_report.json').read_text());recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};fold={r['size']:r['best_reached_sample_angles_deg'] for r in json.loads((P/'engineering-v11-results'/'folding_summary.json').read_text())['sizes']}
def mass(s):
 p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return abs(p.Mass())
def bounds(s):
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b,False,False);return b.Get()
def moved(s,v):
 t=gp_Trsf();t.SetTranslation(gp_Vec(*v));return s.Moved(TopLoc_Location(t))
def rotate(s,x,z,degrees):
 t=gp_Trsf();t.SetRotation(gp_Ax1(gp_Pnt(x,0,z),gp_Dir(0,1,0)),math.radians(degrees));return s.Moved(TopLoc_Location(t))
def common(a,b):
 op=BRepAlgoAPI_Common(a,b);assert op.IsDone();return mass(op.Shape())
def load(row):
 source=verified_source(row);r=STEPControl_Reader();r.ReadFile(str(source));r.TransferRoots();e=TopExp_Explorer(r.OneShape(),TopAbs_SOLID);solids=[]
 while e.More():solids.append(e.Current());e.Next()
 assert len(solids)==row.get('solid_count',32);used=set();parts={};control=[];cached_bounds=[bounds(s) for s in solids];cached_mass=[mass(s) for s in solids]
 for name,b in row['part_bounds_mm'].items():
  # Saved gmsh boxes can be very loose for BSplines. The optimal OCP box must
  # lie inside that box; volume and unique location identify the solid.
  match=[i for i,s in enumerate(solids) if i not in used and all(cached_bounds[i][k]>=b[k]-.03 and cached_bounds[i][k+3]<=b[k+3]+.03 for k in range(3)) and abs(cached_mass[i]-row['part_volumes_mm3'][name])<.01]
  assert len(match)==1,(name,match);i=match[0];s=solids[i];used.add(i);parts[name]=s;valid=BRepCheck_Analyzer(s).IsValid();v=mass(s);iv=common(s,s) if name.endswith('Fork') else None;control.append({'part':name,'valid':valid,'volume_mm3':v,'self_common_mm3':iv,'positive_common_control_performed':iv is not None,'pass':valid and (iv is None or abs(v-iv)<.01)})
 assert all(c['pass'] for c in control)
 return parts,control
def check(parts,groups=None):
 b={k:bounds(s) for k,s in parts.items()};keys=list(parts);overlaps=[];errors=[];n=0
 for i,a in enumerate(keys):
  for c in keys[i+1:]:
   if groups is not None and groups[a]==groups[c]:continue
   if any(min(b[a][k+3],b[c][k+3])-max(b[a][k],b[c][k])<1e-5 for k in range(3)):continue
   try:
    v=common(parts[a],parts[c]);n+=1
    if v>.01:overlaps.append({'parts':[a,c],'intersection_mm3':v})
   except Exception as e:errors.append({'parts':[a,c],'error':str(e)})
 dims=[max(v[k+3] for v in b.values())-min(v[k] for v in b.values()) for k in range(3)]
 return {'pass':not overlaps and not errors,'overlaps':overlaps,'errors':errors,'boolean_count':n,'bbox_dimensions_mm':dims}
def unlocked(parts,R,stroke):
 q=dict(parts)
 for side,prefix in [(-1,'Left'),(1,'Right')]:
  q[prefix+'LockPin']=moved(parts[prefix+'LockPin'],(0,-stroke,0));q[prefix+'PullKnob']=moved(parts[prefix+'PullKnob'],(0,-stroke,0));axis=gp_Ax2(gp_Pnt(side*(R+10),-30,60),gp_Dir(0,1,0));a=BRepPrimAPI_MakeCylinder(axis,3.175,15-stroke).Shape();axis2=gp_Ax2(gp_Pnt(side*(R+10),-31,60),gp_Dir(0,1,0));b=BRepPrimAPI_MakeCylinder(axis2,2.825,17-stroke).Shape();cut=BRepAlgoAPI_Cut(a,b);assert cut.IsDone();q[prefix+'SpringSpace']=cut.Shape()
 return q
def main():
 rows=[];controls=[]
 checkpoint=O/'ocp_motion_partial.json';identity=O/'ocp_checkpoint_sources.json'
 if checkpoint.exists() and identity.exists():
  assert json.loads(identity.read_text())=={r['size']:r['sha256'] for r in cad['sizes']}
  saved=json.loads(checkpoint.read_text());rows=saved['cases'];controls=saved['controls']
  for size in {r['size'] for r in rows}:
   L,T=fold[size];assert sum(r['size']==size for r in rows)==12+L//5+T//5
 for row in cad['sizes']:
  if len(sys.argv)>1 and row['size'] not in sys.argv[1:]:continue
  if any(r['size']==row['size'] for r in rows):continue
  start=time.time();size=row['size'];R=recipes[size]['band_halfspan_mm'];print('loading '+size,flush=True);parts,control=load(row);controls.append({'size':size,'parts':control});moving=['Band','CrownPad','LeftSliderKnob','RightSliderKnob'];print('loaded '+size,flush=True)
  for ext in range(0,31,5):
   q={k:moved(s,(0,0,ext-15)) if k in moving else s for k,s in parts.items()};r=check(q,None if ext==0 else {k:int(k in moving) for k in parts});r.update(size=size,phase='adjustment latched',extension_mm=ext);rows.append(r)
  for stroke in [0,2,4,6]:
   q=unlocked(parts,R,stroke);r=check(q,{k:i+1 if k.endswith(('LockPin','PullKnob','SpringSpace')) else 0 for i,k in enumerate(parts)});r.update(size=size,phase='release nominal',stroke_mm=stroke);rows.append(r)
  q=unlocked(parts,R,6)
  for k in q:
   if k.startswith(('Left','Right')) and not k.endswith('SliderKnob'):q[k]=moved(q[k],(0,0,15 if k.startswith('Left') else -15))
  left=[k for k in q if k.startswith('Left') and k not in ['LeftTongue','LeftForkPin','LeftForkPinCap','LeftSliderKnob']];right=[k for k in q if k.startswith('Right') and k not in ['RightTongue','RightForkPin','RightForkPinCap','RightSliderKnob']];groups={k:1 if k in left else 2 if k in right else 3 if k in ['LeftTongue','LeftForkPin','LeftForkPinCap'] else 4 if k in ['RightTongue','RightForkPin','RightForkPinCap'] else 0 for k in q};L,T=fold[size]
  for la,ra in [(a,0) for a in range(0,L+1,5)]+[(L,a) for a in range(5,T+1,5)]:
   pose={k:rotate(s,-R,80,-la) if k in left else rotate(s,R,50,ra) if k in right else s for k,s in q.items()};r=check(pose,groups);r.update(size=size,phase='folding released',angles_deg=[la,ra]);rows.append(r)
  identity.write_text(json.dumps({r['size']:r['sha256'] for r in cad['sizes']}));(O/'ocp_motion_partial.json').write_text(json.dumps({'cases':rows,'controls':controls},indent=2));print(json.dumps({'size':size,'cases':sum(r['size']==size for r in rows),'failed':sum(not r['pass'] for r in rows if r['size']==size),'seconds':time.time()-start}),flush=True)
 out={'status':'complete independent OCP motion audit','case_count':len(rows),'all_pass':len(rows)==216 and all(r['pass'] for r in rows),'cases':rows,'positive_controls':controls,'sources':[{'size':r['size'],'file':r['file'],'sha256':r['sha256']} for r in cad['sizes']],'kernel':'OCP 7.8.1.1.post1 with located original shapes; no deep geometric copy','limits':['Rigid discrete samples at5degree and5mm increments, not continuous or deformable motion','Within rigid-group pairs invariant after baseline; spring envelopes checked separately','Actual coils, friction, manufactured tolerances, pinch access and loaded retention remain open']}
 (O/'ocp_motion_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'cases':len(rows),'all_pass':out['all_pass']}),flush=True)

if __name__=='__main__':main()
