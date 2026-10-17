"""Grade-specific analytical screens and a wider untested candidate register."""
from pathlib import Path
import json,math,hashlib,csv
P=Path(__file__).parent;O=P/'engineering-v11-results';O.mkdir(exist_ok=True)
S={
 'ensinger_catalog':'https://www.ensingerplastics.com/-/media/ensinger/files/document-teaser-files/brochures/shapes/food-technology-shapes-en.ashx?rev=-1',
 'abs_natural':'https://www.ensingerplastics.com/en-us/shapes/tecaran-abs-natural',
 'pet':'https://www.ensingerplastics.com/en-sg/shapes/polyester-tecadur-pet-natural',
 'peek':'https://www.ensingerplastics.com/en-gb/shapes/peek-tecapeek-natural',
 'pc':'https://www.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1556888808.pdf',
 'pp':'https://www.lyondellbasell.com/en/polymers/p/Moplen-HP500N/e8c2d3bb-d271-459f-a439-629a5d85a7da',
 'poron':'https://www.rogerscorp.com/-/media/project/rogerscorp/documents/elastomeric-material-solutions/poron/english/data-sheets/17-006-poron-4701-30-very-soft.pdf',
 'silicone':'https://www.rogerscorp.com/-/media/project/rogerscorp/documents/elastomeric-material-solutions/bisco/english/data-sheets/180-048-bf-1000-extra-soft-cellular-silicone.pdf',
 'silicone_soft':'https://www.rogerscorp.com/-/media/project/rogerscorp/documents/elastomeric-material-solutions/bisco/english/data-sheets/180-049-bf-2000-ultra-soft-cellular-silicone.pdf',
 'etpu':'https://download.basf.com/p1/8a8081ec96f843480197313d70cc065f/en/Elastollan%253Csup%253E%25C2%25AE%253Csup%253E_Infinergy%253Csup%253E%25C2%25AE%253Csup%253E_230',
 'film':'https://solutions.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1722849968.pdf?hash=46FCCB0CC8DFDD2759C7E45E3035238D&rev=19d7242a775e451b951d57f500bfa203',
 'spacer':'https://info.baltex.co.uk/coolmax-fresh-fx-spacer'}
S['steel301']='https://www.ulbrich.com/uploads/data-sheets/301-Stainless-Steel-Wire-UNS-S30100-Wire.pdf'
# name, modulus MPa, tensile yield MPa, density g/cm3, source, modulus type.
grades=[('TECARAN ABS grey',1700,32,1.04,'ensinger_catalog','tensile'),('TECAFORM AH natural POM C',2800,67,1.41,'ensinger_catalog','tensile'),('TECAMID 66 natural PA66',3500,84,1.15,'ensinger_catalog','tensile'),('TECARAN ABS natural ASTM',400000*.006894757293168,5800*.006894757293168,1.02,'abs_natural','tensile'),('TECADUR PET natural',3300,91,1.39,'pet','tensile'),('TECAPEEK natural',4200,116,None,'peek','tensile'),('Makrolon 2458 PC',2400,65,None,'pc','tensile'),('Moplen HP500N PP',1480,34,.90,'pp','flexural proxy only')]
grades += [('301 stainless annealed reference',193000,205,7.88,'steel301','tensile; published wire form minimum yield, strip qualification required'),('301 stainless full hard reference',193000,965,7.88,'steel301','tensile; published wire form minimum yield, strip qualification required')]
baseline=P/'engineering-v10-results'/'full_width_sizes_summary.json';base=json.loads(baseline.read_text());rows=[]
for c in base['cases']:
 b=c['meshes'][-1];assert hashlib.sha256(Path(b['source']).read_bytes()).hexdigest()==b['source_sha256']
 for name,E,yield_mpa,rho,source,kind in grades:
  # At fixed nu, K scales with E. Fixed force stress is unchanged; imposed displacement force/stress scale with E.
  ratio=E/2000.;u2N=2*b['compliance_mm_per_N']/ratio;stress2N=b['max_von_mises_centroid_MPa']
  rows.append({'size':c['size'],'grade':name,'modulus_MPa':E,'modulus_basis':kind,'typical_tensile_yield_MPa':yield_mpa,'density_g_cm3':rho,'source_url':S[source],'band_source_sha256':b['source_sha256'],'guide_displacement_at_2N_mm':u2N,'force_at_reference_2000MPa_2N_displacement_N':2*ratio,'centroid_stress_at_that_displacement_MPa':stress2N*ratio,'typical_yield_to_sampled_stress_ratio_fixed_displacement':yield_mpa/(stress2N*ratio),'relative_band_strip_thickness_for_equal_EI':(1/ratio)**(1/3),'analysis':'Exact modulus scaling of the existing linear ideal fixture at fixed nu 0.35; PP uses flexural modulus as a proxy, not a tensile FEA material'})
load_rows=[]
for r in rows:
 for load in [2,5,10,20]:
  # Stress at fixed load is independent of E in this fixed-nu homogeneous model.
  sigma=r['centroid_stress_at_that_displacement_MPa']/(r['modulus_MPa']/2000)*load/2
  load_rows.append({'size':r['size'],'grade':r['grade'],'imposed_side_load_N':load,'guide_displacement_mm':r['guide_displacement_at_2N_mm']*load/2,'sampled_centroid_stress_MPa':sigma,'typical_yield_to_sampled_stress_ratio':r['typical_tensile_yield_MPa']/sigma,'source_url':r['source_url'],'scope':'Linear load scaling, not new nonlinear FEA. 5, 10 and 20 N are illustrative loads, not a product standard. Large displacements or yield invalidate extrapolation.'})
area=math.pi*(52.5*42.5-35*25);foam=[]
for name,stress,strain,rho,source in [('PORON 4701 30 240 kg/m3',21,.25,240,'poron'),('PORON 4701 30 320 kg/m3',35,.25,320,'poron'),('PORON 4701 30 400 kg/m3',62,.25,400,'poron'),('BISCO BF1000',16.5,.25,192,'silicone'),('BISCO BF2000',10,.25,175,'silicone_soft'),('Infinergy 230 at 10 percent',25,.10,230,'etpu'),('Infinergy 230 at 50 percent',250,.50,230,'etpu')]:
 for scale in [1.,.85]:
  A=area*scale**2
  foam.append({'grade':name,'geometry_scale':scale,'reference_compression_strain':None if source.startswith('silicone') else strain,'typical_stress_kPa':stress,'density_kg_m3':rho,'flat_projected_ring_area_mm2':A,'uniform_compression_force_N':stress*A/1000,'source_url':S[source],'limits':'Flat full-area uniform compression proxy at a single datasheet point; not curved-pad contact, real cover, low-load curve, seal or comfort. Silicone test deflection must be confirmed from the referenced ASTM D1056 method; no strain curve inferred. PORON cited sheet thicknesses are much thinner than a 20 mm pad; layering or extrapolation is not validated.'})
families={
 'band and hardware':['ABS','PC ABS blend','polycarbonate','polypropylene','HDPE','PA6 nylon','PA66 nylon','PA12 nylon','POM acetal','PBT','PET','PETG printed prototype','PLA printed prototype','TPU flexible carrier','TPE overmould','PEEK','PEI','glass fibre nylon','carbon fibre nylon','glass fibre epoxy laminate','carbon fibre epoxy laminate','flax fibre composite','bamboo laminate','wood laminate','301 spring stainless strip','spring carbon steel strip','aluminium 6061','aluminium 7075','magnesium alloy','titanium alloy','superelastic NiTi','spring steel core with polymer shell'],
 'cushion and compliant zone':['conventional flexible PU foam','high resilience PU foam','slow recovery memory PU foam','microcellular PU PORON','silicone foam','soft solid silicone gel','encapsulated gel insert','natural latex foam','synthetic latex foam','EVA foam','expanded PE foam','expanded PP foam','expanded TPU beads','printed TPU lattice','silicone lattice','3D spacer textile','cork rubber composite','air bladder','water or hydrogel pouch','phase change insert'],
 'cover and liner':['PU coated polyester','PVC synthetic leather','microfibre synthetic leather','woven polyester','polyester velour','cotton jersey','bamboo viscose knit','wool blend','nylon spandex knit','3D spacer face fabric','silicone skin','breathable monolithic TPU film laminate','ePTFE laminate','thin natural leather','cork fabric','recycled PET knit','removable washable textile sleeve','melamine acoustic liner']}
catalog=[]
for role,names in families.items():
 for name in names:
  catalog.append({'family':name,'role':role,'status':'candidate for grade selection; not numerically or physically validated as a family','required_tests':('bending, yield, creep, moisture, repeated flexure, hinge bearing, impact and manufacturing' if role=='band and hardware' else ('compression curve, recovery, ageing, cover interaction and seal' if role=='cushion and compliant zone' else 'surface preference, stretch, rub noise, friction, seam, vapour transport, cleaning and acoustic seal'))})
out={'status':'completed limited analytical screen and broader candidate register','checked':'2026-10-14','families_count':len(catalog),'families':catalog,'numeric_grades':[dict(zip(['grade','modulus_MPa','typical_yield_MPa','density_g_cm3','source_key','modulus_basis'],r)) for r in grades],'band_case_count':len(rows),'band_cases':rows,'foam_case_count':len(foam),'foam_cases':foam,'sources':S,'baseline_evidence_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),'limits':['This is not each material or formulation in existence. Families without grade-specific data are explicitly untested','Manufacturer typical coupon data are not part allowables, measured headphone data or proof of long-term strength','Same geometry, fixed Poisson ratio, ideal fixture and linear elastic assumptions retained; no large-deformation, creep, fatigue, print anisotropy, impact or hinge transfer','Thickness ratio is an ideal rectangular strip EI proxy, not a redesigned guide or validated complete band','Foam points are not enough to build a constitutive curve. No fitted curve was invented','No cheapest-material, skin suitability, universal sensory preference or novelty/patent claim','Supplier price, Indian stock and delivery not investigated for these materials']}
out['prescribed_load_cases']=load_rows;out['prescribed_load_case_count']=len(load_rows)
out['unit_checks']={'density_conversion_example_g_for_1000mm3_at_1gcm3':1,'linear_reference_E2000_multiplier':2000/2000,'status':'simple conversion and scaling identities checked; not independent solver validation'}
(O/'materials_screen.json').write_text(json.dumps(out,indent=2))
for stem,rr in [('band_grade_screen',rows),('band_load_screen',load_rows),('foam_point_screen',foam),('material_families',catalog)]:
 with (O/(stem+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
print(json.dumps({'families':len(catalog),'band_cases':len(rows),'foam_cases':len(foam),'foam_force_range_N':[min(r['uniform_compression_force_N'] for r in foam),max(r['uniform_compression_force_N'] for r in foam)]},indent=2))
