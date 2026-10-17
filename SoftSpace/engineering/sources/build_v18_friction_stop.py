"""V18 passive hinge with a separate wearing stop; local STEP prototype only."""
import sys,json,math,hashlib
from v12_geometry import P,gmsh,import_parts
O=P/'engineering-v18-results';O.mkdir(exist_ok=True);size=sys.argv[1];source=next(r for r in json.loads((P/'engineering-v12-results/cad_report.json').read_text())['sizes'] if r['size']==size);recipe=next(r for r in json.loads((P/'lower-crown-recipes.json').read_text()) if r['name']==size);R=recipe['band_halfspan_mm'];inner=recipe['band_width_mm']/2+(10 if size.startswith('adult') else 2);outer=inner+4;pivot=62. if size.startswith('adult') else 59.;dz=pivot-59
gmsh.initialize();gmsh.option.setNumber('General.Terminal',0);occ=gmsh.model.occ;parts=import_parts(source)
def one(v):
 a=[x for x in v if x[0]==3];assert len(a)==1,a;return a[0]
def fuse(a,b):return one(occ.fuse([a],b)[0])
def cut(a,b):return one(occ.cut([a],b)[0])
for side,prefix in [(-1,'Left'),(1,'Right')]:
 def box(a,b,y1,y2,z1,z2):return (3,occ.addBox(min(side*a,side*b),y1,z1,abs(b-a),y2-y1,z2-z1))
 def cy(y1,y2,r):return (3,occ.addCylinder(side*R,y1,pivot,0,y2-y1,0,r))
 def ring(y1,y2,ro,ri):return cut(cy(y1,y2,ro),[cy(y1-.01,y2+.01,ri)])
 for n in ['Fork','Tongue','ForkPin','ForkPinCap','LockPin','SpringSpace']:
  occ.remove([parts.pop(prefix+n)],recursive=True)
 # Retain the earlier cup pin interface and rebuild the folding hinge above it.
 fork=box(R+17,R+23,-outer,outer,61,69)
 additions=[]
 for sign in [-1,1]:
  y1,y2=sorted([sign*7,sign*13]);arm=box(R+17,R+23,y1,y2,31,65);bore=(3,occ.addCylinder(side*(R+20),y1-1,35,0,y2-y1+2,0,2.1));additions.append(cut(arm,[bore]));a,b=sorted([sign*inner,sign*outer]);prong=fuse(cy(a,b,6),[box(R,R+23,a,b,55+dz,63+dz)]);prong=cut(prong,[cy(a-.1,b+.1,2.15),box(R+6.001,R+13.001,a-.01,b+.01,pivot,80)]);additions.append(prong)
 fork=fuse(fork,additions);parts[prefix+'Fork']=fork
 tongue=fuse(box(R-2,R+2,-8,8,55+dz,134),[cy(-inner+.5,inner-.5,6),box(R+1.5,R+4.5,-5,5,130,134),box(R+4,R+8.2,-inner+.5,inner-.5,pivot,pivot+4),box(R+8,R+12,-outer,outer,pivot,pivot+4)]);tongue=cut(tongue,[cy(-outer-1,outer+1,2.15)]);parts[prefix+'Tongue']=tongue
 if dz:parts['Band']=cut(parts['Band'],[box(R-4.1,R+4.1,-11.1,11.1,81.9,85)])
 parts[prefix+'FrictionWasherRear']=ring(-inner,-inner+.5,5.5,2.15);parts[prefix+'FrictionWasherFront']=ring(inner-.5,inner,5.5,2.15)
 parts[prefix+'BackupWasherRear']=ring(-outer-.5,-outer,6,2.15);parts[prefix+'BackupWasherFront']=ring(outer,outer+.5,6,2.15)
 # Catalogue reference point only. Final assembly is torque-calibrated, so
 # its actual spring height must be measured rather than inferred here.
 base=outer+.5;coords=[(4,base),(2.1,base+.0625),(2.1,base+.3625),(4,base+.3)];pts=[occ.addPoint(side*R+r,y,pivot) for r,y in coords];edges=[occ.addLine(pts[i],pts[(i+1)%4]) for i in range(4)];face=occ.addPlaneSurface([occ.addCurveLoop(edges)]);parts[prefix+'DiscSpring']=one(occ.revolve([(2,face)],side*R,0,pivot,0,1,0,2*math.pi))
 end=outer+.8625;shaft=cy(-outer-.5,end+3.2,2);parts[prefix+'HingeBolt']=fuse(shaft,[cy(-outer-4.5,-outer-.5,3.5)])
 rad=7/math.sqrt(3);points=[occ.addPoint(side*R+rad*math.cos(k*math.pi/3),end,pivot+rad*math.sin(k*math.pi/3)) for k in range(6)];lines=[occ.addLine(points[i],points[(i+1)%6]) for i in range(6)];face=occ.addPlaneSurface([occ.addCurveLoop(lines)]);nut=one(occ.extrude([(2,face)],0,3.2,0));parts[prefix+'HingeNut']=cut(nut,[cy(end-.1,end+3.3,2.05)])
occ.synchronize();assert len(gmsh.model.getEntities(3))==38;target=P/('EarDefender_V18_'+size+'_FrictionStop.step');gmsh.write(str(target));previous=next(r for r in json.loads((P/'engineering-v16-results/selected_candidates.json').read_text())['sizes'] if r['size']==size)
out={'revision':'V18 passive friction hinge and wearing stop','size':size,'file':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source':source['file'],'source_sha256':source['sha256'],'solid_count':38,'parts':{k:list(v) for k,v in parts.items()},'part_bounds_mm':{k:gmsh.model.getBoundingBox(*v) for k,v in parts.items()},'part_volumes_mm3':{k:occ.getMass(*v) for k,v in parts.items()},'pivot_z_mm':pivot,'guide_bottom_mm':85 if dz else 82,'fork_inner_halfspacing_mm':inner,'fork_outer_halfspacing_mm':outer,'fold_angles_deg':previous['fold_angles_deg'],'fold_extension_mm':previous['fold_extension_mm'],'hinge':{'pin_diameter_mm':4,'bore_diameter_mm':4.3,'friction_washer_outer_radius_mm':5.5,'friction_washer_inner_radius_mm':2.15,'wearing_stop_radial_span_mm':[8,12],'wearing_stop_total_contact_area_mm2':32,'disc_spring_reference':'SCHNORR 000600 B','disc_outer_diameter_mm':8,'disc_inner_diameter_mm':4.2,'disc_thickness_mm':.3,'disc_free_height_mm':.55,'disc_loaded_height_mm':.3625,'catalogue_force_at_shortening_N':118,'catalogue_source':'https://www.schnorr-group.com/fileadmin/4_Downloads/Brochures/SCHNORR_Produktbroschuere_EN_2024-02.pdf'},'manufacturing_release':False,'limits':['Local STEP only; no native Fusion reconstruction','Bolt and nut use nominal thread envelopes; actual shoulder length,thread runout,locking and preload assembly need qualification','Disc geometry at catalogue test length is not an actual purchased part or measured preload','Friction coefficients,preload retention,wear,creep,contact and impact remain unvalidated','Stop supports outward rotation at the wearing angle; inward folding remains intentionally possible','No physical comfort,acoustic,durability,cost or child handling pass']};(O/(size+'_cad_report.json')).write_text(json.dumps(out,indent=2));gmsh.finalize();print(json.dumps({'size':size,'solids':38,'file':str(target)}))
