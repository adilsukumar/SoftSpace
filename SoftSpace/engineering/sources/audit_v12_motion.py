"""Reimported V12 motion checks; spring envelopes reserve space conservatively."""
from pathlib import Path
import json,math,hashlib
from v12_geometry import P,O,gmsh,import_parts,audit_pairs
cad=json.loads((O/'cad_report.json').read_text());assert len(cad['sizes'])==6
fold=json.loads((P/'engineering-v11-results'/'folding_summary.json').read_text());angles={r['size']:r['best_reached_sample_angles_deg'] for r in fold['sizes']}
recipes={r['name']:r for r in json.loads((P/'lower-crown-recipes.json').read_text())};rows=[];exports=[]
if (O/'motion_partial.json').exists() and (O/'motion_exact_spring_version.txt').exists():
 rows=json.loads((O/'motion_partial.json').read_text())
 for old in cad['sizes']:
  if any(r['size']==old['size'] for r in rows):
   assert all(r['source_sha256']==old['sha256'] for r in rows if r['size']==old['size'])
   for phase,suffix in [('released','Released'),('folded','Folded')]:
    f=P/('EarDefender_V12_'+old['size']+'_'+suffix+'.step')
    if f.exists():exports.append({'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'size':old['size'],'phase':phase})
def begin(row):
 gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);gmsh.option.setNumber('General.NumThreads',1);return import_parts(row)
def unlock(parts,stroke):
 occ=gmsh.model.occ
 for prefix in ['Left','Right']:
  occ.translate([parts[prefix+'LockPin']],0,-stroke,0)
  # Rebuild the annular space exactly: anisotropic OCC dilation produced a
  # BSpline mass integration discrepancy in the first released exports.
  b=gmsh.model.getBoundingBox(*parts[prefix+'LockPin']);cx=(b[0]+b[3])/2;cz=(b[2]+b[5])/2
  occ.remove([parts[prefix+'SpringSpace']],recursive=True)
  a=(3,occ.addCylinder(cx,-30,cz,0,15-stroke,0,3.175));b=(3,occ.addCylinder(cx,-31,cz,0,17-stroke,0,2.825))
  out,_=occ.cut([a],[b]);assert len(out)==1;parts[prefix+'SpringSpace']=out[0]
 occ.synchronize()
for row in cad['sizes']:
 if any(r['size']==row['size'] for r in rows):continue
 size=row['size'];R=recipes[size]['band_halfspan_mm'];parts=begin(row);occ=gmsh.model.occ;previous=15
 moving=[parts[k] for k in ['Band','CrownPad','LeftSliderKnob','RightSliderKnob']]
 for ext in range(0,31,5):
  occ.translate(moving,0,0,ext-previous);previous=ext;r=audit_pairs(parts,None if ext==0 else {k:int(dt in moving) for k,dt in parts.items()})
  r.update(size=size,phase='adjustment latched',extension_mm=ext,source_sha256=row['sha256'],guide_tongue_gaps_mm=[occ.getDistance(*parts['Band'],*parts[p+'Tongue'])[0] for p in ['Left','Right']]);rows.append(r)
 gmsh.finalize()
 for stroke in [0,2,4,6]:
  parts=begin(row);unlock(parts,stroke);r=audit_pairs(parts,None if stroke==0 else {k:(i+1 if k.endswith(('LockPin','SpringSpace')) else 0) for i,k in enumerate(parts)});r.update(size=size,phase='release nominal',stroke_mm=stroke,source_sha256=row['sha256']);rows.append(r)
  if stroke==6 and r['pass']:
   target=P/('EarDefender_V12_'+size+'_Released.step');gmsh.write(str(target));exports.append({'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'size':size,'phase':'released'})
  gmsh.finalize()
 parts=begin(row);unlock(parts,6);occ=gmsh.model.occ
 for side,prefix in [(-1,'Left'),(1,'Right')]:occ.translate([dt for k,dt in parts.items() if k.startswith(prefix) and not k.endswith('SliderKnob')],0,0,-side*15)
 occ.synchronize();left=[dt for k,dt in parts.items() if k.startswith('Left') and k not in ['LeftTongue','LeftForkPin','LeftForkPinCap','LeftSliderKnob']];right=[dt for k,dt in parts.items() if k.startswith('Right') and k not in ['RightTongue','RightForkPin','RightForkPinCap','RightSliderKnob']]
 groups={name:(0 if dt in left else (1 if dt in right else 2)) for name,dt in parts.items()};last=[0,0];L,T=angles[size];sequence=[]
 for la,ra in [(a,0) for a in range(0,L+1,5)]+[(L,a) for a in range(5,T+1,5)]:
  occ.rotate(left,-R,0,80,0,1,0,-math.radians(la-last[0]));occ.rotate(right,R,0,50,0,1,0,math.radians(ra-last[1]));last=[la,ra]
  r=audit_pairs(parts,None if la==ra==0 else groups);r.update(size=size,phase='folding released',angles_deg=[la,ra],source_sha256=row['sha256']);rows.append(r);sequence.append(r)
 if all(r['pass'] for r in sequence):
  target=P/('EarDefender_V12_'+size+'_Folded.step');gmsh.write(str(target));exports.append({'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'size':size,'phase':'folded'})
 gmsh.finalize();(O/'motion_partial.json').write_text(json.dumps(rows,indent=2));(O/'motion_exact_spring_version.txt').write_text('Exact cylindrical spring-space reconstruction replaces anisotropic dilation.');print(json.dumps({'size':size,'cases':sum(r['size']==size for r in rows),'failed':sum(not r['pass'] for r in rows if r['size']==size),'fold_exported':all(r['pass'] for r in sequence)}),flush=True)
out={'status':'complete sampled motion audit','case_count':len(rows),'all_pass':all(r['pass'] for r in rows),'cases':rows,'exports':exports,'threshold_mm3':.01,'limits':['Rigid samples, not continuous collision detection or deformed contact','All pairs checked at phase start; subsequent pairs within each unchanged rigid group are invariant; deforming spring envelopes remain separately checked','Spring bodies are conservative annular space envelopes, not actual coils','Six mm stroke and pin engagement are nominal CAD dimensions, not measured forces','Final pivot and slider screws, friction, latch stiffness, manufacturing, fatigue, drops and wearer tests remain open']}
(O/'motion_audit.json').write_text(json.dumps(out,indent=2));print(json.dumps({'cases':len(rows),'all_pass':out['all_pass'],'exports':len(exports)}),flush=True)
