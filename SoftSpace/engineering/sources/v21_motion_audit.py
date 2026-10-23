"""Additional finite rigid samples on unchanged final V19 CAD. Not continuous CCD."""
import sys,json,hashlib,time
from pathlib import Path
from audit_v14_motion import P,load,check,moved,rotate,recipes
O=P/'engineering-v21-results';O.mkdir(exist_ok=True)
size=sys.argv[1];start=time.time()
row=json.loads((P/'engineering-v19-results/final-CAD'/f'{size}_cad_report.json').read_text())
parts,controls=load(row);R=recipes[size]['band_halfspan_mm'];pivot=row['pivot_z_mm']
suffix=('Fork','MainFoam','SoftGlassesZone','ContinuousCover','Carrier','Cup','Liner','CupPin','CupPinCap')
def pose(el,er,la,ra):
 out={}
 for name,s in parts.items():
  if name.startswith(('Left','Right')) and not name.endswith('SliderKnob'):
   side=-1 if name.startswith('Left') else 1
   if name.endswith(suffix):s=rotate(s,side*R,pivot,-la if side<0 else ra)
   s=moved(s,(0,0,15-(el if side<0 else er)))
  out[name]=s
 return out
rows=[]
def sample(phase,el,er,la=0,ra=0):
 if phase=='unequal slider':groups={k:1 if k.startswith('Left') and not k.endswith('SliderKnob') else 2 if k.startswith('Right') and not k.endswith('SliderKnob') else 0 for k in parts}
 else:groups={k:1 if k.startswith('Left') and k.endswith(suffix) else 2 if k.startswith('Right') and k.endswith(suffix) else 0 for k in parts}
 r=check(pose(el,er,la,ra),groups);r.update(phase=phase,extensions_mm=[el,er],angles_deg=[la,ra]);rows.append(r)
 print(json.dumps(dict(size=size,phase=phase,angles=[la,ra],extension=[el,er],passed=r['pass'])),flush=True)
 # Keep all failed samples; do not stop at the first collision.
for el in [0,7.5,15,22.5,30]:
 for er in [0,7.5,15,22.5,30]:
  if el!=er:sample('unequal slider',el,er)
L,T=row['fold_angles_deg'];EL,ER=row['fold_extension_mm']
for a in [2.5+5*k for k in range(int(L/5))]:sample('intermediate fold',EL,ER,a,0)
for b in [2.5+5*k for k in range(int(T/5))]:sample('intermediate fold',EL,ER,L,b)
# An alternative handling sequence is a check, not a required valid path.
for f in [.25,.5,.75,1]:sample('simultaneous fold diagnostic',EL,ER,L*f,T*f)
old=json.loads((P/'engineering-v19-results/final-CAD'/f'{size}_motion_audit.json').read_text())
volume=lambda b:b[0]*b[1]*b[2]
ratio=volume(old['folded_box_mm'])/volume(old['nominal_box_mm'])
result=dict(size=size,date='2026-10-23',source_sha256=row['sha256'],positive_controls=controls,cases=rows,
 selected_recommended_path_pass=all(r['pass'] for r in rows if r['phase']!='simultaneous fold diagnostic'),
 diagnostic_failures=sum(not r['pass'] for r in rows if r['phase']=='simultaneous fold diagnostic'),
 folded_to_wear_bounding_volume_ratio=ratio,fold_reduces_bounding_volume=ratio<1,
 seconds=time.time()-start,scope='Original located OCC shapes; same 0.01 mm3 interference gate as V19. Finite midpoint, unequal-slider and diagnostic simultaneous-fold samples only. No continuous collision certificate, deformation, tolerance envelope or finger-access safety qualification.')
(O/f'{size}_motion.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['cases','positive_controls']}),flush=True)
