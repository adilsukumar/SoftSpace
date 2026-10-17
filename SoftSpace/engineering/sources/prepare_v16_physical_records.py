"""Blank records and proposed engineering targets, never fabricated test data."""
import json,csv
from pathlib import Path
P=Path(__file__).parent;O=P/'engineering-v16-results';D=O/'physical-test-records';D.mkdir(exist_ok=True)
fields={
 'sony_mount_measurements.csv':['sample_id','headphone_serial_or_label','side','instrument','resolution_mm','outer_height_mm','outer_width_mm','ear_opening_height_mm','ear_opening_width_mm','pad_thickness_front_mm','pad_thickness_rear_mm','mount_lip_dimensions_mm','groove_dimensions_mm','repeat_number','photo_file','notes'],
 'foam_cover_calibration.csv':['sample_id','supplier','grade','lot','test_date','temperature_C','relative_humidity_percent','thickness_mm','area_mm2','load_N','compression_mm','loading_rate_mm_min','hold_seconds','unload_recovery_mm','cover_extension_mm','dry_or_wet','notes'],
 'band_and_joint.csv':['sample_id','revision','size','material_grade','temperature_C','relative_humidity_percent','head_fixture_width_mm','slider_left_mm','slider_right_mm','force_N','release_force_left_N','release_force_right_N','pin_engaged_left','pin_engaged_right','knob_proof_pull_N','cycle_count','damage_or_looseness','notes'],
 'acoustic_comparison.csv':['sample_id','headphone_or_defender','pad','frame_shape','fixture','reseat_number','ANC_state','source_level','measured_internal_level_dB','frequency_Hz','external_level_dB','external_mic_distance_m','room_background_dB','calibration','expanded_uncertainty_dB','notes'],
 'wearer_feedback.csv':['participant_code','consent_record_reference','product','pad','glasses','wear_minutes','pressure_feedback','heat_feedback','texture_feedback','rubbing_sound_feedback','ease_of_removal','stop_reason','participant_requested_change','notes'],
 'durability.csv':['sample_id','revision','material_lot','test_method','drop_height_m','orientation','cycle_count','temperature_C','relative_humidity_percent','pre_force_N','post_force_N','latch_function','cracks_or_sharp_edges','fastener_or_rivet_damage','photos','notes'],
 'supplier_quotes.csv':['item','drawing_revision','material_grade','process','quantity','unit_price_INR','tooling_price_INR','tax_INR','shipping_INR','scrap_allowance','supplier','quote_date','lead_time_days','inspection_scope','notes']}
for name,header in fields.items():
 f=D/name
 if f.exists():continue
 with f.open('w',newline='') as stream:csv.writer(stream).writerow(header)
protocol=[{'test':'Sony fitting','status':'Awaiting user measurements','method':'Record original pad, lip and groove with repeated dimensions and photos before claiming model compatibility.'},
{'test':'Material calibration','status':'Samples required','method':'Compression and recovery across intended low loads, cover stretch, dry/wet friction and conditioned polymer properties; record grade and lot.'},
{'test':'Joint and retention','status':'Samples required','method':'Measure release and return force, engagement, pullout, rivet forming and looseness before and after cycles. Choose loads from a reviewed load specification before proof testing.'},
{'test':'Acoustic comparison','status':'Qualified fixture and samples required','method':'Repeat stock and candidate seats with several frames. Compare incoming noise separately from outgoing playback. Match measured internal playback level and report uncertainty. Target no worsening against stock outside measurement uncertainty; zero leakage is not assumed.'},
{'test':'Durability','status':'Proposed engineering targets only','method':'Draft first screen5000fold/slider cycles,1m drops in6orientations,45C85percentRH24h conditioning. Review fixture and material suitability first. Record damage, latch function and force before/after. Targets are not a standard or demonstrated service life.'},
{'test':'Voluntary wearer feedback','status':'No participants tested','method':'Include autistic users in design feedback, allow immediate removal and record individual heat, pressure, texture, sound and stop reasons. No universal comfortable force or acceptance score is assumed.'},
{'test':'Cost','status':'No supplier quotes','method':'Quote actual grades and processes at prototype100and1000unit quantities, including tooling, assembly, scrap, tax, packaging, inspection and distribution.'}]
(D/'protocol.json').write_text(json.dumps({'status':'Prepared only; no physical tests performed','tests':protocol},indent=2))
cad_rows=json.loads((O/'selected_candidates.json').read_text())['sizes']
with (D/'geometry_quote_BOM.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['variant','part','net_CAD_volume_mm3','material_grade','process','quote_status','interpretation'])
 for r in cad_rows:
  for name,volume in r['part_volumes_mm3'].items():w.writerow([r['variant'],name,volume,'Not selected','Not qualified','No quote','Spring space allocation only; do not price or weigh as solid material' if name.endswith('SpringSpace') else 'Net finished geometry; raw stock tooling machining forming yield and assembly excluded'])
print(json.dumps({'blank_record_templates':len(fields),'protocol_tests':len(protocol),'CAD_BOM_variants':len(cad_rows),'physical_tests_performed':0}))
