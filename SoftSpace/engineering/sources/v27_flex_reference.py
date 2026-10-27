from pathlib import Path
import sys,json,math,csv,hashlib,ast,os
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'solver-libraries'));os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq
import gmsh
O=P/'engineering-v27-results';O.mkdir(exist_ok=True)
data=json.loads((P/'material-screen-2026-10-26/material_curves.json').read_text());curves={n:PchipInterpolator(r['strain_fraction'],r['compression_stress_kPa'],extrapolate=False) for n,r in data['grades'].items()}
mod=ast.parse((P/'named_material_screen.py').read_text());exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n,ast.FunctionDef) and n.name in ['ellipse_strip','right_ring_strip']],type_ignores=[]),'exact_areas','exec'))
total=math.pi*(40*50-25*35);T=12.7;rows=[]
def solve(A,F,h,soft):
 extra=np.array([0,0,h,h]);grades=['CF-42M',soft,'CF-42M',soft]
 def pressure(d):return np.array([curves[g]((d+e)/T) if a>1e-10 else 0 for a,g,e in zip(A,grades,extra)])
 def load(d):return float(A@pressure(d)/1000)
 lo=.1*T;hi=.8*T-h;low,high=load(lo),load(hi)
 if F<low-1e-10 or F>high+1e-10:return dict(solved=False,domain_min_N=low,domain_max_N=high)
 d=brentq(lambda v:load(v)-F,lo,hi,xtol=1e-12);pr=pressure(d);glass=float((A[2]*pr[2]+A[3]*pr[3])/(A[2]+A[3]))
 return dict(solved=True,closure_mm=d,glass_mean_kPa=glass,glass_max_kPa=float(max(pr[i] for i in [2,3] if A[i]>1e-10)),max_strain=(d+h)/T,force_error_N=abs(load(d)-F))
for zh in [18,32]:
 zone=right_ring_strip(15-zh/2,15+zh/2)
 for cy in range(0,31,5):
  for width in [3,5,7]:
   glo,ghi=cy-width/2,cy+width/2;glass=right_ring_strip(glo,ghi);lo=max(glo,15-zh/2);hi=min(ghi,15+zh/2);inside=right_ring_strip(lo,hi) if hi>lo else 0;outside=glass-inside
   A=np.array([total-zone-outside,zone-inside,outside,inside]);assert min(A)>-1e-9 and abs(A.sum()-total)<1e-8
   for h in [0,.5,1,1.5,2]:
    for F in [8,12,16,24]:
     b=solve(A,F,h,'CF-42M');r=solve(A,F,h,'CF-40M');record=dict(zone_height_mm=zh,arm_centre_y_mm=cy,arm_width_mm=width,arm_protrusion_mm=h,force_per_face_N=F,baseline=b,candidate=r)
     if b['solved'] and r['solved']:record['glass_mean_change_percent']=100*(r['glass_mean_kPa']/b['glass_mean_kPa']-1)
     rows.append(record)
(O/'flex_alignment_cases.json').write_text(json.dumps(rows,indent=2))
paired=[r for r in rows if 'glass_mean_change_percent' in r];summary=dict(date='2026-10-26',cases=len(rows),paired=len(paired),unpaired=len(rows)-len(paired),pressure_increase=sum(r['glass_mean_change_percent']>1e-8 for r in paired),pressure_decrease=sum(r['glass_mean_change_percent']<-1e-8 for r in paired),same=sum(abs(r['glass_mean_change_percent'])<=1e-8 for r in paired),max_force_error_N=max(r['candidate']['force_error_N'] for r in paired),source_material_hash=hashlib.sha256((P/'material-screen-2026-10-26/material_curves.json').read_bytes()).hexdigest(),scope='Typical sourced 12.7mm loading law, uncovered independent columns; broad alignment sensitivity, no acoustic or comfort prediction. Force per face is an assumption, not a wear recommendation.')
summary['zones']={str(zh):dict(paired=sum(r['zone_height_mm']==zh for r in paired),increases=sum(r['zone_height_mm']==zh and r['glass_mean_change_percent']>1e-8 for r in paired),decreases=sum(r['zone_height_mm']==zh and r['glass_mean_change_percent']<-1e-8 for r in paired),min_change_percent=min(r['glass_mean_change_percent'] for r in paired if r['zone_height_mm']==zh),max_change_percent=max(r['glass_mean_change_percent'] for r in paired if r['zone_height_mm']==zh)) for zh in [18,32]}
(O/'flex_alignment_summary.json').write_text(json.dumps(summary,indent=2));print(summary,flush=True)
# Fabrication references deliberately omit the unmeasured Sony mounting skirt.
for zh in [18,32]:
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ
 def ring(a,b,c,d,z,t):
  outer=(2,occ.addDisk(0,0,z,b,a,xAxis=[0,1,0]));inner=(2,occ.addDisk(0,0,z,d,c,xAxis=[0,1,0]));faces,_=occ.cut([outer],[inner]);out=occ.extrude(faces,0,0,t);return [v for v in out if v[0]==3][0]
 foam=ring(40,50,25,35,0,T);box=(3,occ.addBox(0,15-zh/2,-1,50,zh,T+2));zone,_=occ.intersect(occ.copy([foam]),[box]);assert len(zone)==1;main,_=occ.cut([foam],occ.copy(zone));assert len(main)==1
 # Continuous top membrane and walls, open at rear for donor-skirt sewing.
 cover=ring(40.35,50.35,24.65,34.65,0,T+.35);void=ring(40,50,25,35,-.1,T+.1);cover,_=occ.cut([cover],[void]);assert len(cover)==1
 parts={'CF42M_main':main[0],'CF40M_zone':zone[0],'continuous_cover_reference':cover[0]};occ.synchronize();f=O/f'SoftSpace_Flex_V27_zone{zh}.step';gmsh.write(str(f));assert len(gmsh.model.getEntities(3))==3
 r=dict(date='2026-10-26',file=str(f),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),solid_count=3,parts={n:list(v) for n,v in parts.items()},part_bounds_mm={n:list(gmsh.model.getBoundingBox(*v)) for n,v in parts.items()},part_volumes_mm3={n:occ.getMass(*v) for n,v in parts.items()},foam_thickness_mm=T,zone_height_mm=zh,source_material_hash=summary['source_material_hash'],mount='Reuse a fitting donor WH-CH720N pad skirt; preserve its housing attachment. Donor interface is not dimensioned or included in STEP.',scope='Bench foam and cover reference, 80x100 assumed face and 50x70 opening; not a verified Sony replacement. Sewing and trim-to-donor adaptation required. Closed nominal front membrane is not proof of acoustic sealing.')
 assert abs(r['part_volumes_mm3']['CF42M_main']+r['part_volumes_mm3']['CF40M_zone']-total*T)<1e-5
 (O/f'flex_zone{zh}_cad_report.json').write_text(json.dumps(r,indent=2));gmsh.finalize()
print('Flex material-matched CAD references saved',flush=True)
