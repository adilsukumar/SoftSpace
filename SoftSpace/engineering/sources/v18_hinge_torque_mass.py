import json,math,itertools
from audit_v14_motion import P,load,recipes
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
O=P/'engineering-v18-results';sources=[];mass_cases=[];torque_cases=[];ri=2.15;ro=5.5;rmean=2*(ro**3-ri**3)/(3*(ro**2-ri**2))
densities={'MainFoam':[40,60,100],'SoftGlassesZone':[20,40,80],'ContinuousCover':[900,1100,1300],'Carrier':[900,1200,1500],'Cup':[900,1200,1500],'Liner':[20,40,80],'Fork':[900,1200,1500],'CupPin':[2700,7800,8000],'CupPinCap':[2700,7800,8000]}
for f in sorted(O.glob('*_cad_report.json')):
 row=json.loads(f.read_text());parts,_=load(row);R=recipes[row['size']]['band_halfspan_mm'];pivot=row['pivot_z_mm'];sources.append({'size':row['size'],'file':row['file'],'sha256':row['sha256']})
 for level in range(3):
  mass=0;mx=mz=0
  for name,ds in densities.items():
   g=GProp_GProps();BRepGProp.VolumeProperties_s(parts['Right'+name],g);m=g.Mass()*ds[level]/1e6;c=g.CentreOfMass();mass+=m;mx+=m*(c.X()-R);mz+=m*(c.Z()-pivot)
  lever=math.hypot(mx,mz)/mass;gravity=mass/1000*9.80665*lever;mass_cases.append({'size':row['size'],'density_scenario':['low','middle','high'][level],'assumed_mass_per_moving_side_g':mass,'radial_centre_of_mass_mm':lever,'maximum_gravity_moment_over_orientation_Nmm':gravity})
 for mu,preload_fraction,lever in itertools.product([.05,.1,.15,.2,.3,.4],[.6,.8,1,1.2],[50,65,100]):
  force=118*preload_fraction;torque=2*mu*force*rmean;torque_cases.append({'size':row['size'],'assumed_mu':mu,'preload_fraction_of_catalogue_force':preload_fraction,'assumed_preload_N':force,'grip_lever_mm':lever,'hinge_torque_Nmm':torque,'fold_force_N':torque/lever})
out={'sources':sources,'manufacturer_reference':{'article':'SCHNORR000600B','nominal_force_N':118,'test_shortening_mm':.1875,'test_loaded_height_mm':.3625,'source':'https://www.schnorr-group.com/fileadmin/4_Downloads/Brochures/SCHNORR_Produktbroschuere_EN_2024-02.pdf','scope':'Published reference point for8x4.2x0.3disc. Actual component,force tolerance and installed preload not measured'},'friction_model':'Two uniform-pressure annular friction interfaces; torque=2*mu*F*rmean','effective_radius_mm':rmean,'densities_kg_per_m3':densities,'mass_cases':mass_cases,'torque_cases':torque_cases,'chosen_comparison_window':{'assumed_mu':[.1,.3],'assumed_preload_fraction':[.8,1.2],'minimum_torque_Nmm':2*.1*118*.8*rmean,'maximum_torque_Nmm':2*.3*118*1.2*rmean,'maximum_force_at65mm_N':2*.3*118*1.2*rmean/65},'limits':['Density,coefficient and preload ranges are assumptions,not selected materials or measured properties','Friction changes with wear,humidity,contamination,creep and manufacturing','Gravity holding is a static orientation screen,not shake,bag handling or user safety','Wearing stop is intended to carry outward head reaction;friction still does not lock all directions','No torque comfort threshold or actual spring preload qualification']};(O/'torque_and_mass.json').write_text(json.dumps(out,indent=2));print(json.dumps({'sizes':len(sources),'comparison_window':out['chosen_comparison_window'],'gravity_cases':mass_cases},indent=2))

