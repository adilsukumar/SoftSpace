"""Finite compact-pose search on unchanged V19 parts; no continuous CCD claim."""
import sys,json,math,hashlib,time
from audit_v14_motion import P,load,check,moved,rotate,recipes,bounds,mass,common
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs,STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
O=P/'engineering-v21-results';C=O/'compact-CAD';C.mkdir(exist_ok=True);size=sys.argv[1];start=time.time()
row=json.loads((P/'engineering-v19-results/final-CAD'/f'{size}_cad_report.json').read_text());parts,control=load(row);R=recipes[size]['band_halfspan_mm'];pivot=row['pivot_z_mm'];EL,ER=row['fold_extension_mm'];suffix=('Fork','MainFoam','SoftGlassesZone','ContinuousCover','Carrier','Cup','Liner','CupPin','CupPinCap')
def pose(la,ra):
 out={}
 for name,s in parts.items():
  if name.startswith(('Left','Right')) and not name.endswith('SliderKnob'):
   side=-1 if name.startswith('Left') else 1
   if name.endswith(suffix):s=rotate(s,side*R,pivot,-la if side<0 else ra)
   s=moved(s,(0,0,15-(EL if side<0 else ER)))
  out[name]=s
 return out
groups={k:1 if k.startswith('Left') and k.endswith(suffix) else 2 if k.startswith('Right') and k.endswith(suffix) else 0 for k in parts}
def fast(parts):
 bs={k:bounds(s) for k,s in parts.items()};keys=list(parts);queries=0
 for i,k in enumerate(keys):
  for name in keys[i+1:]:
   if groups[k]==groups[name]:continue
   if any(min(bs[k][j+3],bs[name][j+3])-max(bs[k][j],bs[name][j])<1e-5 for j in range(3)):continue
   v=common(parts[k],parts[name]);queries+=1
   if v>.01:return dict(pass_result=False,overlaps=[dict(parts=[k,name],intersection_mm3=v)],boolean_count=queries)
 return dict(pass_result=True,overlaps=[],boolean_count=queries)
def union(bs):return [min(b[k] for b in bs) for k in range(3)]+[max(b[k+3] for b in bs) for k in range(3)]
fixed=union([bounds(s) for k,s in pose(0,0).items() if groups[k]==0]);cache={}
for side in [1,2]:
 for angle in range(0,121,5):cache[side,angle]=union([bounds(s) for k,s in pose(angle if side==1 else 0,angle if side==2 else 0).items() if groups[k]==side])
candidates=[]
for la in range(0,121,5):
 for ra in range(0,121,5):
  b=union([fixed,cache[1,la],cache[2,ra]]);dims=[b[k+3]-b[k] for k in range(3)];candidates.append(dict(angles=[la,ra],box_mm=dims,box_volume_mm3=math.prod(dims)))
candidates.sort(key=lambda r:r['box_volume_mm3']);trials=[];chosen=None;print('ranked 625 endpoint candidates',time.time()-start,flush=True)
assert check(pose(0,0))['pass']
assert fast(pose(0,0))['pass_result'] and not fast(pose(-1,0))['pass_result']
for candidate in candidates:
 la,ra=candidate['angles'];end=fast(pose(la,ra));trial=dict(candidate,endpoint_pass=end['pass_result'],endpoint_overlaps=end['overlaps'],path_pass=False,samples=0)
 if end['pass_result']:
  ok=True
  for a,b in [(v/2,0) for v in range(0,2*la+1,5)]+[(la,v/2) for v in range(5,2*ra+1,5)]:
   r=fast(pose(a,b));trial['samples']+=1
   if not r['pass_result']:ok=False;trial['first_path_failure']=dict(angles=[a,b],overlaps=r['overlaps']);break
  trial['path_pass']=ok
 trials.append(trial)
 if trial['path_pass']:assert check(pose(la,ra),groups)['pass'];chosen=trial;break
 if len(trials)%25==0:print('rejected',len(trials),'ranked candidates',flush=True)
if chosen:
 compound=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(compound)
 for s in pose(*chosen['angles']).values():builder.Add(compound,s)
 f=C/f'SoftSpace_V21_{size}_CompactPose.step';writer=STEPControl_Writer();writer.Transfer(compound,STEPControl_AsIs);status=writer.Write(str(f));reader=STEPControl_Reader();reader.ReadFile(str(f));reader.TransferRoots();e=TopExp_Explorer(reader.OneShape(),TopAbs_SOLID);count=0;vol=0
 while e.More():count+=1;vol+=mass(e.Current());e.Next()
 assert count==42 and abs(vol-sum(mass(s) for s in parts.values()))<.01
 chosen['export']=dict(path=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),solid_count=count,reimport_volume_mm3=vol)
old=json.loads((P/'engineering-v19-results/final-CAD'/f'{size}_motion_audit.json').read_text());result=dict(size=size,source_sha256=row['sha256'],date='2026-10-23',candidate_count=len(candidates),search_range_degrees=[0,120],search_increment_degrees=5,trials=trials,chosen=chosen,original_fold_box_mm=old['folded_box_mm'],nominal_box_mm=old['nominal_box_mm'],extensions_mm=[EL,ER],seconds=time.time()-start,
 scope='Finite 5 degree endpoint search sorted by bounding volume; reject candidates until the first passing left-first 2.5 degree sampled path. Early rejection retains the first actual common-volume failure; accepted poses scan every relevant pair and the endpoint also passes the original full checker. Positive and negative geometry controls passed. Original part geometry unchanged, only assembly locations. No continuous collision certificate, finger access, loaded motion, friction or actual bag fit qualification.')
(O/f'{size}_compact.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='trials'}),flush=True)
