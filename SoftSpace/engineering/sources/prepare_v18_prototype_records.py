import json,csv
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v18-results';D=O/'prototype-records';D.mkdir(exist_ok=True)
with (D/'CAD_parts_and_envelopes.csv').open('w',newline='') as file:
 w=csv.writer(file);w.writerow(['size','part','volume_mm3','envelope_X_mm','envelope_Y_mm','envelope_Z_mm','material_status','source_sha256'])
 for f in sorted(O.glob('*_cad_report.json')):
  r=json.loads(f.read_text())
  for n,b in r['part_bounds_mm'].items():w.writerow([r['size'],n,r['part_volumes_mm3'][n],*[b[k+3]-b[k] for k in range(3)],'Not selected or qualified',r['sha256']])
with (D/'hinge_design_dimensions.csv').open('w',newline='') as file:
 w=csv.writer(file);w.writerow(['size','pivot_z_mm','guide_bottom_z_mm','inner_fork_halfspacing_mm','outer_fork_halfspacing_mm','pin_diameter_mm','bore_diameter_mm','stop_contact_area_mm2','disc_spring_reference','nominal_hinge_torque_target_Nmm','proposed_min_Nmm','proposed_max_Nmm','status'])
 for f in sorted(O.glob('*_cad_report.json')):
  r=json.loads(f.read_text());h=r['hinge'];w.writerow([r['size'],r['pivot_z_mm'],r['guide_bottom_mm'],r['fork_inner_halfspacing_mm'],r['fork_outer_halfspacing_mm'],h['pin_diameter_mm'],h['bore_diameter_mm'],h['wearing_stop_total_contact_area_mm2'],h['disc_spring_reference'],80,64,96,'Nominal prototype concept dimensions; tolerances process and assembly not released'])
(D/'ASSEMBLY_AND_MEASUREMENT.md').write_text('''# V18 prototype assembly and measurement prerequisites

The STEP files and dimension tables describe a digital candidate. They are not manufacturing drawings or a physical test approval.

1. Select actual structural, friction washer, foam and cover materials. Obtain lot-specific properties and measure uncertain contact properties.
2. Review tolerances, real threads, bolt shoulder and thread runout, nut retention, disc seating and the load path. The CAD thread envelopes do not establish a retained assembly.
3. Assemble a bench hinge with the actual washers and spring. Measure breakaway and running torque directly in both directions over the intended range. The proposed target is80Nmm with a chosen64to96Nmm window, not a comfort criterion.
4. Adjust and remeasure torque, then secure and qualify the fastener retention method. Record actual spring height. Do not infer a nut position from one catalogue force point.
5. Measure torque drift after bedding, dwell, temperature, humidity, cleaning and cycles. Record wear, set, damage and unintended folding. Review intended loads before drop, overload or child handling tests.
6. Measure headband force and pad pressure on known fixtures and heads. Calibrate foam and cover models before claiming worn performance.
7. Measure attenuation and outgoing leakage with repeated seating, glasses variants and matched sound conditions. Use voluntary wearer feedback for texture, fit, heat and sensory acceptance.
8. For Sony WH CH720N, obtain the original mounting dimensions before a compatible carrier is designed. Compare original, uniform replacement and soft-zone pads on the same host, with ANC on and off where relevant.

Blank records contain no measured results. Folding envelopes, component FE fixtures and static torque comparisons do not qualify complete joint strength, fatigue, sound reduction, comfort or final cost.
''')
print('Part envelopes,design dimensions and blank measurement workflow saved')
